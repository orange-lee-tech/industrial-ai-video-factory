#!/usr/bin/env python3
"""Small original stdlib-only input contract gate, not a video renderer or fact reviewer."""
import argparse, hashlib, json, pathlib, re, sys

def check(job, workspace, *, verify_asset=True):
    errors=[]
    if job.get("schema_version")!="0.1": errors.append("unsupported schema_version")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*",str(job.get("project_id",""))):errors.append("invalid project_id")
    if not re.fullmatch(r"SH[0-9]{3,}",str(job.get("shot_id",""))): errors.append("invalid shot_id")
    for key in ("duration_seconds","fps","width","height"):
        v=job.get(key)
        if isinstance(v,bool) or not isinstance(v,(int,float)) or v<=0:errors.append(f"invalid {key}")
    if job.get("silent") is not True: errors.append("silent must be true")
    if job.get("billing_approved") is not False: errors.append("no paid runs supported in offline gate")
    if not isinstance(job.get("backend"),str) or not job["backend"].strip():errors.append("missing backend")
    rel=job.get("reference_asset")
    if not isinstance(rel,str) or not rel or pathlib.PurePosixPath(rel).is_absolute() or ".." in pathlib.PurePosixPath(rel).parts or "\\" in rel:
        errors.append("reference_asset must be normalized workspace-relative path")
    elif verify_asset:
        root=pathlib.Path(workspace).resolve()
        asset=(root/rel).resolve()
        if not asset.is_relative_to(root):errors.append("reference_asset escapes workspace")
        elif not asset.is_file():errors.append("reference_asset does not exist")
        else:
            digest=hashlib.sha256(asset.read_bytes()).hexdigest()
            if digest!=job.get("reference_sha256"):errors.append("reference_sha256 mismatch")
    if not re.fullmatch(r"[0-9a-f]{64}",str(job.get("reference_sha256",""))):errors.append("invalid reference_sha256")
    if not isinstance(job.get("equipment_master_revision"),str) or not job["equipment_master_revision"].strip():errors.append("missing equipment_master_revision")
    if not isinstance(job.get("motion_spec"),str) or not job["motion_spec"].strip():errors.append("missing motion_spec")
    return errors

def main():
    p=argparse.ArgumentParser(); p.add_argument("job",type=pathlib.Path);p.add_argument("--workspace",type=pathlib.Path,required=True);a=p.parse_args()
    try: j=json.loads(a.job.read_text(encoding="utf-8"))
    except (OSError,ValueError) as e:print(f"INVALID INPUT: {e}");return 2
    if not isinstance(j,dict): print("INVALID INPUT: JSON object required");return 2
    err=check(j,a.workspace)
    if err:
        for e in err:print("FAIL:",e)
        return 1
    print("PASS: input contract only; no billing, rendering or engineering approval performed")
    return 0
if __name__=="__main__":sys.exit(main())
