#!/usr/bin/env python3
"""Validate retrospective report profiles and run free deterministic mutations."""
from __future__ import annotations

import argparse
import re
import sys

MARKERS = ('Retrospective:', 'Retrospective Assessment:', 'Retrospective Attempts:', 'Retrospective Learnings:',
           'Retrospective Prevention:', 'Retrospective Next Checks:', 'Retrospective Skill Candidate:', 'Retrospective Verdict:')
STATUSES = ('worked', 'partly-worked', 'failed', 'inconclusive', 'superseded')
CAUSES = ('confirmed', 'likely', 'unknown')
MECHANISMS = ('deterministic check', 'shared helper', 'repository guidance', 'refactor', 'reusable skill')
CANDIDATES = ('new skill', 'extend existing guidance', 'no new skill')
VERDICTS = ('CLEAN', 'CONCERNS', 'BLOCK')
CLARIFICATION_MARKERS = ('Retrospective Label Conflict:', 'Retrospective Label Request:')


def valid_labels(labels: tuple[str, ...]) -> bool:
    """Check the effective caller-label set before nonblocked report formatting.

    Blocked reports ignore this set; clarification requires it to be invalid.
    """
    return (len(labels) == len(MARKERS) and len(set(labels)) == len(labels)
            and all(label.splitlines() == [label] and re.fullmatch(r'[^:]+:', label) and label[:-1].strip()
                    and not any(ord(char) < 0x20 or 0x7f <= ord(char) <= 0x9f for char in label)
                    and not label.startswith('- ') for label in labels))


def validate_clarification(text: str, labels: tuple[str, ...]) -> None:
    """Validate the fixed two-line clarification for invalid nonblocked labels.

    Explanation and request semantics remain contextual task assertions.
    """
    if valid_labels(labels):
        raise ValueError('clarification requires invalid caller labels')
    lines = [line for line in text.splitlines() if line.strip()]
    if '\x00' in text or len(lines) != 2:
        raise ValueError('clarification requires exactly two marker lines')
    for line, marker in zip(lines, CLARIFICATION_MARKERS):
        if not line.startswith(marker + ' ') or not line[len(marker):].strip():
            raise ValueError('invalid clarification marker order or value')


def rows(lines: list[str], prefix: str, fields: tuple[str, ...], domains: dict[str, tuple[str, ...]]) -> None:
    """Check consecutive row IDs, exact field order and nonempty field values.

    Scalar values may contain marker text, but cannot contain field separators.
    """
    if not lines:
        raise ValueError('section must not be empty')
    for number, line in enumerate(lines, 1):
        parts = line.split(' | ')
        if parts[0] != f'- {prefix}{number}' or len(parts) != len(fields) + 1:
            raise ValueError('invalid row numbering or field count')
        for part, field in zip(parts[1:], fields):
            start = field + ': '
            if not part.startswith(start) or not part[len(start):].strip() or '|' in part:
                raise ValueError('invalid row field order or value')
            value = part[len(start):]
            if field in domains and value not in domains[field]:
                raise ValueError('invalid ' + field + ' enum')


