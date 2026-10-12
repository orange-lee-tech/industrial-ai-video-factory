import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('layered',Path(__file__).parents[1]/'scripts/render_layered_motion.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class ReworkGateTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)
  (self.p/'script').mkdir();(self.p/'motion/pilot02').mkdir(parents=True);(self.p/'film-keyframes/batch01-v1').mkdir(parents=True)
  self.script=self.p/'script/candidate.json';self.script.write_text(json.dumps({'shots':[{'shot_id':s,'duration_seconds':6} for s in mod.IDS]}))
  hashes={}
  for s in ('SH003','SH007','SH008')+mod.IDS:
   f=self.p/'film-keyframes/batch01-v1'/f'{s}_keyframe.png';f.write_bytes(b'original');hashes[s]=mod.digest(f)
  self.permit=self.p/'motion/pilot02/permit.json';self.data={'status':'REWORK_TRIAL_ONLY','scope':list(mod.IDS),'source_sha256':mod.digest(self.script),'keyframe_sha256':hashes};self.save()
 def save(self):self.permit.write_text(json.dumps(self.data))
 def test_authorized_three_shots(self):self.assertEqual(set(mod.load_inputs(self.p)[0]),set(mod.IDS))
 def test_changed_png_blocks_rework(self):
  (self.p/'film-keyframes/batch01-v1/SH009_keyframe.png').write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'Stale'):mod.load_inputs(self.p)
 def test_expansion_blocks_rework(self):
  self.data['scope'].append('SH012');self.save()
  with self.assertRaisesRegex(ValueError,'scope'):mod.load_inputs(self.p)
 def test_rejected_permit_cannot_render(self):
  self.data['status']='FAIL';self.save()
  with self.assertRaisesRegex(ValueError,'scope'):mod.load_inputs(self.p)
 def test_camera_easing_preserves_endpoints(self):
  self.assertEqual(mod.smooth(0),0);self.assertEqual(mod.smooth(1),1)
