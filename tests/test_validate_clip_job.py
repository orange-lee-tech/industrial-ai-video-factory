import hashlib, pathlib, tempfile, unittest
from scripts.validate_clip_job import check
class ClipJobGateTests(unittest.TestCase):
    def test_valid_dry_job(self):
        with tempfile.TemporaryDirectory() as root:
            f=pathlib.Path(root)/"frame.png";f.write_bytes(b"not-real-image-but-checksum-valid")
            j={"schema_version":"0.1","project_id":"csu-condenser-158s","shot_id":"SH007","duration_seconds":6,"fps":30,"width":1920,"height":1080,"reference_asset":"frame.png","reference_sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"equipment_master_revision":"r1","motion_spec":"camera drift","backend":"local-deterministic","silent":True,"billing_approved":False}
            self.assertEqual([],check(j,root))
            j["reference_sha256"]="0"*64
            self.assertIn("reference_sha256 mismatch",check(j,root))
    def test_traversal_rejected(self):
        j={"schema_version":"0.1","project_id":"x","shot_id":"SH001","duration_seconds":6,"fps":30,"width":1920,"height":1080,"reference_asset":"../secrets","reference_sha256":"0"*64,"equipment_master_revision":"r1","motion_spec":"a","backend":"a","silent":True,"billing_approved":False}
        self.assertIn("reference_asset must be normalized workspace-relative path",check(j,".",verify_asset=False))
    def test_paid_not_allowed(self):
        j={"schema_version":"0.1","project_id":"x","shot_id":"SH001","duration_seconds":6,"fps":30,"width":1920,"height":1080,"reference_asset":"frame.png","reference_sha256":"0"*64,"equipment_master_revision":"r1","motion_spec":"a","backend":"a","silent":True,"billing_approved":True}
        self.assertIn("no paid runs supported in offline gate",check(j,".",verify_asset=False))
if __name__=="__main__":unittest.main()
