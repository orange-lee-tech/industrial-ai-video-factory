#!/usr/bin/env python3
"""Dependency-free static gate; NOT a physical-accuracy or image-quality validator."""
import argparse, json, pathlib, re, sys

VALID={"DRAFT","REVIEW","APPROVED","LOCKED"}
DOWN=VALID|{"BLOCKED"}
def validate(data):
    errors=[]
    if not isinstance(data,dict): return ["root must be object"]
    if not isinstance(data.get('title'),str) or not data['title'].strip(): errors.append('empty title')
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]+",str(data.get("project_id",""))): errors.append("invalid project_id")
    if data.get("active_stage") not in {"script","keyframe","clip","assembly","closed"}: errors.append("invalid active_stage")
    shots=data.get("shots")
    if not isinstance(shots,list) or not shots: return errors+["shots must be a nonempty list"]
    ids=set()
    for i,s in enumerate(shots):
        p=f"shots[{i}]"
        if not isinstance(s,dict): errors.append(p+" must be object"); continue
        sid=s.get("shot_id")
        if not isinstance(sid,str) or not re.fullmatch(r"SH[0-9]{3,}",sid): errors.append(p+" invalid shot_id")
        elif sid in ids: errors.append(p+" duplicate shot_id")
        if isinstance(sid,str): ids.add(sid)
        d=s.get("duration_seconds")
        if isinstance(d,bool) or not isinstance(d,(int,float)) or not 0<d<=60: errors.append(p+" invalid duration_seconds (0,60]")
        if not isinstance(s.get("script"),str) or not s["script"].strip(): errors.append(p+" empty script")
        for field,choices in [("script_status",VALID),("keyframe_status",DOWN),("clip_status",DOWN)]:
            if s.get(field) not in choices: errors.append(p+" invalid "+field)
        if not isinstance(s.get("equipment_ids"),list) or not all(isinstance(x,str) and x.strip() for x in s["equipment_ids"]): errors.append(p+" invalid equipment_ids")
        refs=s.get("reference_files")
        if not isinstance(refs,list) or not all(isinstance(x,str) for x in refs): errors.append(p+" invalid reference_files")
        script_ok=s.get("script_status") in {"APPROVED","LOCKED"}
        frame_ok=s.get("keyframe_status") in {"APPROVED","LOCKED"}
        if not script_ok and s.get("keyframe_status") not in {"BLOCKED","DRAFT"}: errors.append(p+" keyframe review requires approved script")
        if not frame_ok and s.get("clip_status") not in {"BLOCKED","DRAFT"}: errors.append(p+" clip review requires approved keyframe")
        if s.get("clip_status") in {"APPROVED","LOCKED"} and (not frame_ok or not script_ok): errors.append(p+" clip approval violated upstream gate")
    return errors

def main():
    p=argparse.ArgumentParser()
    p.add_argument("manifest",type=pathlib.Path)
    args=p.parse_args()
    try: data=json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError,ValueError) as exc: print("ERROR:",exc);return 2
    errors=validate(data)
    for e in errors: print("FAIL:",e)
    if errors: return 1
    print(f"PASS: {data['project_id']} ({len(data['shots'])} shots); structural gates only")
    return 0
if __name__=="__main__": sys.exit(main())
