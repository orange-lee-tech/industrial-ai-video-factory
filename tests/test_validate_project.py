import unittest
from scripts.validate_project import validate
BASE={"project_id":"demo-001","active_stage":"script","shots":[{"shot_id":"SH001","duration_seconds":5,"equipment_ids":["TURBINE_HP_01"],"reference_files":[],"script":"蒸汽进入高压缸","script_status":"APPROVED","keyframe_status":"BLOCKED","clip_status":"BLOCKED"}]}
class GateTests(unittest.TestCase):
    def test_valid(self): self.assertEqual(validate(dict(BASE,title='Smoke')),[])
    def test_no_script_approval(self):
        import copy
        d=copy.deepcopy(BASE);d["shots"][0]["script_status"]="DRAFT";d["shots"][0]["keyframe_status"]="APPROVED"
        self.assertTrue(validate(d))
    def test_no_keyframe_approval(self):
        import copy
        d=copy.deepcopy(BASE);d["shots"][0]["clip_status"]="APPROVED"
        self.assertTrue(validate(d))
    def test_duplicates(self):
        import copy
        d=copy.deepcopy(BASE);d["shots"].append(copy.deepcopy(d["shots"][0]))
        self.assertTrue(any("duplicate" in e for e in validate(d)))
if __name__=="__main__":unittest.main()
