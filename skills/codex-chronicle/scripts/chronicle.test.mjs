import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm, symlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { analyze, parseArgs, mask } from './chronicle.mjs';

const at = '2026-10-12T12:00:00Z';
const before = '2026-10-10T00:00:00Z';
const row = (type, payload, timestamp = at) => ({ type, payload, timestamp });
const meta = (id, cwd = '/repo', extra = {}, timestamp = at) => row('session_meta', { id, cwd, source: 'vscode', timestamp, ...extra }, timestamp);
const usage = (input, output, cached = 0, reasoning = 0) => ({ input_tokens: input, output_tokens: output, cached_input_tokens: cached, reasoning_output_tokens: reasoning });
const record = (id, counts, timestamp = at) => row('token_usage_record', { response_id: id, usage: counts }, timestamp);
const counter = (counts, timestamp = at) => row('event_msg', { type: 'token_count', info: { total_token_usage: counts } }, timestamp);
const message = (role, text, timestamp = at) => row('response_item', { type: 'message', role, content: [{ type: role === 'user' ? 'input_text' : 'output_text', text }] }, timestamp);

async function fixture(t) {
  const home = await mkdtemp(path.join(tmpdir(), 'codex-chronicle-test-'));
  t.after(() => rm(home, { recursive: true, force: true }));
  await mkdir(path.join(home, 'sessions'));
  await mkdir(path.join(home, 'archived_sessions'));
  return { home, write: async (name, rows) => {
    const file = path.join(home, name);
    await writeFile(file, rows.map(x => typeof x === 'string' ? x : JSON.stringify(x)).join('\n') + '\n');
    return file;
  }, options: (...args) => parseArgs(['cost-tips', '--home', home, '--repo', '/repo', '--days', '1', '--until', at, ...args]) };
}

test('prefers per-response records, deduplicates, keeps subsets separate and does not mutate logs', async t => {
  const f = await fixture(t);
  const file = await f.write('sessions/a.jsonl', [meta('a'), row('turn_context', { model: 'example', effort: 'low' }),
    record('one', usage(100, 10, 80, 3)), record('one', usage(100, 10, 80, 3)),
    record('two', usage(200, 20, 120, 5)), counter(usage(999, 999))]);
  const original = await readFile(file);
  const result = await analyze(f.options());
  assert.deepEqual(result.sessions[0].usage, usage(300, 30, 200, 8));
  assert.deepEqual(result.sessions[0].models['example/low'], usage(300, 30, 200, 8));
  assert.equal(result.sessions[0].usage_source, 'response_records');
  assert.deepEqual(await readFile(file), original);
});

test('uses an older baseline, inclusive window boundaries and omits future usage', async t => {
  const f = await fixture(t);
  await f.write('sessions/a.jsonl', [meta('a', '/repo', {}, before), counter(usage(100, 10), before),
    counter(usage(150, 15), '2026-10-11T12:00:00Z'), counter(usage(200, 20)),
    counter(usage(900, 90), '2026-10-12T12:00:01Z')]);
  const result = await analyze(f.options());
  assert.deepEqual(result.sessions[0].usage, usage(100, 10));
});

test('unknown baseline and counter reset do not inflate usage', async t => {
  const f = await fixture(t);
  await f.write('sessions/a.jsonl', [meta('a', '/repo', {}, before), counter(usage(500, 50)),
    counter(usage(600, 60)), counter(usage(10, 1)), counter(usage(30, 3))]);
  const session = (await analyze(f.options())).sessions[0];
  assert.deepEqual(session.usage, usage(120, 12));
  assert.equal(session.warnings.length, 2);
});

