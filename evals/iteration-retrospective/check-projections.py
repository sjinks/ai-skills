#!/usr/bin/env python3
"""Check retrospective source, validator and decoded eval projections locally."""
from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
import sys

import yaml

from importlib.util import module_from_spec, spec_from_file_location

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / 'evals/iteration-retrospective'
SPEC = spec_from_file_location('retrospective_report', SUITE / 'check-report.py')
REPORT = module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)
GENERIC_FIELDS = ('Status:', 'Action:', 'Result:', 'Evidence:', 'Cause:', 'Lesson:', 'Mechanism:', 'Decision:', 'Assessment:', 'Verdict:')


def negative_response(text: str, forbidden: set[str]) -> None:
    """Apply the negative task's literal exclusions to a supplied response.

    This mirrors the configured token assertions without executing a model.
    """
    if any(token in text for token in forbidden):
        raise ValueError('negative output contains retrospective marker')


def envelope_assertion(assertions: list[str], marker: str) -> str:
    """Require the literal anchored first marker of the task's active profile.

    Row fields, inactive labels and unanchored marker mentions do not qualify.
    """
    pattern = '(?m)^' + re.escape(marker)
    if pattern not in assertions:
        raise ValueError('task_completion requires anchored active envelope marker')
    return pattern


def enum_assertions(assertions: list[str], marker: str, value: str, domain: tuple[str, ...]) -> None:
    """Bind a scalar enum's text assertions to its selected program value.

    Canonical anchored assertions are required; every existing same-field
    assertion must also accept that value outside attempt-row payloads.
    """
    expected = marker + ' ' + value
    canonical = '(?m)^' + re.escape(expected) + '$'
    # Spaces need no escaping in YAML regexes; both canonical spellings qualify.
    plain = '(?m)^' + re.escape(marker) + ' ' + value + '$'
    selected = [pattern for pattern in assertions if marker in pattern or re.escape(marker) in pattern]
    if not any(pattern in (canonical, plain) for pattern in selected):
        raise ValueError('profile-mismatch: missing discriminating ' + marker + ' assertion')
    if not all(re.search(pattern, expected) for pattern in selected):
        raise ValueError('profile-mismatch: incompatible ' + marker + ' assertion')
    if any(all(re.search(pattern, marker + ' ' + other) for pattern in selected) for other in domain if other != value):
        raise ValueError('profile-mismatch: nondiscriminating ' + marker + ' assertions')


def enum_mutations(assertions: list[str], marker: str, value: str, domain: tuple[str, ...]) -> None:
    """Reject a swapped, omitted or extra incompatible enum assertion.

    These mutations change only the selected scalar field's text assertion.
    """
    enum_assertions(assertions, marker, value, domain)
    expected = marker + ' ' + value
    candidates = ('(?m)^' + re.escape(expected) + '$', '(?m)^' + re.escape(marker) + ' ' + value + '$')
    index = next(index for index, pattern in enumerate(assertions) if pattern in candidates)
    wrong = '(?m)^' + re.escape(marker + ' ' + next(other for other in domain if other != value)) + '$'
    swapped = list(assertions)
    swapped[index] = wrong
    omitted = list(assertions)
    del omitted[index]
    for changed in (swapped, omitted, [*assertions, wrong]):
        try:
            enum_assertions(changed, marker, value, domain)
        except ValueError as error:
            assert str(error).startswith('profile-mismatch:')
        else:
            raise AssertionError('accepted incompatible ' + marker + ' projection')


