#!/usr/bin/env python3
"""Real populated pilot invariants, independent of engineering approval."""
import argparse,json,hashlib,sys
from pathlib import Path
try:
    from scripts.import_csu import seconds
    from scripts.validate_project import validate
except ModuleNotFoundError:
    from import_csu import seconds
    from validate_project import validate
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(p):
    data=json.loads((p/'script/candidate.json').read_text(encoding='utf-8'));errors=validate(data)
    shots=data['shots'];cursor=0
    if len(shots)!=26 or data.get('total_seconds')!=158:errors.append('Expected populated 26 shots / 158s')
    ev=json.loads((p/'references/evidence.json').read_text(encoding='utf-8'));known={s['id'] for s in ev['sources']}|{'EDITORIAL'}
    for i,s in enumerate(shots,1):
        if s['shot_id']!=f'SH{i:03d}' or s['duration_seconds']!=(8 if i==26 else 6):errors.append('Invalid ID/duration')
        if seconds(s['start'])!=cursor or seconds(s['end'])-cursor!=s['duration_seconds']:errors.append('Timeline gap/overlap')
        cursor=seconds(s['end'])
        if i<26 and not s['narration'].strip():errors.append('Missing narration')
        if not s.get('visual_prompt') or not s.get('review_note'):errors.append('Blank production/review record')
        if not s.get('evidence_ids') or set(s['evidence_ids'])-known:errors.append('Unknown evidence')
    if cursor!=158:errors.append('Final cut must be 158s')
    jobs=json.loads((p/'tasks/keyframes.json').read_text(encoding='utf-8'))['jobs']
    if [j['shot_id'] for j in jobs]!=['SH003','SH007','SH008','SH009','SH010','SH011']:errors.append('First batch mismatch')
    for j in jobs:
        if j['script_sha256']!=sha(p/'script/candidate.json') or j['master_sha256']!=sha(p/'references/master-spec.json'):errors.append('Stale keyframe tasks')
        if any(not j.get(k) for k in ['start_state','end_state','start_keyframe','end_keyframe','camera','negative_constraints']):errors.append('Incomplete keyframe task')
    source=p/'source/shot-plan.json'
    if source.exists() and json.loads(source.read_text(encoding='utf-8'))['source_sha256']!=data['source_sha256']:errors.append('Wrong original source')
    reviews=json.loads((p/'reviews/script-review.json').read_text(encoding='utf-8'))['shots']
    if [r['shot_id'] for r in reviews]!=[s['shot_id'] for s in shots]:errors.append('Review coverage missing')
    return errors
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,default=ROOT/'projects/csu-condenser-158s');a=p.parse_args()
    try:
        errors=check(a.project)
        print('\n'.join(errors) if errors else 'PASS: actual 26-shot candidate, evidence IDs, 158s timeline, six hashed jobs; no professional approval implied');sys.exit(bool(errors))
    except (OSError,ValueError,KeyError) as e:print('FAIL:',e);sys.exit(1)