test('cumulative snapshots and deltas independently validate cached and reasoning subsets', async t => {
  const f = await fixture(t);
  const invalid = usage(100, 10, 200, 20);
  for (const [id, prior, current] of [
    ['bad-baseline', invalid, usage(150, 15, 120, 12)],
    ['bad-current', usage(100, 10, 80, 8), usage(150, 15, 220, 22)],
    ['both-bad', invalid, usage(150, 15, 220, 22)],
    ['bad-delta', usage(100, 10, 0, 0), usage(150, 15, 120, 12)],
    ['negative', usage(100, 10, -1, -1), usage(150, 15, 120, 12)],
    ['fractional', usage(100, 10, 1.5, 1.5), usage(150, 15, 120, 12)],
    ['unsafe', usage(100, 10, Number.MAX_SAFE_INTEGER + 1, Number.MAX_SAFE_INTEGER + 1), usage(150, 15, 120, 12)],
  ]) {
    await f.write('sessions/' + id + '.jsonl', [meta(id, '/repo', {}, before),
      counter(prior, before), counter(current)]);
  }
  for (const s of (await analyze(f.options())).sessions) {
    assert.equal(s.usage_source, 'cumulative_deltas');
    assert.deepEqual(s.usage, { input_tokens: 50, output_tokens: 5,
      cached_input_tokens: null, reasoning_output_tokens: null });
    assert.ok(s.warnings.some(w => w.includes('cached_input_tokens')));
    assert.ok(s.warnings.some(w => w.includes('reasoning_output_tokens')));
  }
  await f.write('sessions/missing.jsonl', [meta('missing', '/repo', {}, before),
    counter({ input_tokens: 100, output_tokens: 10 }, before), counter(usage(150, 15, 120, 12))]);
  const missing = (await analyze(f.options('--session', 'missing'))).sessions[0];
  assert.equal(missing.usage.cached_input_tokens, null);
  assert.equal(missing.usage.reasoning_output_tokens, null);
});

test('invalid required counter totals break the baseline and never become a zero baseline', async t => {
  const f = await fixture(t);
  const badTotals = [null, {}, usage(-1, 1), usage(1, -1), usage(1.5, 1),
    usage(1, 1.5), usage(Number.MAX_SAFE_INTEGER + 1, 1), usage(1, Number.MAX_SAFE_INTEGER + 1)];
  for (const [i, bad] of badTotals.entries()) {
    for (const older of [false, true]) {
      const id = i + '-' + older;
      const rows = [meta(id, '/repo', {}, older ? before : at)];
      if (older) rows.push(counter(usage(100, 10), before));
      rows.push(counter(bad), counter(usage(200, 20)), counter(usage(250, 25)));
      await f.write('sessions/' + id + '.jsonl', rows);
    }
  }
  const result = await analyze(f.options());
  assert.equal(result.coverage.matched_sessions, badTotals.length * 2);
  for (const s of result.sessions) {
    assert.deepEqual(s.usage, usage(50, 5));
    assert.ok(s.warnings.some(w => w.startsWith('Invalid cumulative usage snapshot')));
    assert.ok(s.warnings.some(w => w.startsWith('No earlier usage baseline')));
  }
});

test('decreasing cumulative subsets warn independently while preserving measured whole counts', async t => {
  const f = await fixture(t);
  for (const [id, current, expected, fields] of [
    ['cached', usage(150, 15, 80, 10), usage(50, 5, null, 1), ['cached_input_tokens']],
    ['reasoning', usage(150, 15, 100, 8), usage(50, 5, 10, null), ['reasoning_output_tokens']],
    ['both', usage(150, 15, 80, 8), usage(50, 5, null, null), ['cached_input_tokens', 'reasoning_output_tokens']],
  ]) {
    await f.write('sessions/' + id + '.jsonl', [meta(id, '/repo', {}, before),
      counter(usage(100, 10, 90, 9), before), counter(current)]);
    const s = (await analyze(f.options('--session', id))).sessions[0];
    assert.deepEqual(s.usage, expected);
    assert.deepEqual(s.models['unknown/unknown'], expected);
    assert.equal(s.warnings.length, fields.length);
    for (const field of fields) assert.ok(s.warnings.some(w => w.includes(field)));
  }
});

test('an invalid cumulative timestamp breaks rather than bridges the baseline', async t => {
  const f = await fixture(t);
  for (const [i, timestamp] of ['invalid', 2026, null, false, [], [2026], {}].entries()) {
    await f.write('sessions/' + i + '.jsonl', [meta('counter-' + i, '/repo', {}, before), counter(usage(100, 10), before),
      counter(usage(150, 15), timestamp), counter(usage(200, 20)), counter(usage(250, 25))]);
  }
  const r = await analyze(f.options());
  assert.equal(r.coverage.invalid_timestamps, 7);
  for (const s of r.sessions) {
    assert.deepEqual(s.usage, usage(50, 5));
    assert.ok(s.warnings.some(w => w.startsWith('Invalid cumulative usage timestamp')));
  }
});

