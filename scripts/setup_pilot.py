#!/usr/bin/env python3
"""Cross-platform control-folder bootstrap; source clones only, no third-party execution."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROLES=['industrial-script-auditor','shot-planner','industrial-keyframe-director','visual-continuity-inspector','image-to-video-director','clip-quality-inspector']
def git(*args):return subprocess.run(['git',*map(str,args)],check=True,capture_output=True,text=True).stdout.strip()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def doctor(root):
    failures=[]
    for name in ROLES:
        path=root/'.agents/skills'/name/'SKILL.md'
        if not path.is_file():failures.append(f'Missing skill: {name}');continue
        content=path.read_text(encoding='utf-8')
        if not content.startswith('---\n') or '\nname: '+name+'\n' not in content or '\ndescription: ' not in content:failures.append(f'Invalid discovery metadata: {name}')
    if failures:raise ValueError('; '.join(failures))
    return {'skills':ROLES,'discovery':'repository .agents/skills with name/description frontmatter','codex_runtime':'not invoked; restart existing Codex session if skills were added'}
def setup(root,with_upstreams=False,install_storyboard=False):
    root=root.resolve();doctor(root)
    project=root/'projects/csu-condenser-158s'
    for name in ['source','script','keyframes','clips','reviews','exports','references','tmp','tasks']:(project/name).mkdir(parents=True,exist_ok=True)
    registry=json.loads((root/'registry/approved-skills.json').read_text(encoding='utf-8'))['upstreams']
    if with_upstreams or install_storyboard:
        if not shutil.which('git'):raise ValueError('Git required for approved source checkout')
        for entry in registry:
            name=entry['repository'].rstrip('/').split('/')[-1];dest=root/'.upstreams'/name
            if not dest.exists():
                dest.parent.mkdir(exist_ok=True);git('clone','--no-checkout',entry['repository']+'.git',dest)
            remote=git('-C',dest,'remote','get-url','origin').removesuffix('.git').rstrip('/')
            if remote!=entry['repository']:raise ValueError('Unexpected upstream remote: '+name)
            if git('-C',dest,'status','--porcelain','--untracked-files=no'):raise ValueError('Upstream has local tracked edits; refuse checkout: '+name)
            git('-C',dest,'fetch','--depth','1','origin',entry['revision'])
            git('-C',dest,'checkout','--detach',entry['revision'])
            if git('-C',dest,'rev-parse','HEAD')!=entry['revision']:raise ValueError('Upstream pin mismatch')
            if not (dest/entry['entry']).is_file():raise ValueError('Upstream entry missing')
            if entry['name']=='create-storyboard' and not (dest/'LICENSE').read_text(encoding='utf-8').startswith('MIT License'):raise ValueError('Unexpected source license')
    if install_storyboard:
        entry=registry[0];repo=root/'.upstreams/create-storyboard-skill';src=repo/'skills/create-storyboard';dest=root/'.agents/skills/create-storyboard'
        expected={str(p.relative_to(src)):digest(p) for p in src.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
        expected['LICENSE']=digest(repo/'LICENSE')
        if dest.exists():
            for name,h in expected.items():
                if not (dest/name).is_file() or digest(dest/name)!=h:raise ValueError('Installed storyboard differs; preserve edits and use a clean destination')
        else:
            shutil.copytree(src,dest,ignore=shutil.ignore_patterns('__pycache__'));shutil.copy2(repo/'LICENSE',dest/'LICENSE')
        (dest/'installation-provenance.json').write_text(json.dumps({'source':entry['repository'],'revision':entry['revision'],'license':'MIT','files_sha256':expected},indent=2)+'\n',encoding='utf-8')
    return {'project':str(project),'doctor':doctor(root),'upstreams_checked':bool(with_upstreams or install_storyboard),'storyboard_discoverable_install':install_storyboard,'external_code_executed':False}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--with-upstreams',action='store_true');p.add_argument('--install-storyboard',action='store_true');p.add_argument('--doctor',action='store_true');a=p.parse_args()
    try:print(json.dumps(doctor(a.root.resolve()) if a.doctor else setup(a.root,a.with_upstreams,a.install_storyboard),indent=2))
    except (ValueError,OSError,subprocess.SubprocessError) as e:print('SETUP FAILED:',str(e),file=sys.stderr);sys.exit(1)