def validate(text: str, labels: tuple[str, ...] = MARKERS, expected: str | None = None,
             candidate: str | None = None, attempt_count: int | None = None) -> None:
    """Validate default, caller-label and blocked profiles without causal inference.

    Optional fixture expectations check the task's verdict, candidate and row count.
    """
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines or '\x00' in text:
        raise ValueError('empty or invalid report')
    blocked = lines[-1] == 'Retrospective Verdict: BLOCK'
    if not blocked and not valid_labels(labels):
        raise ValueError('invalid caller labels')
    if attempt_count is not None and attempt_count < 0:
        raise ValueError('invalid attempt count')
    active = MARKERS if blocked else labels
    inspected_markers = set(MARKERS) if blocked else set(MARKERS) | set(labels)
    if any(line.startswith(marker) for line in lines for marker in inspected_markers
           if marker not in active):
        raise ValueError('inactive marker')
    positions = []
    for label in active:
        hits = [i for i, line in enumerate(lines) if line == label or line.startswith(label + ' ')]
        if len(hits) != 1:
            raise ValueError('marker must occur exactly once')
        positions.append(hits[0])
    if positions != sorted(positions) or positions[:3] != [0, 1, 2]:
        raise ValueError('invalid marker order or leading prose')
    if positions[-1] != len(lines) - 1 or positions[-2] != positions[-1] - 1:
        raise ValueError('verdict must terminate report')
    scalar = {}
    for i in (0, 1, 6, 7):
        line = lines[positions[i]]
        value = line[len(active[i]):].strip()
        if not value:
            raise ValueError('empty scalar value')
        scalar[i] = value
    for i in (2, 3, 4, 5):
        if lines[positions[i]] != active[i]:
            raise ValueError('section marker must stand alone')
    verdict = scalar[7]
    if verdict == 'BLOCK' and not blocked:
        raise ValueError('BLOCK requires default labels and blocked profile')
    if verdict not in VERDICTS or (expected is not None and verdict != expected):
        raise ValueError('invalid or unexpected verdict')
    allowed = ('not assessed',) if blocked else CANDIDATES
    if scalar[6] not in allowed or (candidate is not None and scalar[6] != candidate):
        raise ValueError('invalid or unexpected skill candidate')
    sections = {i: lines[positions[i] + 1:positions[i + 1]] for i in (2, 3, 4, 5)}
    timeline = sections[2]
    if timeline == ['None.']:
        raise ValueError('timeline must use rows or blocked sentinel')
    if timeline != ['Not assessed.']:
        rows(timeline, 'A', ('Status', 'Action', 'Result', 'Evidence'), {'Status': STATUSES})
    elif timeline == ['Not assessed.'] and not blocked:
        raise ValueError('unavailable analysis requires BLOCK')
    if attempt_count is not None and len([line for line in timeline if line.startswith('- A')]) != attempt_count:
        raise ValueError('wrong attempt count')
    if blocked:
        if not scalar[1].startswith('Not assessed.'):
            raise ValueError('BLOCK assessment must name unavailable analysis')
        if len(sections[3]) != 1 or not re.fullmatch(r'Missing: \S.*', sections[3][0]):
            raise ValueError('BLOCK requires missing evidence')
        if sections[4] != ['Not assessed.']:
            raise ValueError('BLOCK prevention must be unavailable')
        if sections[5] == ['None.']:
            raise ValueError('BLOCK requires next checks')
    else:
        statuses = [line.split(' | ')[1].removeprefix('Status: ') for line in timeline]
        if any(status in ('failed', 'partly-worked') for status in statuses) and sections[3] == ['None.']:
            raise ValueError('failed or partly-worked attempts require learnings')
        if sections[3] != ['None.']:
            rows(sections[3], 'L', ('Cause', 'Lesson', 'Evidence'), {'Cause': CAUSES})
        if sections[4] != ['None.']:
            rows(sections[4], 'P', ('Mechanism', 'Decision'), {'Mechanism': MECHANISMS})
        mechanisms = [line.split(' | ')[1].removeprefix('Mechanism: ') for line in sections[4] if line.startswith('- P')]
        if ('reusable skill' in mechanisms) != (scalar[6] == 'new skill'):
            raise ValueError('skill candidate must match selected reusable skill')
        if scalar[6] == 'extend existing guidance' and 'repository guidance' not in mechanisms:
            raise ValueError('guidance candidate requires selected repository guidance')
        if verdict == 'CONCERNS' and sections[5] == ['None.']:
            raise ValueError('CONCERNS requires next checks')
    if sections[5] != ['None.']:
        if not sections[5]:
            raise ValueError('next checks must not be empty')
        for number, line in enumerate(sections[5], 1):
            if not re.fullmatch(rf'- N{number}: \S.*', line) or '|' in line:
                raise ValueError('invalid next-check numbering or value')


VALID = '''Retrospective: Fix report drift
Retrospective Assessment: Validator prevents omissions.
Retrospective Attempts:
- A1 | Status: failed | Action: Check fields | Result: Missing field | Evidence: Review
- A2 | Status: worked | Action: Share validator | Result: Passed | Evidence: Test
Retrospective Learnings:
- L1 | Cause: confirmed | Lesson: Centralize checks | Evidence: Review
Retrospective Prevention:
- P1 | Mechanism: deterministic check | Decision: Reuse validator
Retrospective Next Checks:
None.
Retrospective Skill Candidate: no new skill
Retrospective Verdict: CLEAN'''
BLOCK = '''Retrospective: Not assessed.
Retrospective Assessment: Not assessed. No history supplied.
Retrospective Attempts:
Not assessed.
Retrospective Learnings:
Missing: goal, attempts and outcomes
Retrospective Prevention:
Not assessed.
Retrospective Next Checks:
- N1: Provide goal, attempts and outcomes
Retrospective Skill Candidate: not assessed
Retrospective Verdict: BLOCK'''
CUSTOM = ('Goal:', 'Outcome:', 'Attempts:', 'Lessons:', 'Controls:', 'Checks:', 'Candidate:', 'Result:')