test('non-string event and metadata timestamps never enter window accounting or authorize zero baseline', async t => {
  const f = await fixture(t);
  // A numeric year is coercible by Date.parse; the selected window contains its parsed date.
  const endpoint = '2026-01-02T00:00:00Z';
  await f.write('sessions/events.jsonl', [meta('events', '/repo', {}, '2026-01-01T00:00:00Z'),
    record('invalid', usage(900, 90), 2026), message('user', 'invalid', [2026]),
    record('valid', usage(10, 1), '2026-01-01T12:00:00Z')]);
  const options = parseArgs(['cost-tips', '--home', f.home, '--repo', '/repo', '--days', '2', '--until', endpoint]);
  const r = await analyze(options);
  assert.deepEqual(r.sessions[0].usage, usage(10, 1));
  assert.equal(r.sessions[0].messages.user, 0);
  assert.equal(r.coverage.invalid_timestamps, 2);
  for (const [i, timestamp] of [2026, 0, null, false, '', [], [2026], {}].entries()) {
    await f.write('sessions/start-' + i + '.jsonl', [meta('start-' + i, '/repo', { timestamp }, '2026-01-01T00:00:00Z'),
      counter(usage(100, 10), '2026-01-01T12:00:00Z'), counter(usage(150, 15), '2026-01-01T13:00:00Z')]);
  }
  const starts = (await analyze(options)).sessions.filter(s => s.id.startsWith('start-'));
  assert.equal(starts.length, 8);
  for (const s of starts) {
    assert.deepEqual(s.usage, usage(50, 5));
    assert.ok(s.warnings.some(w => w.startsWith('Invalid session start timestamp')));
  }
  const missing = meta('missing-start', '/repo', {}, '2026-01-01T00:00:00Z');
  delete missing.payload.timestamp;
  await f.write('sessions/missing-start.jsonl', [missing, counter(usage(100, 10), '2026-01-01T12:00:00Z')]);
  const fallback = (await analyze({ ...options, session: 'missing-start' })).sessions[0];
  assert.deepEqual(fallback.usage, usage(100, 10));
});

test('missing usage and absent optional subsets remain unknown', async t => {
  const f = await fixture(t);
  await f.write('sessions/a.jsonl', [meta('a'), record('one', { input_tokens: 20, output_tokens: 2 })]);
  await f.write('sessions/b.jsonl', [meta('b'), message('user', 'hello')]);
  const result = await analyze(f.options());
  assert.equal(result.coverage.missing_usage_sessions, 1);
  assert.equal(result.sessions.find(x => x.id === 'b').usage, null);
  assert.deepEqual(result.surfaces.vscode.measured_usage, { input_tokens: 20, output_tokens: 2, cached_input_tokens: null, reasoning_output_tokens: null });
});

test('session and model totals become persistently unknown on overflow in either usage stream', async t => {
  const f = await fixture(t);
  const maximum = Number.MAX_SAFE_INTEGER;
  const large = usage(maximum, maximum, maximum, maximum);
  const small = usage(1, 1, 1, 1);
  await f.write('sessions/records.jsonl', [meta('records'),
    row('turn_context', { model: 'example', effort: 'low' }),
    record('one', large), record('two', small), record('three', small)]);
  await f.write('sessions/counters.jsonl', [meta('counters'),
    row('turn_context', { model: 'example', effort: 'low' }),
    counter(large), counter(usage(0, 0, 0, 0)), counter(small), counter(usage(2, 2, 2, 2))]);
  await f.write('sessions/measured.jsonl', [meta('measured'), record('safe', small)]);
  const result = await analyze(f.options());
  assert.equal(result.sessions[0].id, 'measured');
  for (const id of ['records', 'counters']) {
    const session = result.sessions.find(s => s.id === id);
    const unknown = Object.fromEntries(Object.keys(large).map(k => [k, null]));
    assert.deepEqual(session.usage, unknown);
    assert.deepEqual(session.models['example/low'], unknown);
    for (const key of Object.keys(large)) assert.ok(session.warnings.some(w => w.includes(key)));
  }
});

