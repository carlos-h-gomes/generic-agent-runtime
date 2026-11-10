"""Check a reviewed delivery policy against artifact-bound evidence; never run code."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from harnesslib.evidence_io import EvidenceError, bound, digest, fresh, keys, load, member, sha

CONTROLS = {f'VC-{i:02d}' for i in range(1, 16)}

def check(root: Path, policy_name: str, expected_policy: str, record: dict) -> dict:
    policy_path = member(root, policy_name)
    if digest(policy_path) != sha(expected_policy):
        raise EvidenceError('reviewed policy digest changed')
    policy = load(policy_path)
    keys(policy, {'schema_version', 'artifact', 'controls'})
    if policy['schema_version'] != '1.0':
        raise EvidenceError('unsupported policy version')
    artifact = bound(root, policy['artifact'])
    controls = policy['controls']
    if not isinstance(controls, dict) or set(controls) != CONTROLS:
        raise EvidenceError('all fifteen controls require disposition')
    keys(record, {'schema_version', 'policy_sha256', 'artifact_sha256', 'observed_at', 'expires_at', 'evidence'})
    if record['schema_version'] != '1.0' or record['policy_sha256'] != expected_policy or record['artifact_sha256'] != digest(artifact):
        raise EvidenceError('delivery identity mismatch')
    fresh(record)
    if not isinstance(record['evidence'], dict) or set(record['evidence']) - CONTROLS:
        raise EvidenceError('unknown evidence control')
    gaps, failures = [], []
    for control, requirement in controls.items():
        keys(requirement, {'applicable', 'rationale', 'checks'})
        if type(requirement['applicable']) is not bool or not isinstance(requirement['rationale'], str) or not requirement['rationale'].strip():
            raise EvidenceError('reviewed applicability rationale required')
        checks = requirement['checks']
        if not isinstance(checks, dict) or (requirement['applicable'] and not checks):
            raise EvidenceError('applicable control requires checks')
        if not requirement['applicable']:
            if checks:
                raise EvidenceError('inapplicable control cannot hide checks')
            continue
        entries = record['evidence'].get(control, {})
        if not isinstance(entries, dict) or set(entries) - set(checks):
            raise EvidenceError('unknown check evidence')
        for name, kind in checks.items():
            if kind not in {'automated', 'manual'}:
                raise EvidenceError('unknown check kind')
            item = entries.get(name)
            if item is None:
                gaps.append(f'{control}/{name}: missing')
                continue
            keys(item, {'status', 'kind', 'artifact_sha256', 'observed_at', 'expires_at', 'proof'})
            fresh(item)
            bound(root, item['proof'])
            if item['kind'] != kind or item['artifact_sha256'] != record['artifact_sha256']:
                raise EvidenceError('check scope mismatch')
            if item['status'] == 'failed':
                failures.append(f'{control}/{name}')
            elif item['status'] != 'passed':
                gaps.append(f'{control}/{name}: not verified')
    return {'status': 'blocked' if failures else 'incomplete' if gaps else 'evidence_complete',
            'failures': failures, 'gaps': gaps,
            'limitation': 'Evidence completeness does not authenticate reviewers or prove production safety.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--policy', required=True)
    parser.add_argument('--expected-policy-sha256', required=True)
    parser.add_argument('--record', required=True)
    args = parser.parse_args()
    try:
        result = check(args.root, args.policy, args.expected_policy_sha256, load(member(args.root, args.record)))
        print(json.dumps(result))
        return 1 if result['status'] == 'blocked' else 3 if result['status'] == 'incomplete' else 0
    except (EvidenceError, ValueError, OSError, RecursionError):
        print(json.dumps({'status': 'invalid', 'error': 'Invalid, stale, or changed evidence; review local inputs.'}))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
