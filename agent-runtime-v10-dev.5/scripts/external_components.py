"""Review a component admission record; never download, install or execute it."""
from urllib.parse import urlsplit
from harnesslib.evidence_io import EvidenceError, bound, fresh, keys, sha

REVIEWS = {'license_notice', 'dependencies_advisories', 'provenance', 'permissions_egress_telemetry', 'negative_tests'}

def check(root, record):
    keys(record, {'schema_version', 'origin', 'revision', 'artifact', 'owner', 'observed_at', 'expires_at', 'reviews'})
    if record['schema_version'] != '1.0':
        raise EvidenceError('unsupported component contract')
    url = urlsplit(record['origin'])
    if url.scheme != 'https' or not url.hostname or url.username or url.password or url.query or url.fragment:
        raise EvidenceError('official HTTPS origin required')
    revision = record['revision']
    if not isinstance(revision, str) or len(revision) not in {40, 64} or any(c not in '0123456789abcdef' for c in revision):
        raise EvidenceError('immutable source revision required')
    if not isinstance(record['owner'], str) or not record['owner'].strip():
        raise EvidenceError('review owner required')
    fresh(record)
    bound(root, record['artifact'])
    if not isinstance(record['reviews'], dict) or set(record['reviews']) != REVIEWS:
        raise EvidenceError('all component reviews required')
    gaps = []
    for name, review in record['reviews'].items():
        keys(review, {'status', 'proof'})
        bound(root, review['proof'])
        if review['status'] != 'passed':
            gaps.append(name)
    return {'status': 'incomplete' if gaps else 'record_complete', 'gaps': sorted(gaps),
            'limitation': 'Origin ownership, reviewer trust and binary provenance require independent verification.'}