test('safe-integer boundary stays measured and independently overflowing surface fields warn', async t => {
  const f = await fixture(t);
  const maximum = Number.MAX_SAFE_INTEGER;
  await f.write('sessions/a.jsonl', [meta('a'),
    record('one', usage(maximum - 1, 1, maximum - 1, 0)), record('two', usage(1, 1, 1, 0))]);
  const safe = (await analyze(f.options())).sessions[0];
  assert.deepEqual(safe.usage, usage(maximum, 2, maximum, 0));
  assert.deepEqual(safe.models['unknown/unknown'], safe.usage);
  assert.deepEqual(safe.warnings, []);
  await f.write('sessions/b.jsonl', [meta('b'), record('one', usage(1, 1, 1, 1))]);
  await f.write('sessions/c.jsonl', [meta('c'), record('one', usage(1, 1, 1, 1))]);
  const group = (await analyze(f.options())).surfaces.vscode;
  assert.deepEqual(group.measured_usage, { input_tokens: null, output_tokens: 4,
    cached_input_tokens: null, reasoning_output_tokens: 2 });
  assert.equal(group.warnings.length, 2);
  assert.ok(group.warnings.some(w => w.includes('input_tokens')));
  assert.ok(group.warnings.some(w => w.includes('cached_input_tokens')));
  for (const [i, counts] of [usage(maximum, maximum, maximum, maximum), usage(1, 1, 1, 1), usage(1, 1, 1, 1)].entries()) {
    await f.write('sessions/cli-' + i + '.jsonl', [meta('cli-' + i, '/repo', { source: 'cli' }), record('one', counts)]);
  }
  const cli = (await analyze(f.options())).surfaces.cli;
  assert.deepEqual(cli.measured_usage, { input_tokens: null, output_tokens: null,
    cached_input_tokens: null, reasoning_output_tokens: null });
  assert.equal(cli.warnings.length, 4);
});

test('invalid recorded cwd stays unassigned across repository modes and all-repository scope', async t => {
  const f = await fixture(t);
  const invalid = [undefined, null, false, 0, '', ' ', '.', './nested', 'repo', '../repo'];
  for (const [i, cwd] of invalid.entries()) {
    const metadata = meta('invalid-' + i);
    if (cwd === undefined) delete metadata.payload.cwd;
    else metadata.payload.cwd = cwd;
    await f.write('sessions/invalid-' + i + '.jsonl', [metadata, record('one', usage(1, 1))]);
  }
  await f.write('sessions/valid.jsonl', [meta('valid', '/repo/nested'), record('one', usage(1, 1))]);
  await f.write('sessions/neighbor.jsonl', [meta('neighbor', '/repo-other'), record('one', usage(1, 1))]);
  for (const mode of ['tips', 'cost-tips', 'improve']) {
    const options = parseArgs([mode, '--home', f.home, '--repo', '/repo', '--days', '1', '--until', at]);
    assert.deepEqual((await analyze(options)).sessions.map(s => s.id), ['valid']);
  }
  // Resolving '.' against the analyzer's cwd would falsely include this session.
  const current = parseArgs(['improve', '--home', f.home, '--repo', process.cwd(), '--until', at]);
  assert.equal((await analyze(current)).coverage.matched_sessions, 0);
  const all = await analyze(parseArgs(['tips', '--home', f.home, '--all-repos', '--until', at]));
  assert.equal(all.coverage.matched_sessions, invalid.length + 2);
  assert.ok(all.sessions.filter(s => s.id.startsWith('invalid-')).every(s => s.cwd === null));
});

test('repository boundaries and agent scopes exclude neighbors; aggregates exceed listing limit', async t => {
  const f = await fixture(t);
  await f.write('sessions/a.jsonl', [meta('a'), record('a', usage(20, 2))]);
  await f.write('sessions/b.jsonl', [meta('b', '/repo/nested'), record('b', usage(30, 3))]);
  await f.write('sessions/c.jsonl', [meta('c', '/repo-other'), record('c', usage(900, 90))]);
  await f.write('sessions/d.jsonl', [meta('d', '/repo', { source: { subagent: {} }, thread_source: 'subagent' }), record('d', usage(800, 80))]);
  const result = await analyze(f.options('--limit', '1'));
  assert.equal(result.coverage.matched_sessions, 2);
  assert.equal(result.sessions[0].id, 'b');
  assert.equal(result.session_list_truncated, true);
  assert.equal(result.surfaces.vscode.measured_usage.input_tokens, 50);
  assert.deepEqual(result.surfaces.vscode.usage_provenance, [
    { id: 'a', usage_source: 'response_records' }, { id: 'b', usage_source: 'response_records' }]);
  const all = await analyze(f.options('--agents', 'all'));
  assert.equal(all.surfaces.subagent.measured_usage.input_tokens, 800);
  const rootOptions = f.options();
  rootOptions.repo = path.parse('/repo').root;
  assert.equal((await analyze(rootOptions)).coverage.matched_sessions, 3);
});

