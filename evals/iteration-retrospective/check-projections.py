#!/usr/bin/env python3
"""Check retrospective source, validator and decoded eval projections locally."""
from __future__ import annotations

from pathlib import Path
import argparse
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


def check() -> None:
    """Inspect every task projection and the source's explicit enum vocabulary.

    This detects structural drift and prompt-token collisions, not causal reasoning.
    """
    skill = (ROOT / 'skills/iteration-retrospective/SKILL.md').read_text()
    reference = (ROOT / 'skills/iteration-retrospective/references/report-format.md').read_text()
    template = re.search(r'```text\n(.*?)\n```', skill, re.S).group(1)
    markers = tuple(line.split(':', 1)[0] + ':' for line in template.splitlines() if not line.startswith('- '))
    assert markers == REPORT.MARKERS, 'source marker order differs from validator'
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
            for flag in ('--verdict', '--candidate', '--attempt-count'):
                assert args.count(flag) == 1, 'missing task expectation: ' + flag
            assert any(g['type'] == 'skill_invocation' for g in graders), 'positive invocation missing'
            if '--labels' in args:
                assert len(args[args.index('--labels') + 1:]) == 8, 'caller-label cardinality'
        else:
            assert not programs and not any(g['type'] == 'skill_invocation' for g in graders), 'negative invocation drift'
            forbidden = set()
            for grader in graders:
                if grader['type'] == 'text':
                    forbidden.update(grader['config'].get('not_contains', []))
            assert set((*REPORT.MARKERS, 'iteration-retrospective')) <= forbidden, 'negative exclusions incomplete'
            assert not set(GENERIC_FIELDS) & forbidden, 'generic field must not be a negative exclusion'
            ordinary = 'Status: Implementation complete.\nResult: Changes are ready.\nEvidence: Local checks passed.\nAssessment: Ready.\nVerdict: Accept.'
            negative_response(ordinary, forbidden)
            for marker in REPORT.MARKERS:
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
    parser.add_argument('--negative-task', choices=sorted(p.name for p in (SUITE / 'tasks').glob('negative-*.yaml')))
    args = parser.parse_args()
    if args.negative_task:
        task = yaml.safe_load((SUITE / 'tasks' / args.negative_task).read_text())
        forbidden = {token for g in task['graders'] if g['type'] == 'text' for token in g['config'].get('not_contains', [])}
        try:
            negative_response(sys.stdin.read(), forbidden)
        except ValueError as error:
            print(str(error), file=sys.stderr)
            raise SystemExit(1) from error
    else:
        check()