def check() -> None:
    """Inspect every task projection and the source's explicit enum vocabulary.

    This detects structural drift and prompt-token collisions, not causal reasoning.
    """
    skill = (ROOT / 'skills/iteration-retrospective/SKILL.md').read_text()
    reference = (ROOT / 'skills/iteration-retrospective/references/report-format.md').read_text()
    templates = re.findall(r'```text\n(.*?)\n```', skill, re.S)
    markers = [tuple(line.split(':', 1)[0] + ':' for line in template.splitlines() if not line.startswith('- '))
               for template in templates]
    assert markers == [REPORT.CLARIFICATION_MARKERS, REPORT.MARKERS], 'source marker order differs from validator'
    for value in (*REPORT.STATUSES, *REPORT.CAUSES, *REPORT.MECHANISMS, *REPORT.CANDIDATES, *REPORT.VERDICTS, 'not assessed'):
        assert f'`{value}`' in reference, 'source domain missing: ' + value
    assert not re.search(r'\bowner\b', skill + reference, re.I), 'removed field remains in source'
    manifest = yaml.safe_load((SUITE / 'eval.yaml').read_text())
    metric = [m for m in manifest['metrics'] if m['name'] == 'report_contract']
    assert len(metric) == 1 and metric[0]['threshold'] == 1.0, 'report metric missing'
    tasks = sorted((SUITE / 'tasks').glob('*.yaml'))
    for path in tasks:
        task = yaml.safe_load(path.read_text())
        prompt = task['inputs']['prompt']
        assert not re.search(r'\bowner\b', path.read_text(), re.I), 'removed field remains in task'
        graders = task['graders']
        programs = [g for g in graders if g['type'] == 'program' and g['name'] == 'report_contract']
        if task['expected']['should_trigger']:
            assert len(programs) == 1, 'positive requires report program: ' + path.name
            config = programs[0]['config']
            assert config['command'] == 'python3', 'program command drift'
            args = config['args']
            assert args[0] == 'evals/iteration-retrospective/check-report.py', 'wrong checker'
            clarification = path.name == 'positive-edge-8.yaml'
            if clarification:
                assert args.count('--profile') == 1 and args[args.index('--profile') + 1] == 'label-clarification', 'clarification profile required'
                assert not set(('--verdict', '--candidate', '--attempt-count', '--statuses', '--causes', '--mechanisms')) & set(args), 'clarification has report expectations'
                assert '--labels' in args and not REPORT.valid_labels(tuple(args[args.index('--labels') + 1:])), 'clarification requires invalid labels'
                assertions = [token for g in graders if g['type'] == 'text' for token in g['config'].get('regex_match', [])]
                assert all(any(marker in token for token in assertions) for marker in REPORT.CLARIFICATION_MARKERS), 'clarification assertions missing'
            else:
                assert '--profile' not in args, 'report task profile drift'
                for flag in ('--verdict', '--candidate', '--attempt-count'):
                    assert args.count(flag) == 1, 'missing task expectation: ' + flag
            completions = [g for g in graders if g['type'] == 'text' and g['name'] == 'task_completion']
            assert len(completions) == 1, 'positive requires one text task_completion: ' + path.name
            labels = tuple(args[args.index('--labels') + 1:]) if '--labels' in args else REPORT.MARKERS
            active = (REPORT.CLARIFICATION_MARKERS if clarification else
                      REPORT.MARKERS if args[args.index('--verdict') + 1] == 'BLOCK' else labels)
            assertions = completions[0]['config'].get('regex_match', [])
            if not clarification:
                for position, flag, domain in ((7, '--verdict', REPORT.VERDICTS),
                                               (6, '--candidate', (*REPORT.CANDIDATES, 'not assessed'))):
                    enum_mutations(assertions, active[position], args[args.index(flag) + 1], domain)
            pattern = envelope_assertion(assertions, active[0])
            # Isolated projection mutations preserve every other task assertion.
            for replacement in (None, '(?m)^- A1', '(?m)^Inactive:', re.escape(active[0])):
                mutated = [token for token in assertions if token != pattern]
                if replacement is not None:
                    mutated.append(replacement)
                try:
                    envelope_assertion(mutated, active[0])
                except ValueError as error:
                    assert str(error) == 'task_completion requires anchored active envelope marker'
                else:
                    raise AssertionError('accepted missing active envelope assertion: ' + path.name)
            assert re.search(pattern, active[0] + ' value')
            assert not re.search(pattern, '- A1 | Evidence: ' + active[0] + ' value')
            assert any(g['type'] == 'skill_invocation' for g in graders), 'positive invocation missing'
            if '--labels' in args:
                assert len(args[args.index('--labels') + 1:]) == 8, 'caller-label cardinality'
        else:
            assert not programs and not any(g['type'] == 'skill_invocation' for g in graders), 'negative invocation drift'
            forbidden = set()
            for grader in graders:
                if grader['type'] == 'text':
                    forbidden.update(grader['config'].get('not_contains', []))
            assert set((*REPORT.MARKERS, *REPORT.CLARIFICATION_MARKERS, 'iteration-retrospective')) <= forbidden, 'negative exclusions incomplete'
            assert not set(GENERIC_FIELDS) & forbidden, 'generic field must not be a negative exclusion'
            ordinary = 'Status: Implementation complete.\nResult: Changes are ready.\nEvidence: Local checks passed.\nAssessment: Ready.\nVerdict: Accept.'
            negative_response(ordinary, forbidden)
            for marker in (*REPORT.MARKERS, *REPORT.CLARIFICATION_MARKERS):
                try:
                    negative_response(marker, forbidden)
                except ValueError:
                    pass
                else:
                    raise AssertionError('report marker not excluded')
            assert all(token not in prompt for token in forbidden), 'negative token occurs in prompt'
    print(f'source/validator/metric projections and all {len(tasks)} task files: passed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    probes = parser.add_mutually_exclusive_group()
    probes.add_argument('--label-set', action='store_true', help='validate a JSON array of caller labels from stdin')
    probes.add_argument('--positive-envelope-task', choices=sorted(p.name for p in (SUITE / 'tasks').glob('positive-*.yaml')))
    probes.add_argument('--negative-task', choices=sorted(p.name for p in (SUITE / 'tasks').glob('negative-*.yaml')))
    args = parser.parse_args()
    if args.label_set:
        try:
            labels = json.load(sys.stdin)
        except json.JSONDecodeError:
            print('invalid caller labels', file=sys.stderr)
            raise SystemExit(1) from None
        if not isinstance(labels, list) or not all(isinstance(label, str) for label in labels) or not REPORT.valid_labels(tuple(labels)):
            print('invalid caller labels', file=sys.stderr)
            raise SystemExit(1)
    elif args.positive_envelope_task:
        task = yaml.safe_load((SUITE / 'tasks' / args.positive_envelope_task).read_text())
        config = next(g['config'] for g in task['graders'] if g['type'] == 'program' and g['name'] == 'report_contract')
        flags = config['args']
        marker = (REPORT.CLARIFICATION_MARKERS[0] if '--profile' in flags else
                  REPORT.MARKERS[0] if flags[flags.index('--verdict') + 1] == 'BLOCK' or '--labels' not in flags
                  else flags[flags.index('--labels') + 1])
        assertions = next(g['config']['regex_match'] for g in task['graders'] if g['type'] == 'text' and g['name'] == 'task_completion')
        pattern = envelope_assertion(assertions, marker)
        if not re.search(pattern, sys.stdin.read()):
            print('response missing anchored active envelope marker', file=sys.stderr)
            raise SystemExit(1)
    elif args.negative_task:
        task = yaml.safe_load((SUITE / 'tasks' / args.negative_task).read_text())
        forbidden = {token for g in task['graders'] if g['type'] == 'text' for token in g['config'].get('not_contains', [])}
        try:
            negative_response(sys.stdin.read(), forbidden)
        except ValueError as error:
            print(str(error), file=sys.stderr)
            raise SystemExit(1) from error
    else:
        check()