test('surface provenance stays complete in truncated summaries and session drill-downs', async t => {
  const f = await fixture(t);
  await f.write('sessions/response.jsonl', [meta('response'), record('one', usage(20, 2))]);
  await f.write('sessions/cumulative.jsonl', [meta('cumulative'), counter(usage(30, 3))]);
  await f.write('sessions/missing.jsonl', [meta('missing'), message('user', 'no usage')]);
  await f.write('sessions/empty.jsonl', [meta('empty', '/repo', { source: 'empty' }), message('user', 'no usage')]);
  await f.write('archived_sessions/copy.jsonl', [meta('response'), record('one', usage(20, 2))]);
  await f.write('sessions/cli.jsonl', [meta('cli', '/repo', { source: 'cli' }), record('one', usage(40, 4))]);
  await f.write('sessions/subagent.jsonl', [meta('subagent', '/repo', { thread_source: 'subagent' }), record('one', usage(50, 5))]);
  await f.write('sessions/other.jsonl', [meta('other', '/repo-other'), record('one', usage(60, 6))]);
  for (const args of [['--limit', '1'], ['--session', 'response', '--limit', '1']]) {
    const r = await analyze(f.options(...args));
    assert.equal(r.listed_sessions, 1);
    const surface = r.surfaces.vscode;
    assert.equal(surface.sessions, 3);
    assert.equal(surface.sessions_with_usage, 2);
    assert.equal(surface.measured_usage.input_tokens, 50);
    assert.deepEqual(surface.usage_provenance.slice().sort((a, b) => a.id.localeCompare(b.id)), [
      { id: 'cumulative', usage_source: 'cumulative_deltas' },
      { id: 'response', usage_source: 'response_records' }]);
    assert.deepEqual(r.surfaces.cli.usage_provenance, [{ id: 'cli', usage_source: 'response_records' }]);
    assert.equal(r.surfaces.empty.measured_usage, null);
    assert.deepEqual(r.surfaces.empty.usage_provenance, []);
    assert.equal(r.coverage.duplicate_sessions, 1);
    if (!args.includes('--session')) assert.equal(r.session_list_truncated, true);
  }
  const missing = (await analyze({ ...f.options(), repo: '/repo', agents: 'roots' })).sessions.find(s => s.id === 'missing');
  assert.equal(missing.usage, null);
  const all = await analyze(f.options('--agents', 'all', '--limit', '1'));
  assert.deepEqual(all.surfaces.subagent.usage_provenance, [{ id: 'subagent', usage_source: 'response_records' }]);
});

test('duplicate active/archive files do not double count, malformed input and unknown types are reported', async t => {
  const f = await fixture(t);
  const rows = [meta('a'), record('one', usage(10, 1))];
  await f.write('sessions/a.jsonl', rows);
  await f.write('archived_sessions/a.jsonl', [...rows, '{broken', row('new_format', {}), row('event_msg', null), 'null']);
  const result = await analyze(f.options());
  assert.equal(result.coverage.duplicate_sessions, 1);
  assert.equal(result.coverage.malformed_lines, 2);
  assert.equal(result.coverage.invalid_payloads, 1);
  assert.equal(result.coverage.unknown_event_types.new_format, 1);
  assert.equal(result.surfaces.vscode.measured_usage.input_tokens, 10);
});

test('messages are not duplicated, summaries omit excerpts, drill-down is bounded and masked', async t => {
  const f = await fixture(t);
  await f.write('sessions/a.jsonl', [meta('a'), message('user', 'wrong password=very-secret-value'),
    row('event_msg', { type: 'user_message', message: 'wrong password=very-secret-value' }),
    message('assistant', 'fixed'), message('user', 'latest')]);
  const summary = (await analyze(f.options())).sessions[0];
  assert.equal(summary.messages.user, 2);
  assert.equal(summary.correction_signals, 1);
  assert.equal('excerpts' in summary, false);
  const detail = (await analyze(f.options('--session', 'a', '--line', '2', '--limit', '2'))).sessions[0];
  assert.equal(detail.excerpts.length, 2);
  const first = (await analyze(f.options('--session', 'a', '--line', '1'))).sessions[0].excerpts;
  assert.equal(first[0].line, 2);
  assert.equal(first[0].text, 'wrong password=[REDACTED]');
  assert.equal(JSON.stringify(first).includes('very-secret-value'), false);
});

