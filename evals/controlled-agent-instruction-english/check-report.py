#!/usr/bin/env python3
"""Validate CAIE report envelopes and suite projections without model calls."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

MARKERS = ('CAIE mode:', 'CAIE artifact:', 'CAIE findings:', 'CAIE status:')
NAME = 'controlled-agent-instruction-english'
RULES = {f'{prefix}{number}' for prefix, count in
         [('T', 8), ('N', 7), ('S', 6), ('R', 5), ('C', 8), ('P', 8), ('D', 6), ('E', 8)] for number in range(1, count + 1)}
PROFILES = ('author', 'author-findings', 'audit-clean', 'audit-findings', 'blocked')
TASK_PROFILES = {'positive-trigger-1': 'author', 'positive-edge-1': 'audit-findings',
                 'positive-edge-2': 'audit-clean', 'positive-edge-3': 'blocked',
                 'positive-edge-4': 'author-findings', 'positive-edge-5': 'blocked'}
VALID = {
    'author': 'CAIE mode: author\nCAIE artifact:\n```text\nRead config.json.\n```\nCAIE findings: None.\nCAIE status: Authored',
    'author-findings': 'CAIE mode: author\nCAIE artifact:\n```text\nRun the tests.\n```\nCAIE findings:\n- error | N4 | supplied snippet:1 | "should" makes testing optional | Run the tests.\nCAIE status: Authored',
    'audit-clean': 'CAIE mode: audit\nCAIE artifact: None.\nCAIE findings: None.\nCAIE status: Clean',
    'audit-findings': 'CAIE mode: audit\nCAIE artifact: None.\nCAIE findings:\n- error | N4 | supplied snippet:1 | "should" leaves required testing optional | Run the tests.\nCAIE status: Findings',
    'blocked': 'CAIE mode: blocked\nCAIE artifact: None.\nCAIE findings: None.\nCAIE status: Blocked; Missing: instruction text',
}


def validate_findings(lines: list[str]) -> None:
    """Validate shared finding fields for audit and combined author reports.

    At least one finding is required when this branch is selected.
    """
    if not lines:
        raise ValueError('finding branch requires at least one bullet')
    for line in lines:
        fields = line.split(' | ')
        if len(fields) != 5 or fields[0] not in ('- error', '- warning') or fields[1] not in RULES:
            raise ValueError('invalid finding severity, rule or cardinality')
        if not re.fullmatch(r'(?:supplied snippet:[1-9][0-9]*|[^#|]+#[^#|]+)', fields[2]):
            raise ValueError('invalid finding location')
        if '#' in fields[2] and any(not part.strip() for part in fields[2].split('#')):
            raise ValueError('invalid finding location')
        if fields[4].startswith('Clarify:') and not re.fullmatch(r'Clarify: \S.*\?', fields[4]):
            raise ValueError('invalid clarification correction')
        if any(not field.strip() or '|' in field for field in fields[2:]):
            raise ValueError('finding fields must be nonempty and contain no pipe')


def validate(text: str, profile: str) -> None:
    """Check exactly one envelope while preserving fenced artifact literals.

    The selected profile constrains the mode, findings branch, and verdict.
    """
    if profile not in PROFILES:
        raise ValueError('invalid profile')
    lines = text.replace('\r\n', '\n').replace('\r', '\n').removesuffix('\n').split('\n')
    mode = 'audit' if profile.startswith('audit-') else 'author' if profile.startswith('author') else profile
    if not lines or lines[0] != f'CAIE mode: {mode}':
        raise ValueError('invalid mode or first marker')
    if profile.startswith('author'):
        if len(lines) < 7 or lines[1] != MARKERS[1] or not re.fullmatch(r'`{3,}[A-Za-z0-9_+-]*', lines[2]):
            raise ValueError('artifact must be one nonempty fenced block')
        fence = re.match(r'`+', lines[2]).group()
        close = next((i for i in range(3, len(lines)) if lines[i] == fence), None)
        if close is None or not any(line.strip() for line in lines[3:close]):
            raise ValueError('artifact must be one nonempty fenced block')
        if any(re.fullmatch(r'`+', line.strip()) and len(line.strip()) >= len(fence) for line in lines[3:close]):
            raise ValueError('artifact fence must exceed every payload fence')
        # Report-like payload lines are not envelope fields.
        tail = lines[close + 1:]
        if profile == 'author':
            if tail != [MARKERS[2] + ' None.', MARKERS[3] + ' Authored']:
                raise ValueError('invalid author envelope or termination')
        else:
            if len(tail) < 3 or tail[0] != MARKERS[2] or tail[-1] != MARKERS[3] + ' Authored':
                raise ValueError('combined author requires findings and Authored status')
            validate_findings(tail[1:-1])
        return
    if len(lines) < 4 or lines[1] != MARKERS[1] + ' None.':
        raise ValueError('artifact must be None outside author mode')
    if profile == 'audit-findings':
        if lines[2] != MARKERS[2] or lines[-1] != MARKERS[3] + ' Findings' or len(lines) < 5:
            raise ValueError('findings branch requires bullets and Findings status')
        validate_findings(lines[3:-1])
        return
    if len(lines) != 4 or lines[2] != MARKERS[2] + ' None.':
        raise ValueError('invalid marker order, cardinality or termination')
    if profile == 'audit-clean' and lines[3] != MARKERS[3] + ' Clean':
        raise ValueError('clean audit requires Clean status')
    if profile == 'blocked' and not re.fullmatch(r'CAIE status: Blocked; Missing: \S.*', lines[3]):
        raise ValueError('blocked status requires missing input')


def self_test() -> None:
    """Exercise all profiles and isolated envelope and field mutations.

    Marker payloads, CRLF, long fences, and multiple findings are valid inputs.
    """
    count = 0
    for profile, report in VALID.items():
        validate(report, profile)
        validate(report.replace('\n', '\r\n') + '\n', profile)
        lines = report.splitlines()
        mutations = ['prefix\n' + report, report + '\nTrailing prose.', report + '\n\n']
        for marker in MARKERS:
            mutations.extend([report.replace(marker, 'Omitted:', 1), report + '\n' + marker])
        mutations.append('\n'.join([lines[1], lines[0]] + lines[2:]))
        mutations.append(report.replace('CAIE status:', 'CAIE status: invalid', 1))
        for mutation in mutations:
            try:
                validate(mutation, profile)
            except ValueError:
                count += 1
            else:
                raise AssertionError((profile, 'accepted mutation', mutation))
        for other in PROFILES:
            if other == profile:
                continue
            try:
                validate(report, other)
            except ValueError:
                count += 1
            else:
                raise AssertionError((profile, 'accepted crossover', other))
    literal = VALID['author'].replace('Read config.json.', '\n'.join(MARKERS) + '\n```\ncode')
    literal = literal.replace('```text', '````text').rsplit('\n```\n', 1)
    validate('\n````\n'.join(literal), 'author')
    for profile in ('author', 'author-findings'):
        mutation = VALID[profile].replace('```text', '````text').replace('\n```\n', '\n````\n').replace('CAIE artifact:\n````text\n', 'CAIE artifact:\n````text\n`````\n')
        try:
            validate(mutation, profile)
        except ValueError:
            count += 1
        else:
            raise AssertionError('accepted longer payload fence')
    for inner in (' ```', '``` ', '  ````  '):
        mutation = VALID['author'].replace('Read config.json.', inner + '\nRead config.json.')
        try:
            validate(mutation, 'author')
        except ValueError:
            count += 1
        else:
            raise AssertionError('accepted whitespace payload fence')
    report = VALID['audit-findings']
    bullet = report.splitlines()[3]
    validate(report.replace('supplied snippet:1', 'instructions.md#Testing'), 'audit-findings')
    warning = 'CAIE mode: audit\nCAIE artifact: None.\nCAIE findings:\n- warning | R1 | supplied snippet:3 | it may refer to the log or report | Clarify: Which artifact must be archived?\nCAIE status: Findings'
    validate(warning, 'audit-findings')
    for correction in ('Clarify:', 'Clarify: ?', 'Clarify: Which artifact must be archived'):
        mutation = warning.replace('Clarify: Which artifact must be archived?', correction)
        try:
            validate(mutation, 'audit-findings')
        except ValueError as error:
            assert str(error) == 'invalid clarification correction'
            count += 1
        else:
            raise AssertionError('accepted invalid clarification correction')
    for location in (' #Testing', 'instructions.md# ', ' # '):
        try:
            validate(report.replace('supplied snippet:1', location), 'audit-findings')
        except ValueError as error:
            assert str(error) == 'invalid finding location'
            count += 1
        else:
            raise AssertionError('accepted whitespace location component')
    validate(report.replace(bullet, bullet + '\n' + bullet.replace('N4', 'C8')), 'audit-findings')
    for mutation in (report.replace('- error', '- info'), report.replace('N4', 'N8'),
                     report.replace('supplied snippet:1', ''), report.replace('Run the tests.', ''),
                     report.replace('Run the tests.', 'bad | extra'), VALID['blocked'].replace('instruction text', ''),
                     VALID['author'].replace('Read config.json.', ''), VALID['audit-clean'].replace('Clean', 'Findings')):
        profile = next(p for p in PROFILES if mutation.startswith('CAIE mode: ' + ('audit' if p.startswith('audit-') else 'author' if p.startswith('author') else p))
                       and (p != 'audit-clean' or 'CAIE findings: None.' in mutation))
        try:
            validate(mutation, profile)
        except ValueError:
            count += 1
        else:
            raise AssertionError(('accepted field mutation', mutation))
    print(f'report profiles and {count} deterministic rejection mutations: passed')


def projections(root: Path | None = None) -> None:
    """Compare decoded task markers and negatives against the owned grammar.

    Also bind each positive program grader to its expected profile and metric.
    """
    import yaml
    root = root or Path(__file__).resolve().parent
    repo = root.parent.parent
    skill = (repo / 'skills' / NAME / 'SKILL.md').read_text()
    for marker in MARKERS:
        if f'`{marker}`' not in skill:
            raise ValueError('source marker missing: ' + marker)
    catalog = (repo / 'skills' / NAME / 'references/language-rules.md').read_text()
    if set(re.findall(r'^#### ([TNSRCPDE][0-9]+)\.', catalog, re.MULTILINE)) != RULES:
        raise ValueError('source rule domain mismatch')
    spec = yaml.safe_load((root / 'eval.yaml').read_text())
    if 'report_contract' not in {metric['name'] for metric in spec['metrics']}:
        raise ValueError('report metric missing')
    tasks = list((root / 'tasks').glob('*.yaml'))
    positive_files = {path.stem for path in tasks if yaml.safe_load(path.read_text())['expected']['should_trigger']}
    if positive_files != set(TASK_PROFILES):
        raise ValueError('positive task coverage must match every report profile')
    for path in tasks:
        task = yaml.safe_load(path.read_text())
        graders = {grader['name']: grader for grader in task['graders']}
        text_config = graders['task_completion']['config']
        if task['expected']['should_trigger']:
            patterns = text_config.get('regex_match', [])
            for marker in MARKERS:
                if not any(pattern.startswith('(?m)^' + marker) for pattern in patterns):
                    raise ValueError(f'{path.name}: positive marker missing: {marker}')
            program = graders['report_contract']['config']
            if program['command'] != 'python3' or program['args'] != [f'evals/{NAME}/check-report.py', TASK_PROFILES.get(path.stem)]:
                raise ValueError(f'{path.name}: incorrect program binding')
            if graders['skill_invocation']['config']['required_skills'] != [NAME]:
                raise ValueError(f'{path.name}: incorrect invocation binding')
        else:
            if set(text_config['not_contains']) != set(MARKERS) | {NAME}:
                raise ValueError(f'{path.name}: negative exclusions mismatch')
            if 'skill_invocation' in graders:
                raise ValueError(f'{path.name}: forbidden negative invocation grader')
            if any(token in task['inputs']['prompt'] for token in text_config['not_contains']):
                raise ValueError(f'{path.name}: forbidden token occurs in prompt')
    if any(metric['name'] == 'task_completion_substance' for metric in spec['metrics']):
        for filename in ('positive-trigger-1', 'positive-edge-1', 'positive-edge-4', 'positive-edge-5'):
            data = yaml.safe_load((root / 'tasks' / (filename + '.yaml')).read_text())
            if not any(grader['name'] == 'task_completion_substance' and grader['type'] == 'prompt' for grader in data['graders']):
                raise ValueError('missing selected-task substance grader')
    print(f'decoded task projections: {len(tasks)} passed')


def projection_mutations() -> None:
    """Reject isolated wrong-profile and missing-marker task projections.

    Mutations operate on temporary copies and never change repository files.
    """
    import shutil
    import tempfile
    import yaml
    original = Path(__file__).resolve().parent
    repo = original.parent.parent
    with tempfile.TemporaryDirectory(prefix='caie-projections-') as directory:
        root = Path(directory) / 'evals' / NAME
        shutil.copytree(original, root, ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(repo / 'skills' / NAME, Path(directory) / 'skills' / NAME)
        path = root / 'tasks' / 'positive-trigger-1.yaml'
        data = yaml.safe_load(path.read_text())
        for mutation in ('profile', 'marker', 'substance'):
            changed = yaml.safe_load(yaml.safe_dump(data))
            for grader in changed['graders']:
                if mutation == 'profile' and grader['name'] == 'report_contract':
                    grader['config']['args'][1] = 'blocked'
                if mutation == 'marker' and grader['name'] == 'task_completion':
                    grader['config']['regex_match'] = [pattern for pattern in grader['config']['regex_match'] if not pattern.startswith('(?m)^CAIE status:')]
            if mutation == 'substance':
                changed['graders'] = [grader for grader in changed['graders'] if grader['name'] != 'task_completion_substance']
            path.write_text(yaml.safe_dump(changed))
            try:
                projections(root)
            except ValueError:
                continue
            raise AssertionError('accepted task projection mutation: ' + mutation)
        path.write_text(yaml.safe_dump(data))
        (root / 'tasks' / 'positive-edge-3.yaml').unlink()
        try:
            projections(root)
        except ValueError as error:
            if str(error) != 'positive task coverage must match every report profile':
                raise
        else:
            raise AssertionError('accepted missing profile task')
    print('isolated task profile/marker/substance/coverage mutations: passed')


def main() -> None:
    """Read a report from stdin or execute free local preflight checks."""
    parser = argparse.ArgumentParser()
    parser.add_argument('profile', nargs='?', choices=PROFILES)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--projections', action='store_true')
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        if args.projections:
            projections()
            projection_mutations()
        if args.profile:
            validate(sys.stdin.read(), args.profile)
        elif not args.self_test and not args.projections:
            parser.error('provide a profile or preflight flag')
    except ValueError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == '__main__':
    main()