def replace_labels(text: str, labels: tuple[str, ...]) -> str:
    """Replace only leading report markers in a deterministic fixture.

    Payload marker literals remain ordinary field text.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        for old, new in zip(MARKERS, labels):
            if line == old or line.startswith(old + ' '):
                lines[i] = new + line[len(old):]
                break
    return '\n'.join(lines)


def self_test() -> None:
    """Accept every profile and reject isolated grammar and branch mutations.

    These checks validate serialization; they do not prove model reasoning.
    """
    custom = replace_labels(VALID, CUSTOM)
    profiles = [(VALID, MARKERS), (custom, CUSTOM), (BLOCK, MARKERS), (BLOCK, CUSTOM)]
    checks = 0
    for text, labels in profiles:
        validate(text, labels)
        lines = text.splitlines()
        active = MARKERS if text == BLOCK else labels
        mutations = [text + '\nTrailing prose', text.replace('CLEAN', 'OK'),
                     text.replace('not assessed\nRetrospective Verdict:', 'no new skill\nRetrospective Verdict:')]
        for marker in active:
            index = next(i for i, line in enumerate(lines) if line == marker or line.startswith(marker + ' '))
            mutations += ['\n'.join(lines[:index] + lines[index + 1:]), text + '\n' + lines[index]]
        for i in range(len(active) - 1):
            changed = lines[:]
            left = next(j for j, line in enumerate(lines) if line == active[i] or line.startswith(active[i] + ' '))
            right = next(j for j, line in enumerate(lines) if line == active[i + 1] or line.startswith(active[i + 1] + ' '))
            changed[left], changed[right] = changed[right], changed[left]
            mutations.append('\n'.join(changed))
        if text == BLOCK:
            mutations += [text.replace('Retrospective Verdict: BLOCK', 'Retrospective Verdict: CLEAN'), text.replace('Missing:', 'Lesson:'),
                          text.replace('Retrospective Prevention:\nNot assessed.', 'Retrospective Prevention:\nNone.'), text.replace('Retrospective Attempts:\nNot assessed.', 'Retrospective Attempts:\nNone.'), replace_labels(text, CUSTOM)]
        else:
            mutations += [text.replace('worked |', 'good |'), text.replace('Cause: confirmed', 'Cause: certain'),
                          text.replace('Mechanism: deterministic check', 'Mechanism: source-of-truth change'),
                          text.replace('Retrospective Skill Candidate: no new skill', 'Retrospective Skill Candidate: not assessed'),
                          text.replace('A2 |', 'A3 |'), text.replace(' | Decision:', ' | Extra: unexpected | Decision:'),
                          text.replace('Retrospective Verdict: CLEAN', 'Retrospective Verdict: BLOCK'), text.replace('Retrospective Learnings:\n', 'Retrospective Learnings:\nNot assessed.\n')]
        for mutation in mutations:
            if mutation == text:
                continue
            try:
                validate(mutation, labels)
            except ValueError:
                checks += 1
            else:
                raise AssertionError('accepted mutation: ' + mutation)
    for status in STATUSES:
        validate(VALID.replace('Status: failed', 'Status: ' + status))
    for cause in CAUSES:
        validate(VALID.replace('Cause: confirmed', 'Cause: ' + cause))
    for mechanism in MECHANISMS:
        report = VALID.replace('Mechanism: deterministic check', 'Mechanism: ' + mechanism)
        if mechanism == 'reusable skill':
            report = report.replace('Retrospective Skill Candidate: no new skill', 'Retrospective Skill Candidate: new skill')
        validate(report)
    guidance = VALID.replace('Mechanism: deterministic check', 'Mechanism: repository guidance')
    validate(guidance)
    validate(guidance.replace('Retrospective Skill Candidate: no new skill', 'Retrospective Skill Candidate: extend existing guidance'))
    mixed = guidance.replace('Retrospective Next Checks:', '- P2 | Mechanism: reusable skill | Decision: Codify the independent repeated judgment failure\nRetrospective Next Checks:')
    mixed = mixed.replace('Retrospective Skill Candidate: no new skill', 'Retrospective Skill Candidate: new skill')
    validate(mixed)
    invalid_candidates = [
        VALID.replace('Retrospective Skill Candidate: no new skill', 'Retrospective Skill Candidate: new skill'),
        VALID.replace('Retrospective Skill Candidate: no new skill', 'Retrospective Skill Candidate: extend existing guidance'),
        VALID.replace('Mechanism: deterministic check', 'Mechanism: reusable skill'),
        mixed.replace('Retrospective Skill Candidate: new skill', 'Retrospective Skill Candidate: extend existing guidance'),
    ]
    for invalid in invalid_candidates:
        try:
            validate(invalid)
        except ValueError:
            checks += 1
        else:
            raise AssertionError('accepted candidate/mechanism mismatch')
    for labels in (CUSTOM, (*MARKERS[:-1], 'Result:')):
        crossover = replace_labels(VALID, labels).replace('Result: CLEAN', 'Result: BLOCK')
        try:
            validate(crossover, labels)
        except ValueError as error:
            assert str(error) == 'BLOCK requires default labels and blocked profile', str(error)
            checks += 1
        else:
            raise AssertionError('accepted custom-labeled BLOCK')
    concerns = VALID.replace('Retrospective Verdict: CLEAN', 'Retrospective Verdict: CONCERNS').replace('Retrospective Next Checks:\nNone.', 'Retrospective Next Checks:\n- N1: Establish costs for the unresolved pattern')
    validate(concerns)
    no_learning = VALID.replace('Retrospective Learnings:\n- L1 | Cause: confirmed | Lesson: Centralize checks | Evidence: Review', 'Retrospective Learnings:\nNone.')
    success_only = no_learning.replace('- A1 | Status: failed | Action: Check fields | Result: Missing field | Evidence: Review', '- A1 | Status: worked | Action: Check fields | Result: All fields checked | Evidence: Test')
    validate(success_only.replace('Retrospective Prevention:\n- P1 | Mechanism: deterministic check | Decision: Reuse validator', 'Retrospective Prevention:\nNone.'))
    for labels in (MARKERS, CUSTOM):
        for status in ('failed', 'partly-worked'):
            mutation = replace_labels(no_learning.replace('Status: failed', 'Status: ' + status), labels)
            try:
                validate(mutation, labels)
            except ValueError as error:
                assert str(error) == 'failed or partly-worked attempts require learnings', str(error)
                checks += 1
            else:
                raise AssertionError('accepted missing required learnings')
        mutation = replace_labels(VALID.replace('Retrospective Verdict: CLEAN', 'Retrospective Verdict: CONCERNS'), labels)
        try:
            validate(mutation, labels)
        except ValueError as error:
            assert str(error) == 'CONCERNS requires next checks', str(error)
            checks += 1
        else:
            raise AssertionError('accepted missing CONCERNS next checks')
    validate(BLOCK.replace('Not assessed.\nRetrospective Learnings:', '- A1 | Status: failed | Action: Check fields | Result: Missing field | Evidence: Review\nRetrospective Learnings:'))
    partial_labels = ('Goal:', *MARKERS[1:])
    validate(replace_labels(VALID, partial_labels), partial_labels)
    validate(BLOCK, ('Duplicate:',) * 8)
    for caller_labels in (('Missing:', *CUSTOM[1:]), ('- N1:', *CUSTOM[1:]), ('Not assessed.:', *CUSTOM[1:])):
        validate(BLOCK, caller_labels)
    for labels in (('Duplicate:',) * 8, ('Missing colon', *MARKERS[1:]), (' ', *MARKERS[1:]), ('- N1:', *MARKERS[1:])):
        try:
            validate(VALID, labels)
        except ValueError:
            checks += 1
        else:
            raise AssertionError('accepted invalid labels')
    validate(VALID.replace('Evidence: Review', 'Evidence: Review includes Retrospective Verdict: BLOCK'))
    validate(BLOCK.replace('Not assessed.\nRetrospective Learnings:', '- A1 | Status: inconclusive | Action: unknown | Result: unknown | Evidence: unavailable\nRetrospective Learnings:'))
    clarification = 'Retrospective Label Conflict: Duplicate labels are not distinct.\nRetrospective Label Request: Please provide distinct valid replacement labels.'
    invalid_labels = (CUSTOM[0], CUSTOM[0], *CUSTOM[2:])
    # Documented str.splitlines boundaries, including the two-character CRLF.
    boundaries = ('\n', '\r', '\r\n', '\v', '\f', '\x1c', '\x1d', '\x1e', '\x85', '\u2028', '\u2029')
    for boundary in boundaries:
        for slot in range(len(CUSTOM)):
            labels = tuple(label[:-1] + boundary + ':' if i == slot else label for i, label in enumerate(CUSTOM))
            assert not valid_labels(labels), 'line boundary accepted in label'
            validate_clarification(clarification, labels)
            validate(BLOCK, labels)
            try:
                validate(replace_labels(VALID, labels), labels)
            except ValueError as error:
                assert str(error) == 'invalid caller labels', str(error)
                checks += 1
            else:
                raise AssertionError('accepted split-line label')
    # C0, DEL and C1 include controls that splitlines does not recognize.
    controls = tuple(chr(code) for code in (*range(0x20), *range(0x7f, 0xa0)))
    for control in controls:
        for slot in range(len(CUSTOM)):
            labels = tuple(label[:-1] + control + ':' if i == slot else label for i, label in enumerate(CUSTOM))
            assert not valid_labels(labels), 'control accepted in label'
            validate_clarification(clarification, labels)
            validate(BLOCK, labels)
            try:
                validate(custom, labels)
            except ValueError as error:
                assert str(error) == 'invalid caller labels', str(error)
                checks += 1
            else:
                raise AssertionError('accepted control in caller labels')
    for label in ('Goal with spaces:', 'Ціль:', '目標:', 'Go\u00a0al:'):
        labels = (label, *CUSTOM[1:])
        validate(replace_labels(VALID, labels), labels)
    for labels in (invalid_labels, ('Missing colon', *CUSTOM[1:]), ('- N1:', *CUSTOM[1:]), (' ', *CUSTOM[1:])):
        validate_clarification(clarification, labels)
        validate(BLOCK, labels)
    clarification_lines = clarification.splitlines()
    bad_clarifications = [VALID, BLOCK, custom, clarification + '\nTrailing prose',
                          '\n'.join(reversed(clarification_lines))]
    for line in clarification_lines:
        bad_clarifications += [line, clarification + '\n' + line]
    for marker in CLARIFICATION_MARKERS:
        bad_clarifications += [clarification.replace(marker, 'Other:'),
                               clarification.replace(next(line for line in clarification_lines if line.startswith(marker)), marker)]
    for mutation in bad_clarifications:
        try:
            validate_clarification(mutation, invalid_labels)
        except ValueError:
            checks += 1
        else:
            raise AssertionError('accepted clarification mutation')
    for report, labels, validator in ((clarification, MARKERS, validate_clarification),
                                      (clarification, invalid_labels, validate)):
        try:
            validator(report, labels)
        except ValueError:
            checks += 1
        else:
            raise AssertionError('accepted profile crossover')
    print(f'report profiles and {checks} deterministic mutations: passed')


def expectations(text: str, required: dict[str, str | None]) -> None:
    """Check explicit fixture expectations after structural report validation.

    Expected values come from the trusted task, not from report claims.
    """
    for field, expected in required.items():
        if expected is None:
            continue
        actual = []
        for line in text.splitlines():
            if line.startswith(('- A', '- L', '- P')):
                for part in line.split(' | ')[1:]:
                    if part.startswith(field + ': '):
                        actual.append(part[len(field) + 2:])
        if actual != expected.split(','):
            raise ValueError('unexpected ' + field + ' sequence')


def main() -> None:
    """Read raw Waza output from stdin or run local profile mutation checks.

    Invalid reports exit 1 with a concise diagnostic and no traceback.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--profile', choices=('report', 'label-clarification'), default='report')
    parser.add_argument('--labels', nargs=8, default=MARKERS)
    parser.add_argument('--verdict', choices=VERDICTS)
    parser.add_argument('--candidate', choices=(*CANDIDATES, 'not assessed'))
    parser.add_argument('--attempt-count', type=int)
    parser.add_argument('--statuses')
    parser.add_argument('--causes')
    parser.add_argument('--mechanisms')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    try:
        text = sys.stdin.read()
        if args.profile == 'label-clarification':
            if any(value is not None for value in (args.verdict, args.candidate, args.attempt_count,
                                                  args.statuses, args.causes, args.mechanisms)):
                raise ValueError('clarification cannot use report expectations')
            validate_clarification(text, tuple(args.labels))
        else:
            validate(text, tuple(args.labels), args.verdict, args.candidate, args.attempt_count)
            expectations(text, {'Status': args.statuses, 'Cause': args.causes, 'Mechanism': args.mechanisms})
    except ValueError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == '__main__':
    main()
