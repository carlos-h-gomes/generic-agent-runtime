"""Produce a bounded context inventory without dropping mandatory instructions."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from harnesslib.evidence_io import EvidenceError, digest, member

def plan(root: Path, required: list[str], optional: list[str], budget: int) -> dict:
    if type(budget) is not int or budget < 1 or len(required) + len(optional) > 256 or not required:
        raise EvidenceError('bounded plan requires mandatory paths')
    if len(set(required + optional)) != len(required + optional):
        raise EvidenceError('duplicate context paths')
    rows, omitted, used = [], [], 0
    for name in required + optional:
        path = member(root, name)
        size = path.stat().st_size
        identity = digest(path)
        mandatory = name in required
        if not mandatory and used + size > budget:
            omitted.append(name)
            continue
        rows.append({'path': name, 'sha256': identity, 'bytes': size, 'mandatory': mandatory})
        used += size
    return {'status': 'over_budget' if used > budget else 'planned', 'files': rows,
            'omitted_optional': omitted, 'bytes': used, 'approximate_tokens': (used + 3) // 4,
            'limitation': 'Caller must enumerate all applicable ancestor instructions and triggered skills. Token count is an estimate; no savings claim.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--required', action='append', required=True)
    parser.add_argument('--optional', action='append', default=[])
    parser.add_argument('--budget-bytes', type=int, required=True)
    args = parser.parse_args()
    try:
        result = plan(args.root, args.required, args.optional, args.budget_bytes)
        print(json.dumps(result))
        return 3 if result['status'] == 'over_budget' else 0
    except (EvidenceError, OSError, ValueError):
        print('{"status":"invalid","error":"Review context paths and budget."}')
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
