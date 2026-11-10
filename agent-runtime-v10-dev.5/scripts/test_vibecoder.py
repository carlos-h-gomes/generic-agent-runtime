"""Independent negative fixtures for GAR 10 evidence boundaries."""
import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
import os
import subprocess
from harnesslib.evidence_io import EvidenceError, digest, load, member
import delivery_check
import context_plan
import operation_check
import external_components
import report_adapters

class EvidenceBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'artifact.txt').write_text('synthetic artifact', encoding='utf-8')
        (self.root / 'proof.txt').write_text('synthetic assertion only', encoding='utf-8')
        self.identity = digest(self.root / 'artifact.txt')
        now = datetime.now(timezone.utc)
        self.dates = {'observed_at': (now-timedelta(minutes=1)).isoformat(), 'expires_at': (now+timedelta(minutes=5)).isoformat()}
        self.proof = {'path': 'proof.txt', 'sha256': digest(self.root / 'proof.txt')}
        self.policy = {'schema_version':'1.0', 'artifact':{'path':'artifact.txt','sha256': self.identity},
                       'controls': {c:{'applicable':False, 'rationale':'synthetic fixture', 'checks':{}} for c in delivery_check.CONTROLS}}
        self.policy['controls']['VC-03'] = {'applicable':True,'rationale':'authorization boundary', 'checks': {'tenant':'automated', 'review':'manual'}}
        self.save_policy()
        item = {'status':'passed','kind':'automated','artifact_sha256':self.identity,'proof':self.proof,**self.dates}
        manual = {**item,'kind':'manual'}
        self.record = {'schema_version':'1.0','policy_sha256':self.policy_sha,'artifact_sha256':self.identity,
                       **self.dates,'evidence':{'VC-03':{'tenant':item,'review':manual}}}

    def save_policy(self):
        path = self.root/'policy.json'
        path.write_text(json.dumps(self.policy), encoding='utf-8')
        self.policy_sha = digest(path)

    def check(self):
        return delivery_check.check(self.root,'policy.json', self.policy_sha,self.record)

    def test_complete_structure(self):
        self.assertEqual(self.check()['status'],'evidence_complete')

    def test_missing_manual_never_passes(self):
        del self.record['evidence']['VC-03']['review']
        self.assertEqual(self.check()['status'],'incomplete')

    def test_failed_check_blocks(self):
        self.record['evidence']['VC-03']['tenant']['status']='failed'
        self.assertEqual(self.check()['status'],'blocked')

    def test_artifact_drift(self):
        (self.root/'artifact.txt').write_text('changed',encoding='utf-8')
        with self.assertRaises(EvidenceError): self.check()

    def test_policy_drift(self):
        (self.root/'policy.json').write_text('{}',encoding='utf-8')
        with self.assertRaises(EvidenceError): self.check()

    def test_proof_drift(self):
        (self.root/'proof.txt').write_text('changed',encoding='utf-8')
        with self.assertRaises(EvidenceError): self.check()

    def test_expired_and_future(self):
        for field,value in [('expires_at','2000-01-01T00:00:00Z'),('observed_at','2099-01-01T00:00:00Z')]:
            original=self.record[field]
            self.record[field]=value
            with self.assertRaises(EvidenceError): self.check()
            self.record[field]=original

    def test_manual_cannot_be_automated(self):
        self.record['evidence']['VC-03']['review']['kind']='automated'
        with self.assertRaises(EvidenceError): self.check()

    def test_missing_control(self):
        del self.policy['controls']['VC-15']
        self.save_policy()
        self.record['policy_sha256']=self.policy_sha
        with self.assertRaises(EvidenceError): self.check()

    def test_path_escape(self):
        for value in ['../outside','C:/outside','/outside','a\\b']:
            with self.assertRaises(EvidenceError): member(self.root,value)

    def test_duplicate_keys(self):
        path=self.root/'duplicate.json'
        path.write_text('{"status":"passed","status":"failed"}',encoding='utf-8')
        with self.assertRaises(EvidenceError): load(path)

    def test_oversize_json(self):
        path=self.root/'big.json'
        path.write_bytes(b' ' * 1_048_577)
        with self.assertRaises(EvidenceError): load(path)

    def test_mandatory_context_retained(self):
        result=context_plan.plan(self.root,['artifact.txt'],['proof.txt'],1)
        self.assertEqual(result['status'],'over_budget')
        self.assertEqual([v['path'] for v in result['files']],['artifact.txt'])
        self.assertEqual(result['omitted_optional'],['proof.txt'])

    def test_preflight_requires_verified_host(self):
        action={'tool':'mock','action':'publish','target':'loopback','effect':'external','artifact_sha256':self.identity}
        approval={**action,**self.dates,'status':'approved'}
        self.assertEqual(operation_check.check(action,approval)['status'],'incomplete')
        action['target']='production'
        self.assertEqual(operation_check.check(action,approval,True)['status'],'blocked')

    def test_incomplete_component_review(self):
        record={'schema_version':'1.0','origin':'https://example.invalid/component','revision':'a'*40,
                'artifact':{'path':'artifact.txt','sha256':self.identity},'owner':'synthetic reviewer',**self.dates,
                'reviews':{name:{'status':'not_verified','proof':self.proof} for name in external_components.REVIEWS}}
        self.assertEqual(external_components.check(self.root,record)['status'],'incomplete')
        record['revision']='main'
        with self.assertRaises(EvidenceError): external_components.check(self.root,record)

    def test_empty_reports_never_pass(self):
        for profile, value in [('gitleaks-json-v1',[]),('osv-json-v1',{'results':[]}),
                              ('playwright-json-v1',{'suites':[],'errors':[],'stats':{'expected':0,'unexpected':0,'flaky':0,'skipped':0}})]:
            self.assertEqual(report_adapters.normalize(profile,json.dumps(value).encode(),True)['status'],'incomplete')

    def test_unqualified_clean_browser_report(self):
        content=json.dumps({'suites':[{}],'errors':[],'stats':{'expected':1,'unexpected':0,'flaky':0,'skipped':0}}).encode()
        self.assertEqual(report_adapters.normalize('playwright-json-v1',content)['status'],'incomplete')

    def test_browser_failure_and_skips(self):
        for unexpected,skipped,status in [(1,0,'blocked'),(0,1,'incomplete')]:
            content=json.dumps({'suites':[{}],'errors':[],'stats':{'expected':1,'unexpected':unexpected,'flaky':0,'skipped':skipped}}).encode()
            self.assertEqual(report_adapters.normalize('playwright-json-v1',content,True)['status'],status)

    def test_axe_incomplete_and_findings(self):
        content=json.dumps({'testEngine':{'name':'axe-core'},'violations':[{}],'incomplete':[],'passes':[{}],'inapplicable':[]}).encode()
        self.assertEqual(report_adapters.normalize('axe-json-v1',content,True)['status'],'blocked')

    def test_unknown_or_forged_report(self):
        for profile in ['unknown','axe-json-v1','osv-json-v1','playwright-json-v1']:
            with self.assertRaises(EvidenceError): report_adapters.normalize(profile,b'{"status":"passed"}',True)

    @unittest.skipUnless(os.name=='nt','Windows reparse boundary only')
    def test_windows_junction_cannot_supply_evidence(self):
        with tempfile.TemporaryDirectory() as outside:
            (Path(outside)/'proof.txt').write_text('outside',encoding='utf-8')
            link=self.root/'junction'
            result=subprocess.run(['cmd','/c','mklink','/J',str(link),outside],capture_output=True,timeout=10)
            self.assertEqual(result.returncode,0)
            try:
                with self.assertRaises(EvidenceError): member(self.root,'junction/proof.txt')
            finally:
                link.rmdir()

if __name__ == '__main__':
    unittest.main(verbosity=2)
