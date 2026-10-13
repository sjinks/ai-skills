import { constants } from 'node:fs';
import { readdir, lstat, open } from 'node:fs/promises';
import { Readable } from 'node:stream';
import { createInterface } from 'node:readline';
import { homedir } from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const MODES = ['tips', 'cost-tips', 'improve'];
const PROVENANCE_LIMIT = 100;

export async function openLogSnapshot(file) {
  if (!Number.isInteger(constants.O_NOFOLLOW) || constants.O_NOFOLLOW <= 0) throw Object.assign(new Error('No-follow reads unavailable'), { code: 'ENOTSUP' });
  const handle = await open(file, constants.O_RDONLY | constants.O_NOFOLLOW | (constants.O_NONBLOCK || 0));
  try {
    const info = await handle.stat();
    if (!info.isFile()) throw Object.assign(new Error('Not a regular log file'), { code: 'ENOTFILE' });
    if (info.size > 64 * 1024 * 1024) throw Object.assign(new Error('Log exceeds byte limit'), { code: 'EFBIG' });
    const input = info.size ? handle.createReadStream({ encoding: 'utf8', start: 0, end: info.size - 1, autoClose: false }) : Readable.from([]);
    return { handle, input, size: info.size };
  } catch (error) {
    await handle.close();
    throw error;
  }
}
const KEYS = ['input_tokens', 'output_tokens', 'cached_input_tokens', 'reasoning_output_tokens'];
const KNOWN = new Set(['session_meta', 'turn_context', 'response_item', 'event_msg',
  'token_usage_record', 'compacted', 'world_state']);
const integer = value => Number.isSafeInteger(value) && value >= 0;
const validUsage = value => value && integer(value.input_tokens) && integer(value.output_tokens);
const emptyUsage = () => Object.fromEntries(KEYS.map(key => [key, 0]));
function timestampValue(value) {
  if (typeof value !== 'string') return NaN;
  const parts = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-](\d{2}):(\d{2}))$/.exec(value);
  if (!parts) return NaN;
  const [year, month, day, hour, minute, second] = parts.slice(1, 7).map(Number);
  const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1];
  if (!days || day < 1 || day > days || hour > 23 || minute > 59 || second > 59 ||
    Number(parts[7] ?? 0) > 23 || Number(parts[8] ?? 0) > 59) return NaN;
  return Date.parse(value);
}

function validatedSubsets(usage, warnings) {
  const counts = { ...usage };
  for (const [subset, whole] of [['cached_input_tokens', 'input_tokens'], ['reasoning_output_tokens', 'output_tokens']]) {
    if (counts[subset] !== undefined && counts[subset] !== null && (!integer(counts[subset]) || counts[subset] > counts[whole])) {
      counts[subset] = null;
      warnings.push(`Invalid token subset ${subset} omitted`);
    }
  }
  return counts;
}

export function parseArgs(args, now = new Date()) {
  const mode = args[0] && !args[0].startsWith('--') ? args.shift() : 'tips';
  if (!MODES.includes(mode)) throw new Error('Mode must be tips, cost-tips, or improve');
  const options = { mode, home: process.env.CODEX_HOME || path.join(homedir(), '.codex'),
    repo: process.cwd(), days: mode === 'tips' ? 7 : 30, until: now.toISOString(), agents: 'roots' };
  const seen = new Set();
  const values = new Set(['home', 'repo', 'days', 'until', 'agents', 'limit', 'session', 'line']);
  for (let i = 0; i < args.length; i++) {
    const name = args[i].replace(/^--/, '');
    if (!args[i].startsWith('--') || seen.has(name)) throw new Error('Unknown or repeated option');
    seen.add(name);
    if (name === 'all-repos') { options.repo = null; continue; }
    if (!values.has(name) || !args[i + 1] || args[i + 1].startsWith('--')) throw new Error('Unknown option or missing value');
    options[name] = args[++i];
  }
  if (seen.has('repo') && seen.has('all-repos')) throw new Error('--repo and --all-repos conflict');
  if (mode === 'improve' && options.repo === null) throw new Error('improve requires repository scope');
  if (!['roots', 'subagents', 'all'].includes(options.agents)) throw new Error('Invalid --agents');
  options.limit ??= options.session ? 12 : 20;
  for (const [name, maximum] of [['days', 3650], ['limit', options.session ? 50 : 100], ['line', Number.MAX_SAFE_INTEGER]]) {
    if (options[name] === undefined) continue;
    if (!/^\d+$/.test(String(options[name])) || Number(options[name]) < 1 || Number(options[name]) > maximum) throw new Error(`Invalid --${name}`);
    options[name] = Number(options[name]);
  }
  if (options.line && !options.session) throw new Error('--line requires --session');
  options.end = timestampValue(options.until);
  if (!Number.isFinite(options.end)) throw new Error('--until requires a valid ISO calendar timestamp with timezone');
  options.start = options.end - options.days * 86400000;
  options.home = path.resolve(options.home);
  if (options.repo !== null) options.repo = path.resolve(options.repo);
  return options;
}

