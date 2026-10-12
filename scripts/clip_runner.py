#!/usr/bin/env python3
"""Zero-spend replaceable local backends; dry-run default, content-addressed jobs."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_PROJECT=ROOT/'projects/csu-condenser-158s'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def atomic_json(p,data):
    tmp=p.with_suffix('.json.partial');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,p)
def contained(root,relative):
    p=(root/relative).resolve()
    if not p.is_relative_to(root.resolve()):raise ValueError('Path escapes project')
    return p

def probe():
    import importlib.util
    ready=bool(shutil.which('ffmpeg') and shutil.which('ffprobe') and importlib.util.find_spec('PIL'))
    return {'diagram-flow':{'available':ready,'requires':['Pillow','ffmpeg','ffprobe'],'network':False,'billable':False},'still-pan':{'available':ready,'requires':['Pillow','ffmpeg','ffprobe'],'network':False,'billable':False}}

def validate_inputs(project,job):
    paths={k:contained(project,job[k]) for k in ['start_keyframe','end_keyframe']}
    if any(not p.is_file() for p in paths.values()):raise ValueError('Missing real keyframe files')
    script=project/'script/candidate.json';master=project/'references/master-spec.json'
    if job['script_sha256']!=sha(script) or job['master_sha256']!=sha(master):raise ValueError('Stale task upstream hash')
    index=read(project/'keyframes/index.json')
    for pos,k in [('start','start_keyframe'),('end','end_keyframe')]:
        f=next((f for f in index['frames'] if f['shot_id']==job['shot_id'] and f['position']==pos),None)
        if not f or f.get('png_sha256')!=sha(paths[k]):raise ValueError('Untracked or modified input image')
        if f['script_sha256']!=sha(script) or f['master_sha256']!=sha(master):raise ValueError('Stale input provenance')
        if f['task_sha256']!=sha(project/'tasks/keyframes.json') or f['renderer_sha256']!=sha(ROOT/'scripts/render_keyframes.py'):raise ValueError('Regenerate inputs after task/renderer edits')
    return paths

def require_approval(project,job,inputs,approval_path):
    if approval_path is None:raise ValueError('Production requires explicit professional approval file; use --preview for draft tests')
    a=read(approval_path)
    if a.get('status')!='APPROVED' or not isinstance(a.get('reviewer'),str) or not a['reviewer'].strip():raise ValueError('Named APPROVED reviewer required')
    datetime.fromisoformat(a['reviewed_at'].replace('Z','+00:00'))
    if a.get('script_sha256')!=job['script_sha256'] or a.get('master_sha256')!=job['master_sha256']:raise ValueError('Approval invalidated by upstream edit')
    frames=a.get('frames',{}).get(job['shot_id'],{})
    for pos,k in [('start','start_keyframe'),('end','end_keyframe')]:
        if frames.get(pos)!=sha(inputs[k]):raise ValueError('Keyframe approval missing or stale')

def measure(path):
    r=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,nb_read_frames:format=duration','-of','json',str(path)],capture_output=True,text=True,check=True)
    return json.loads(r.stdout)

def verify_measurement(m,params):
    s=m['streams'][0];expected=round(params['duration_seconds']*params['fps'])
    if (s['width'],s['height'])!=(params['width'],params['height']) or int(s['nb_read_frames'])!=expected:raise ValueError('Unexpected encoded geometry/frame count')
    n,d=map(int,s['avg_frame_rate'].split('/'))
    if abs(n/d-params['fps'])>1e-6 or abs(float(m['format']['duration'])-params['duration_seconds'])>1/params['fps']:raise ValueError('Unexpected video timing')

def encode(job,inputs,params,target,project):
    from PIL import Image, ImageChops
    size=(params['width'],params['height']);fps=params['fps'];n=round(params['duration_seconds']*fps)
    start=Image.open(inputs['start_keyframe']).convert('RGB');end=Image.open(inputs['end_keyframe']).convert('RGB')
    if start.size!=end.size:raise ValueError('Keyframe sizes differ')
    draw=None
    if params['backend']=='diagram-flow':
        # Directly generated layers are allowed only if both anchors equal the real inputs.
        from render_keyframes import draw_master
        spec=read(project/'references/master-spec.json');draw=lambda t:draw_master(spec,job['focus'],t,True).image
        for image,t in [(start,0),(end,1)]:
            if ImageChops.difference(image,draw(t)).getbbox():raise ValueError('Diagram backend does not bind to supplied anchors')
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
    # Encoder errors go to disk, avoiding a stderr pipe deadlock on streamed frames.
    log=target.with_suffix('.log')
    with log.open('wb') as err:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err)
        try:
            for i in range(n):
                t=i/(n-1)
                if draw:im=draw(t)
                else:
                    # Gentle 4% pan/zoom of one image; this backend does not promise end-anchor matching.
                    w,h=start.size;factor=1+.04*t;cw=int(w/factor);ch=int(h/factor)
                    im=start.crop(((w-cw)//2,(h-ch)//2,(w+cw)//2,(h+ch)//2))
                im=im.resize(size,Image.Resampling.LANCZOS);proc.stdin.write(im.tobytes())
            proc.stdin.close()
            if proc.wait()!=0:raise RuntimeError('ffmpeg failed; see local encoder log')
        except BaseException:
            if proc.poll() is None:proc.kill();proc.wait()
            raise
    log.unlink(missing_ok=True)
    return cmd

def run(project,shot_id,backend='diagram-flow',execute=False,preview=False,approval=None,width=960,fps=24):
    if width<320 or width>3840 or width%32 or fps not in [12,24,30]:raise ValueError('Use width 320..3840 divisible by 32 and fps 12/24/30')
    project=project.resolve();jobs=read(project/'tasks/keyframes.json')['jobs']
    job=next((j for j in jobs if j['shot_id']==shot_id),None)
    if job is None:raise ValueError('Shot has no keyframe task')
    inputs=validate_inputs(project,job)
    if execute and not preview:require_approval(project,job,inputs,approval)
    params={'backend':backend,'width':width,'height':width*9//16,'fps':fps,'duration_seconds':job['duration_seconds'],'seed':job['seed'],'preview':preview,'camera':job['camera'],'focus':job['focus']}
    payload={'shot_id':shot_id,'parameters':params,'input_sha256':{k:sha(v) for k,v in inputs.items()},'script_sha256':job['script_sha256'],'master_sha256':job['master_sha256'],'task_sha256':sha(project/'tasks/keyframes.json'),'runner_sha256':sha(Path(__file__)),'renderer_sha256':sha(ROOT/'scripts/render_keyframes.py')}
    ident=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:20]
    bucket=project/('tmp/preview-clips' if preview else 'clips')/shot_id/ident
    if not execute:
        path=project/'tmp/dry-runs'/f'{shot_id}-{ident}.json';path.parent.mkdir(parents=True,exist_ok=True)
        atomic_json(path,{**payload,'state':'DRY_RUN','job_id':ident,'capabilities':probe(),'output':str((bucket/'clip.mp4').relative_to(project)),'production_gate':'PROFESSIONAL_APPROVAL_REQUIRED','anchor_policy':'first and last exact composition' if backend=='diagram-flow' else 'first image only; end image not bound'})
        return {'state':'DRY_RUN','path':str(path),'job_id':ident}
    if not probe()[backend]['available']:raise ValueError('Local backend unavailable: install approved small tools Pillow/FFmpeg; no model required')
    bucket.mkdir(parents=True,exist_ok=True);manifest=bucket/'run.json';output=bucket/'clip.mp4';lock=bucket/'RUNNING.lock'
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.close(fd)
    try:
        if manifest.exists() and output.exists():
            old=read(manifest)
            if old.get('state')=='COMPLETED' and old.get('output_sha256')==sha(output):
                verify_measurement(measure(output),params)
                return {'state':'REUSED','output':str(output),'job_id':ident}
        partial=bucket/'clip.partial.mp4'
        state={**payload,'job_id':ident,'state':'RUNNING','started_at':datetime.now(timezone.utc).isoformat(),'output':'clip.mp4','anchor_policy':'first/last composition' if backend=='diagram-flow' else 'start only; no end anchor'}
        atomic_json(manifest,state)
        try:
            cmd=encode(job,inputs,params,partial,project);m=measure(partial);verify_measurement(m,params)
            os.replace(partial,output);state.update(state='COMPLETED',output_sha256=sha(output),measurement=m,encoder_command=cmd,approval_sha256=sha(approval) if approval and not preview else None,qa_status='DRAFT_PREVIEW' if preview else 'AWAITING_CLIP_REVIEW')
            atomic_json(manifest,state)
        except BaseException as exc:
            state.update(state='FAILED',error=type(exc).__name__+': '+str(exc));atomic_json(manifest,state);partial.unlink(missing_ok=True);raise
        return {'state':'COMPLETED','output':str(output),'job_id':ident}
    finally:lock.unlink(missing_ok=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,default=DEFAULT_PROJECT);p.add_argument('--shot',default='SH009');p.add_argument('--backend',choices=['diagram-flow','still-pan'],default='diagram-flow');p.add_argument('--execute',action='store_true');p.add_argument('--preview',action='store_true');p.add_argument('--approval',type=Path);p.add_argument('--width',type=int,default=960);p.add_argument('--fps',type=int,default=24);p.add_argument('--probe',action='store_true');a=p.parse_args()
    try:print(json.dumps(probe() if a.probe else run(a.project,a.shot,a.backend,a.execute,a.preview,a.approval,a.width,a.fps),ensure_ascii=False,indent=2))
    except (ValueError,OSError,KeyError,subprocess.SubprocessError) as e:print('BLOCKED:',str(e),file=sys.stderr);sys.exit(1)
