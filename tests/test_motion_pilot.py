import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('motion',Path(__file__).parents[1]/'scripts/render_motion_pilot.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class TrialGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)
        (self.p/'script').mkdir(); (self.p/'motion/pilot01').mkdir(parents=True); (self.p/'film-keyframes/batch01-v1').mkdir(parents=True)
        self.script=self.p/'script/candidate.json'
        self.script.write_text(json.dumps({'shots':[{'shot_id':s,'duration_seconds':6} for s in m.IDS]}))
        hashes={}
        for s in ('SH003','SH007','SH008')+m.IDS:
            f=self.p/'film-keyframes/batch01-v1'/f'{s}_keyframe.png';f.write_bytes(b'immutable raster fixture');hashes[s]=m.sha(f)
        self.permit=self.p/'motion/pilot01/permit.json'
        self.data={'scope':list(m.IDS),'status':'CONDITIONAL_TRIAL_ONLY','source_sha256':m.sha(self.script),'keyframe_sha256':hashes}
        self.save()
    def save(self): self.permit.write_text(json.dumps(self.data))
    def test_current_permit_accepts_only_three_trial_shots(self):
        self.assertEqual(set(m.authorized_inputs(self.p)[2]),set(m.IDS))
    def test_changed_input_revokes_trial(self):
        (self.p/'film-keyframes/batch01-v1/SH011_keyframe.png').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Stale permit'): m.authorized_inputs(self.p)
    def test_expanded_scope_is_rejected(self):
        self.data['scope'].append('SH012');self.save()
        with self.assertRaisesRegex(ValueError,'scope mismatch'): m.authorized_inputs(self.p)
    def test_changed_timing_is_rejected_even_if_resigned(self):
        self.script.write_text(json.dumps({'shots':[{'shot_id':s,'duration_seconds':8} for s in m.IDS]}))
        self.data['source_sha256']=m.sha(self.script);self.save()
        with self.assertRaisesRegex(ValueError,'timing changed'): m.authorized_inputs(self.p)