export function mask(text) {
  return text.replace(/[\u0000-\u0008\u000b-\u001f\u007f-\u009f]/g, '')
    .replace(/-----BEGIN [^-\n]*PRIVATE KEY-----[\s\S]*?(?:-----END [^-\n]*PRIVATE KEY-----|$)/g, '[REDACTED KEY]')
    .replace(/\b(?:sk-[\w-]{12,}|gh[pousr]_[\w]{12,}|github_pat_[\w]{12,}|AKIA[A-Z0-9]{16})\b/g, '[REDACTED]')
    .replace(/((?:api[_-]?key|password|secret|access[_-]?token)\s*[=:]\s*)(?:"[^"\n]*"|'[^'\n]*'|[^\s,;]+)/gi, '$1[REDACTED]')
    .replace(/(Bearer\s+)[\w.\-]+/gi, '$1[REDACTED]');
}

function addUsage(target, usage, warnings) {
  for (const key of KEYS) {
    const value = usage[key];
    if (target[key] === null || !integer(value)) target[key] = null;
    else if (value > Number.MAX_SAFE_INTEGER - target[key]) {
      target[key] = null;
      warnings.push(`Unsafe aggregate for ${key}: count left unknown`);
    } else target[key] += value;
  }
}

async function discover(directory, coverage) {
  const files = [];
  let entries;
  try {
    if ((await lstat(directory)).isSymbolicLink()) { coverage.symlinks_skipped++; return files; }
    entries = await readdir(directory, { withFileTypes: true });
  }
  catch (error) {
    coverage.directory_errors.push({ directory, code: error.code || 'UNKNOWN' });
    return files;
  }
  for (const entry of entries) {
    const file = path.join(directory, entry.name);
    if (entry.isSymbolicLink()) { coverage.symlinks_skipped++; continue; }
    if (entry.isDirectory()) files.push(...await discover(file, coverage));
    else if (entry.isFile() && entry.name.endsWith('.jsonl')) files.push(file);
  }
  return files.sort();
}

function textContent(payload) {
  if (typeof payload.output === 'string') return payload.output;
  const content = Array.isArray(payload.output) ? payload.output : payload.content;
  if (!Array.isArray(content)) return '';
  return content.filter(x => x && ['input_text', 'output_text', 'text'].includes(x.type))
    .map(x => typeof x.text === 'string' ? x.text : '').join('\n');
}

function requestText(text) {
  if (text.startsWith('# AGENTS.md instructions') || /^<(?:environment_context|skill|skills_instructions|external_codex_apps_open_page)[>\s]/.test(text)) return '';
  const marker = '## My request:';
  const index = text.indexOf(marker);
  return index < 0 ? text : text.slice(index + marker.length);
}

async function readSession(file, options, coverage) {
  let snapshot;
  try {
    snapshot = await openLogSnapshot(file);
  }
  catch (error) {
    if (error.code === 'ELOOP') coverage.symlinks_skipped++;
    else if (error.code === 'EFBIG') coverage.large_files_skipped++;
    else coverage.file_errors.push({ file, code: error.code || 'UNKNOWN' });
    return null;
  }
  const { size, input, handle } = snapshot;
  const session = { id: null, file, size, cwd: null, surface: 'unknown', subagent: false,
    first: null, last: null, messages: { user: 0, assistant: 0 }, prompt_characters: 0,
    largest_prompt: 0, largest_prompt_line: null, tool_output_characters: 0,
    largest_tool_output: null, tool_calls: 0, compactions: 0,
    correction_signals: 0, candidate_lines: [], tools: Object.create(null), models: Object.create(null), usage: null,
    usage_source: 'missing', warnings: [], excerpts: [] };
  const records = new Map();
  const fallback = [];
  const responseRoles = new Set();
  const eventMessages = [];
  let model = 'unknown', effort = 'unknown', baseline = null, counterSeen = false, line = 0, started = NaN;
  const inWindow = timestamp => timestamp >= options.start && timestamp <= options.end;
  function message(role, text, timestamp, location) {
    if (!inWindow(timestamp)) return;
    session.messages[role]++;
    if (role === 'user') {
      session.prompt_characters += text.length;
      if (text.length > session.largest_prompt) {
        session.largest_prompt = text.length;
        session.largest_prompt_line = location;
      }
      if (/\b(?:wrong|instead|incorrect|you missed|do not|don't|stop|again|not what)\b/i.test(requestText(text))) {
        session.correction_signals++;
        if (session.candidate_lines.length < 20) session.candidate_lines.push(location);
      }
    }
    excerpt(role, text, timestamp, location);
  }
  function excerpt(role, text, timestamp, location) {
    if (!options.session || session.id !== options.session || !inWindow(timestamp)) return;
    if (options.line && Math.abs(options.line - location) > 3) return;
    const masked = mask(text);
    let end = Math.min(masked.length, 1600);
    if (end < masked.length && masked.charCodeAt(end - 1) >= 0xd800 && masked.charCodeAt(end - 1) <= 0xdbff &&
      masked.charCodeAt(end) >= 0xdc00 && masked.charCodeAt(end) <= 0xdfff) end--;
    session.excerpts.push({ role, line: location, timestamp: new Date(timestamp).toISOString(),
      text: masked.slice(0, end), clipped: end < masked.length });
    session.excerpts.sort((a, b) => a.line - b.line);
    if (session.excerpts.length > options.limit) session.excerpts.shift();
  }
  const reader = createInterface({ input, crlfDelay: Infinity });
  try {
    for await (const raw of reader) {
      line++;
      if (!raw.trim()) continue;
      let row;
      try { row = JSON.parse(raw); }
      catch { coverage.malformed_lines++; continue; }
      if (!row || typeof row !== 'object' || Array.isArray(row)) { coverage.malformed_lines++; continue; }
      if (!KNOWN.has(row.type)) {
        const type = typeof row.type === 'string' ? row.type.slice(0, 80) : 'missing';
        coverage.unknown_event_types[type] = (coverage.unknown_event_types[type] || 0) + 1;
      }
      const p = row.payload;
      if (!p || typeof p !== 'object' || Array.isArray(p)) { coverage.invalid_payloads++; continue; }
      const timestamp = timestampValue(row.timestamp);
      if (row.type === 'session_meta') {
        session.id = typeof p.id === 'string' ? p.id : typeof p.session_id === 'string' ? p.session_id : null;
        session.cwd = typeof p.cwd === 'string' && path.isAbsolute(p.cwd) ? path.resolve(p.cwd) : null;
        session.subagent = p.thread_source === 'subagent' || Boolean(p.source?.subagent);
        session.surface = session.subagent ? 'subagent' : typeof p.source === 'string' ? p.source : 'unknown';
        started = timestampValue(p.timestamp === undefined ? row.timestamp : p.timestamp);
        if (p.timestamp !== undefined && !Number.isFinite(started)) {
          coverage.invalid_timestamps++;
          session.warnings.push('Invalid session start timestamp: zero usage baseline unavailable');
        }
      }
      if (!Number.isFinite(timestamp)) {
        coverage.invalid_timestamps++;
        if (row.type === 'event_msg' && p.type === 'token_count') {
          counterSeen = true;
          baseline = null;
          session.warnings.push('Invalid cumulative usage timestamp omitted; baseline discarded');
        }
        continue;
      }
      if (row.type === 'turn_context') {
        model = typeof p.model === 'string' ? p.model : 'unknown';
        effort = typeof p.effort === 'string' ? p.effort : 'unknown';
      }
      if (inWindow(timestamp)) {
        session.first = session.first === null ? timestamp : Math.min(session.first, timestamp);
        session.last = session.last === null ? timestamp : Math.max(session.last, timestamp);
      }
      if (row.type === 'token_usage_record') {
        if (!validUsage(p.usage) || typeof p.response_id !== 'string' || !p.response_id) {
          session.warnings.push('Invalid per-response usage record omitted');
        } else if (inWindow(timestamp) && !records.has(p.response_id)) records.set(p.response_id, { usage: p.usage, timestamp, model, effort });
      }
      if (row.type === 'event_msg' && p.type === 'token_count') {
        const firstCounter = !counterSeen;
        counterSeen = true;
        if (!validUsage(p.info?.total_token_usage)) {
          session.warnings.push('Invalid cumulative usage snapshot omitted; baseline discarded');
          baseline = null;
          continue;
        }
        const current = validatedSubsets(p.info.total_token_usage, session.warnings);
        let delta = null;
        if (baseline && (current.input_tokens < baseline.input_tokens || current.output_tokens < baseline.output_tokens)) {
          if (inWindow(timestamp)) session.warnings.push('Counter reset: first counter of new segment omitted');
        } else if (baseline) {
          delta = Object.fromEntries(KEYS.map(key => [key,
            integer(current[key]) && integer(baseline[key]) ? current[key] - baseline[key] : null]));
        } else if (firstCounter && started >= options.start && started <= options.end) delta = current;
        else if (inWindow(timestamp)) session.warnings.push('No earlier usage baseline: first cumulative counter omitted');
        baseline = current;
        if (delta && inWindow(timestamp)) fallback.push({ usage: delta, model, effort });
      }
      if (row.type === 'response_item' && p.type === 'message' && ['user', 'assistant'].includes(p.role) && inWindow(timestamp)) {
        const text = textContent(p);
        if (mask(text).trim()) {
          responseRoles.add(p.role);
          message(p.role, text, timestamp, line);
        }
      }
      if (row.type === 'event_msg' && ['user_message', 'agent_message'].includes(p.type) && typeof p.message === 'string' && mask(p.message).trim() && inWindow(timestamp)) {
        eventMessages.push({ role: p.type === 'user_message' ? 'user' : 'assistant', text: p.message, timestamp, line });
      }
      if (row.type === 'response_item' && ['function_call', 'custom_tool_call'].includes(p.type) && inWindow(timestamp)) {
        session.tool_calls++;
        const name = typeof p.name === 'string' ? p.name : 'unknown';
        session.tools[name] = (session.tools[name] || 0) + 1;
      }
      if (row.type === 'response_item' && ['function_call_output', 'custom_tool_call_output'].includes(p.type) && inWindow(timestamp)) {
        const text = textContent(p);
        session.tool_output_characters += text.length;
        if (text.length > (session.largest_tool_output?.characters ?? 0)) {
          session.largest_tool_output = { characters: text.length, line };
        }
        excerpt('tool', text, timestamp, line);
      }
      if (row.type === 'compacted' && inWindow(timestamp)) session.compactions++;
    }
  } catch (error) {
    coverage.file_errors.push({ file, code: error.code || 'UNKNOWN' });
    return null;
  } finally { reader.close(); input.destroy(); await handle.close(); }
  for (const item of eventMessages) if (!responseRoles.has(item.role)) message(item.role, item.text, item.timestamp, item.line);
  session.excerpts.sort((a, b) => a.line - b.line);
  const usageRows = records.size ? [...records.values()] : fallback;
  session.usage_source = records.size ? 'response_records' : fallback.length ? 'cumulative_deltas' : 'missing';
  if (records.size) session.warnings = session.warnings.filter(x => !x.startsWith('Counter reset') && !x.startsWith('No earlier'));
  if (usageRows.length) {
    session.usage = emptyUsage();
    for (const item of usageRows) {
      const counts = validatedSubsets(item.usage, session.warnings);
      addUsage(session.usage, counts, session.warnings);
      const key = JSON.stringify([item.model, item.effort]);
      session.models[key] ??= emptyUsage();
      addUsage(session.models[key], counts, session.warnings);
    }
  }
  session.warnings = [...new Set(session.warnings)];
  session.tools = Object.fromEntries(Object.entries(session.tools).sort((a, b) => b[1] - a[1]).slice(0, 20));
  return session;
}

export async function analyze(options) {
  const coverage = { files_discovered: 0, files_read: 0, matched_sessions: 0,
    duplicate_sessions: 0, metadata_missing: 0, missing_usage_sessions: 0,
    malformed_lines: 0, invalid_payloads: 0, invalid_timestamps: 0,
    symlinks_skipped: 0, large_files_skipped: 0, directory_errors: [], file_errors: [], unknown_event_types: Object.create(null) };
  const files = [...await discover(path.join(options.home, 'sessions'), coverage),
    ...await discover(path.join(options.home, 'archived_sessions'), coverage)].sort();
  coverage.files_discovered = files.length;
  const unique = new Map();
  for (const file of files) {
    const session = await readSession(file, options, coverage);
    if (!session) continue;
    coverage.files_read++;
    if (!session.id) { coverage.metadata_missing++; continue; }
    const previous = unique.get(session.id);
    if (previous) coverage.duplicate_sessions++;
    if (!previous || previous.size < session.size) unique.set(session.id, session);
  }
  const sessions = [...unique.values()].filter(session => {
    if (session.last === null) return false;
    if (options.repo !== null) {
      if (!session.cwd) return false;
      const relative = path.relative(options.repo, session.cwd);
      if (relative === '..' || relative.startsWith('..' + path.sep) || path.isAbsolute(relative)) return false;
    }
    return options.agents === 'all' || (options.agents === 'subagents' ? session.subagent : !session.subagent);
  });
  coverage.matched_sessions = sessions.length;
  coverage.missing_usage_sessions = sessions.filter(x => !x.usage).length;
  const surfaces = Object.create(null);
  let provenanceEntries = 0;
  for (const session of sessions) {
    surfaces[session.surface] ??= { sessions: 0, sessions_with_usage: 0, measured_usage: emptyUsage(), warnings: [], usage_provenance: [] };
    const group = surfaces[session.surface];
    group.sessions++;
    if (session.usage) {
      group.sessions_with_usage++;
      if (provenanceEntries < PROVENANCE_LIMIT) {
        group.usage_provenance.push({ id: session.id, usage_source: session.usage_source });
        provenanceEntries++;
      }
      addUsage(group.measured_usage, session.usage, group.warnings);
    }
  }
  for (const group of Object.values(surfaces)) {
    if (!group.sessions_with_usage) group.measured_usage = null;
    group.usage_provenance_truncated = group.usage_provenance.length < group.sessions_with_usage;
    group.warnings = [...new Set(group.warnings)];
  }
  sessions.sort((a, b) => (options.mode === 'cost-tips'
    ? (b.usage?.input_tokens ?? -1) - (a.usage?.input_tokens ?? -1)
    : b.correction_signals - a.correction_signals) || b.last - a.last || a.id.localeCompare(b.id));
  const selected = options.session ? sessions.filter(x => x.id === options.session) : sessions.slice(0, options.limit);
  return { schema_version: 1, scope: { mode: options.mode, home: options.home, repo: options.repo,
    start: new Date(options.start).toISOString(), until: new Date(options.end).toISOString(), agents: options.agents },
    coverage, surfaces, usage_provenance_limit: PROVENANCE_LIMIT, listed_sessions: selected.length, session_list_truncated: !options.session && sessions.length > selected.length,
    sessions: selected.map(({ size, first, last, excerpts, ...session }) => ({ ...session,
      first: new Date(first).toISOString(), last: new Date(last).toISOString(),
      ...(options.session ? { excerpts } : {}) })) };
}

const HELP = `Usage: node chronicle.mjs [tips|cost-tips|improve] [options]
--home PATH       Codex data directory (CODEX_HOME or ~/.codex)
--repo PATH       Working-directory subtree (default: current directory)
--all-repos       All repositories (not for improve)
--days N          Rolling window: tips 7, otherwise 30 (1–3650)
--until ISO       Inclusive endpoint with timezone (default: now)
--agents VALUE    roots (default), subagents, or all
--limit N         Summary 1–100 (20); excerpts 1–50 (12)
--session ID      Bounded excerpts for one matched session
--line N          Excerpts within three log lines; requires --session
--help            Print this help
Read-only, no network, no billing estimates. Excerpts need human inspection.`;

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    if (process.argv.slice(2).includes('--help')) console.log(HELP);
    else console.log(JSON.stringify(await analyze(parseArgs(process.argv.slice(2))), null, 2));
  } catch (error) {
    // Do not echo argv or log payloads, which may contain sensitive text.
    console.error(`codex-chronicle: ${error.message}`);
    process.exitCode = 1;
  }
}
