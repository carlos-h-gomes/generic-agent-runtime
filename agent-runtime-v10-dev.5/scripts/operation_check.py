"""Pure preflight; this is neither a sandbox nor a deployment executor."""
from harnesslib.evidence_io import EvidenceError, fresh, keys, sha

def check(action: dict, approval: dict, host_intercepts: bool = False) -> dict:
    fields = {'tool', 'action', 'target', 'effect', 'artifact_sha256'}
    keys(action, fields)
    keys(approval, fields | {'observed_at', 'expires_at', 'status'})
    sha(action['artifact_sha256'])
    if any(not isinstance(action[k], str) or not action[k] or len(action[k]) > 500 for k in fields):
        raise EvidenceError('bounded action identity required')
    fresh(approval)
    if approval['status'] != 'approved' or any(action[k] != approval[k] for k in fields):
        return {'status': 'blocked', 'reason': 'Approval does not cover the exact action.'}
    return {'status': 'preflight_complete' if host_intercepts is True else 'incomplete',
            'reason': 'Host interception must be independently verified; records do not grant authority.'}
