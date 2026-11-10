"""Opt-in local report profiles; parser acceptance is not scanner qualification."""
import json
from harnesslib.evidence_io import EvidenceError, pairs

def normalize(profile: str, content: bytes, admitted: bool = False) -> dict:
    if len(content) > 1_048_576 or type(admitted) is not bool:
        raise EvidenceError('bounded report/admission required')
    value = json.loads(content.decode('utf-8'), object_pairs_hook=pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(EvidenceError('nonfinite JSON')))
    findings, gaps, checks = 0, 0, 0
    if profile == 'playwright-json-v1':
        if not isinstance(value, dict) or not isinstance(value.get('stats'), dict) or not isinstance(value.get('suites'), list) or not isinstance(value.get('errors'), list):
            raise EvidenceError('unsupported Playwright report')
        stats = value['stats']
        numbers = [stats.get(k) for k in ('expected', 'unexpected', 'flaky', 'skipped')]
        if any(type(n) is not int or n < 0 for n in numbers):
            raise EvidenceError('invalid test counts')
        checks = sum(numbers)
        findings = stats['unexpected'] + len(value['errors'])
        gaps = stats['flaky'] + stats['skipped']
    elif profile == 'axe-json-v1':
        if not isinstance(value, dict) or not isinstance(value.get('testEngine'), dict) or value['testEngine'].get('name') != 'axe-core':
            raise EvidenceError('unsupported axe report')
        arrays = [value.get(k) for k in ('violations','incomplete','passes','inapplicable')]
        if any(not isinstance(a, list) for a in arrays):
            raise EvidenceError('invalid accessibility results')
        findings, gaps, checks = len(arrays[0]),len(arrays[1]),len(arrays[2])
    elif profile == 'osv-json-v1':
        if not isinstance(value, dict) or not isinstance(value.get('results'), list):
            raise EvidenceError('unsupported OSV report')
        for result in value['results']:
            if not isinstance(result, dict) or not isinstance(result.get('packages'), list):
                raise EvidenceError('invalid OSV result')
            for package in result['packages']:
                if not isinstance(package, dict) or not isinstance(package.get('package'), dict) or not isinstance(package.get('vulnerabilities'), list):
                    raise EvidenceError('invalid OSV package')
                checks += 1
                findings += len(package['vulnerabilities'])
    elif profile == 'gitleaks-json-v1':
        if not isinstance(value,list):
            raise EvidenceError('unsupported Gitleaks report')
        for item in value:
            if not isinstance(item,dict) or not isinstance(item.get('RuleID'),str) or not isinstance(item.get('File'),str):
                raise EvidenceError('invalid Gitleaks finding')
        findings = len(value)
        # An empty array contains no scan scope/count/exit evidence.
        gaps = 1 if not findings else 0
    else:
        raise EvidenceError('unknown adapter profile')
    status = 'blocked' if findings else 'incomplete' if gaps or not checks or not admitted else 'report_clean'
    return {'status':status,'findings':findings,'gaps':gaps,'checks':checks,
            'limitation':'Requires separately trusted exact tool/version, command exit, scanned scope, coverage and report digest. Accessibility also requires manual/visual review.'}