test('falls back to event messages and omits reasoning/system/developer payloads', async t => {
  const f = await fixture(t);
  await f.write('sessions/a.jsonl', [meta('a'), row('response_item', { type: 'message', role: 'system', content: [{ type: 'input_text', text: 'private system' }] }),
    row('response_item', { type: 'reasoning', text: 'private reasoning' }), row('event_msg', { type: 'user_message', message: 'hello' })]);
  const result = await analyze(f.options('--session', 'a'));
  assert.equal(result.sessions[0].messages.user, 1);
  assert.deepEqual(result.sessions[0].excerpts.map(x => x.text), ['hello']);
});

test('response messages outside the window do not suppress in-window fallback for either role', async t => {
  const f = await fixture(t);
  await f.write('sessions/a.jsonl', [meta('a', '/repo', {}, before),
    message('user', 'old wrong prompt', before),
    message('assistant', 'future answer', '2026-10-12T12:00:01Z'),
    row('event_msg', { type: 'user_message', message: 'wrong fallback prompt' }),
    row('event_msg', { type: 'agent_message', message: 'fallback answer' })]);
  const s = (await analyze(f.options('--session', 'a'))).sessions[0];
  assert.deepEqual(s.messages, { user: 1, assistant: 1 });
  assert.equal(s.prompt_characters, 'wrong fallback prompt'.length);
  assert.equal(s.correction_signals, 1);
  assert.deepEqual(s.candidate_lines, [4]);
  assert.equal(s.largest_prompt_line, 4);
  assert.deepEqual(s.excerpts.map(e => [e.role, e.line, e.text]), [
    ['user', 4, 'wrong fallback prompt'], ['assistant', 5, 'fallback answer']]);
  const targeted = (await analyze(f.options('--session', 'a', '--line', '4'))).sessions[0];
  assert.deepEqual(targeted.excerpts, s.excerpts);
});

test('in-window response selection is per role and inclusive at both window boundaries', async t => {
  const f = await fixture(t);
  const start = '2026-10-11T12:00:00Z';
  await f.write('sessions/mixed.jsonl', [meta('mixed', '/repo', {}, before),
    message('user', 'response prompt', start),
    row('event_msg', { type: 'user_message', message: 'wrong duplicate' }),
    row('event_msg', { type: 'agent_message', message: 'fallback answer' })]);
  const mixed = (await analyze(f.options('--session', 'mixed'))).sessions[0];
  assert.deepEqual(mixed.messages, { user: 1, assistant: 1 });
  assert.equal(mixed.correction_signals, 0);
  assert.deepEqual(mixed.excerpts.map(e => e.text), ['response prompt', 'fallback answer']);
  await f.write('sessions/end.jsonl', [meta('end', '/repo', {}, before),
    row('event_msg', { type: 'user_message', message: 'fallback prompt' }, start),
    row('event_msg', { type: 'agent_message', message: 'duplicate answer' }),
    message('assistant', 'response answer', at)]);
  const end = (await analyze(f.options('--session', 'end'))).sessions[0];
  assert.deepEqual(end.messages, { user: 1, assistant: 1 });
  assert.deepEqual(end.excerpts.map(e => e.text), ['fallback prompt', 'response answer']);
});

test('structured tool outputs are counted and instruction wrappers do not become correction candidates', async t => {
  const f = await fixture(t);
  await f.write('sessions/a.jsonl', [meta('a'), message('user', '# AGENTS.md instructions\nDo not do wrong things'),
    message('user', '# Context from my IDE setup:\nwrong tab\n## My request:\nPlease implement'),
    message('user', '<skill>\nDo not be wrong\n</skill>'),
    row('response_item', { type: 'custom_tool_call', name: 'exec' }),
    row('response_item', { type: 'custom_tool_call_output', output: [{ type: 'text', text: 'result' }] })]);
  const result = await analyze(f.options('--session', 'a'));
  assert.equal(result.sessions[0].tool_output_characters, 6);
  assert.equal(result.sessions[0].largest_tool_output.characters, 6);
  assert.equal(result.sessions[0].tool_calls, 1);
  assert.equal(result.sessions[0].correction_signals, 0);
  assert.equal(result.sessions[0].excerpts.at(-1).text, 'result');
});

