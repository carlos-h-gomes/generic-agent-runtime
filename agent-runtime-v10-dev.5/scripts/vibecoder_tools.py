"""Read-only local preflight and report inspection commands for GAR 10."""
import argparse
import json
from pathlib import Path
from harnesslib.evidence_io import EvidenceError, digest, load, member, sha
import external_components
import operation_check
import report_adapters

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    sub=parser.add_subparsers(dest='command',required=True)
    component=sub.add_parser('component')
    component.add_argument('--record',required=True)
    component.add_argument('--expected-record-sha256',required=True)
    operation=sub.add_parser('operation')
    operation.add_argument('--action',required=True)
    operation.add_argument('--approval',required=True)
    report=sub.add_parser('report')
    report.add_argument('--profile',required=True,choices=['playwright-json-v1','axe-json-v1','osv-json-v1','gitleaks-json-v1'])
    report.add_argument('--report',required=True)
    report.add_argument('--expected-report-sha256',required=True)
    args=parser.parse_args()
    try:
        if args.command=='component':
            path=member(args.root,args.record)
            if digest(path)!=sha(args.expected_record_sha256):
                raise EvidenceError('reviewed component record changed')
            result=external_components.check(args.root,load(path))
        elif args.command=='operation':
            result=operation_check.check(load(member(args.root,args.action)),load(member(args.root,args.approval)))
        else:
            path=member(args.root,args.report)
            if digest(path)!=sha(args.expected_report_sha256):
                raise EvidenceError('report identity changed')
            # Inspection cannot establish tool authenticity, exact scope or successful execution.
            result=report_adapters.normalize(args.profile,path.read_bytes())
        print(json.dumps(result))
        return 1 if result['status']=='blocked' else 3 if result['status']=='incomplete' else 0
    except (EvidenceError,ValueError,OSError,TypeError,RecursionError):
        print('{"status":"invalid","error":"Invalid, stale, unsupported or changed inputs; review local evidence."}')
        return 2

if __name__=='__main__':
    raise SystemExit(main())
