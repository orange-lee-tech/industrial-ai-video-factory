import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from scripts.setup_pilot import doctor,ROOT
from scripts.validate_pilot import check
from scripts.validate_project import validate
from scripts.clip_runner import contained,require_approval,verify_measurement
class PilotTests(unittest.TestCase):
    def test_populated_pilot(self):self.assertEqual(check(ROOT/'projects/csu-condenser-158s'),[])
    def test_six_discoverable_roles(self):self.assertEqual(len(doctor(ROOT)['skills']),6)
    def test_invalid_id_does_not_crash(self):
        d={'project_id':'xx','title':'x','active_stage':'script','shots':[{'shot_id':[]}]}
        self.assertTrue(validate(d))
    def test_path_escape(self):
        with self.assertRaises(ValueError):contained(ROOT,'../escape.png')
    def test_production_requires_review(self):
        with self.assertRaises(ValueError):require_approval(ROOT,{}, {},None)
    def test_stale_approval(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'approval.json';p.write_text(json.dumps({'status':'APPROVED','reviewer':'Reviewer','reviewed_at':'2026-10-12T12:00:00Z','script_sha256':'old','master_sha256':'a'}))
            with self.assertRaises(ValueError):require_approval(ROOT,{'script_sha256':'new','master_sha256':'a'}, {},p)
    def test_measurement_rejects_wrong_duration(self):
        m={'streams':[{'width':960,'height':540,'nb_read_frames':'144','avg_frame_rate':'24/1'}],'format':{'duration':'6'}}
        params={'duration_seconds':6,'fps':24,'width':960,'height':540};verify_measurement(m,params)
        m['format']['duration']='5'
        with self.assertRaises(ValueError):verify_measurement(m,params)

class RecoveryTests(unittest.TestCase):
    def test_failed_job_resumes_and_reuses_verified_output(self):
        from unittest.mock import patch
        from scripts.clip_runner import run
        import shutil
        source=ROOT/'projects/csu-condenser-158s'
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            for name in ['script/candidate.json','tasks/keyframes.json','references/master-spec.json']:
                dest=p/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/name,dest)
            inputs={'start_keyframe':p/'start.png','end_keyframe':p/'end.png'}
            for path in inputs.values():path.write_bytes(b'mock input')
            m={'streams':[{'width':960,'height':540,'nb_read_frames':'144','avg_frame_rate':'24/1'}],'format':{'duration':'6'}}
            def encode_ok(job,inputs,params,target,project):target.write_bytes(b'mock encoded file');return ['mock encoder']
            with patch('scripts.clip_runner.validate_inputs',return_value=inputs),patch('scripts.clip_runner.probe',return_value={'diagram-flow':{'available':True}}),patch('scripts.clip_runner.measure',return_value=m),patch('scripts.clip_runner.encode',side_effect=[RuntimeError('injected interruption'),None]) as encoder:
                with self.assertRaises(RuntimeError):run(p,'SH009',execute=True,preview=True)
                failed=next((p/'tmp/preview-clips').glob('*/*/run.json'))
                self.assertEqual(json.loads(failed.read_text())['state'],'FAILED');self.assertFalse((failed.parent/'RUNNING.lock').exists())
                encoder.side_effect=encode_ok
                self.assertEqual(run(p,'SH009',execute=True,preview=True)['state'],'COMPLETED')
                self.assertEqual(run(p,'SH009',execute=True,preview=True)['state'],'REUSED')
                self.assertEqual(encoder.call_count,2)
    def test_frame_approval_must_match_actual_hash(self):
        from scripts.clip_runner import sha
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);start=p/'start.png';end=p/'end.png';start.write_bytes(b'a');end.write_bytes(b'b')
            a=p/'approval.json';a.write_text(json.dumps({'status':'APPROVED','reviewer':'Reviewer','reviewed_at':'2026-10-12T12:00:00Z','script_sha256':'s','master_sha256':'m','frames':{'SH009':{'start':sha(start),'end':'wrong'}}}))
            with self.assertRaises(ValueError):require_approval(p,{'shot_id':'SH009','script_sha256':'s','master_sha256':'m'},{'start_keyframe':start,'end_keyframe':end},a)

class AdmissionTests(unittest.TestCase):
    def test_deferred_upstream_is_never_selected_for_setup(self):
        from scripts.setup_pilot import active_upstreams
        entries=json.loads((ROOT/'registry/approved-skills.json').read_text())['upstreams']
        self.assertEqual([e['name'] for e in active_upstreams(entries)],['create-storyboard'])