test('missing directories, invalid usage and symlinks are visible without raw payload errors', async t => {
  const f = await fixture(t);
  await f.write('sessions/a.jsonl', [meta('a'), record('one', usage(-2, 1))]);
  await symlink(path.join(f.home, 'sessions/a.jsonl'), path.join(f.home, 'sessions/link.jsonl'));
  await rm(path.join(f.home, 'archived_sessions'), { recursive: true });
  const result = await analyze(f.options());
  assert.equal(result.coverage.symlinks_skipped, 1);
  assert.equal(result.coverage.directory_errors[0].code, 'ENOENT');
  assert.equal(result.sessions[0].usage, null);
  assert.equal(result.sessions[0].warnings.length, 1);
});

test('CLI rejects invalid scope and values, uses mode defaults, and returns nonzero on errors', () => {
  for (const args of [['improve', '--all-repos'], ['tips', '--days', '0'], ['tips', '--days', '1.5'],
    ['tips', '--repo', '/repo', '--all-repos'], ['tips', '--until', '2026-10-12'], ['tips', '--line', '2'],
    ['tips', '--agents', 'bad'], ['tips', '--limit', '101'], ['tips', '--days'], ['tips', '--typo', 'x']]) {
    assert.throws(() => parseArgs(args));
  }
  assert.equal(parseArgs([], new Date(at)).days, 7);
  assert.equal(parseArgs(['improve'], new Date(at)).days, 30);
  const script = fileURLToPath(new URL('./chronicle.mjs', import.meta.url));
  const result = spawnSync(process.execPath, [script, 'improve', '--all-repos'], { encoding: 'utf8' });
  assert.equal(result.status, 1);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /requires repository scope/);
});

test('oversized token subsets become unknown and arbitrary metadata keys remain data', async t => {
  const f = await fixture(t);
  await f.write('sessions/a.jsonl', [meta('a', '/repo', { source: 'constructor' }),
    record('a', usage(10, 2, 20, 3)), row('__proto__', {}),
    row('response_item', { type: 'custom_tool_call', name: '__proto__' })]);
  const result = await analyze(f.options());
  assert.equal(result.sessions[0].usage.cached_input_tokens, null);
  assert.equal(result.sessions[0].usage.reasoning_output_tokens, null);
  assert.equal(result.surfaces.constructor.sessions, 1);
  assert.equal(result.coverage.unknown_event_types.__proto__, 1);
  assert.equal(result.sessions[0].tools.__proto__, 1);
  assert.match(result.sessions[0].warnings[0], /Invalid token subset/);
});

test('source-directory symlinks are skipped rather than followed', async t => {
  const f = await fixture(t);
  await rm(path.join(f.home, 'archived_sessions'), { recursive: true });
  await symlink(path.join(f.home, 'sessions'), path.join(f.home, 'archived_sessions'));
  await f.write('sessions/a.jsonl', [meta('a')]);
  const result = await analyze(f.options());
  assert.equal(result.coverage.files_discovered, 1);
  assert.equal(result.coverage.symlinks_skipped, 1);
});

test('masking happens before clipping and removes common credentials and control sequences', () => {
  assert.equal(mask('Bearer abc.def\u001b password="secret words"'), 'Bearer [REDACTED] password=[REDACTED]');
  assert.equal(mask('-----BEGIN PRIVATE KEY-----\nprivate\n-----END PRIVATE KEY-----'), '[REDACTED KEY]');
});

test('excerpt clipping status uses masked length for expansion, contraction and exact boundaries', async t => {
  const f = await fixture(t);
  const cases = [
    ['expansion', 'x'.repeat(1586) + ' password=x', true],
    ['key', '-----BEGIN PRIVATE KEY-----\n' + 'x'.repeat(1700) + '\n-----END PRIVATE KEY-----', false],
    ['controls', '\u001b'.repeat(1700) + 'safe', false],
    ['exact', 'x'.repeat(1600), false],
    ['over', 'x'.repeat(1601), true],
  ];
  for (const [id, raw, clipped] of cases) {
    await f.write('sessions/' + id + '.jsonl', [meta(id), message('user', raw)]);
    const e = (await analyze(f.options('--session', id))).sessions[0].excerpts[0];
    assert.equal(e.text, mask(raw).slice(0, 1600));
    assert.equal(e.clipped, clipped);
    assert.ok(e.text.length <= 1600);
  }
});
