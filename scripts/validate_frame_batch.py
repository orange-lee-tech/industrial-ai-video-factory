#!/usr/bin/env python3
"""Validate real PNG/provenance transport only, never factual or visual quality."""
import argparse,hashlib,json,struct,sys
from pathlib import Path
EXPECTED=['SH003','SH007','SH008','SH009','SH010','SH011']
def check(batch):
    index=json.loads((batch/'batch-manifest.json').read_text(encoding='utf-8'));errors=[]
    if [x['shot_id'] for x in index['items']]!=EXPECTED:errors.append('Unexpected first-batch IDs/order')
    for x in index['items']:
        sid=x['shot_id'];rel=x['file'];path=(batch/rel).resolve()
        if not path.is_relative_to(batch.resolve()) or Path(rel).name!=sid+'_keyframe.png':errors.append(sid+' invalid path');continue
        if not path.is_file():errors.append(sid+' missing PNG');continue
        data=path.read_bytes()
        if data[:8]!=b'\x89PNG\r\n\x1a\n' or data[12:16]!=b'IHDR':errors.append(sid+' invalid PNG');continue
        w,h=struct.unpack('>II',data[16:24])
        if [w,h]!=[x['width'],x['height']] or abs(h-w*9/16)>(1+9/16):errors.append(sid+' wrong size/aspect ratio')
        if hashlib.sha256(data).hexdigest()!=x['file_sha256']:errors.append(sid+' wrong PNG hash')
        for suffix in ['brief.md','prompt.txt','provenance.json']:
            if not (batch/(sid+'_'+suffix)).is_file():errors.append(sid+' missing '+suffix)
        prov=json.loads((batch/(sid+'_provenance.json')).read_text(encoding='utf-8'))
        if prov!=x:errors.append(sid+' mismatched provenance/index')
        if hashlib.sha256((batch/(sid+'_prompt.txt')).read_bytes()).hexdigest()!=x['generation']['final_prompt_sha256']:errors.append(sid+' changed prompt')
        if x['production_state'] in ['APPROVED','MOTION_READY']:
            for field in ['human_fact_review','human_art_review']:
                review=x[field]
                if review['status']!='APPROVED' or not review.get('reviewer'):errors.append(sid+' missing named dual approval')
    return errors
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('batch',type=Path);a=p.parse_args()
    try:
        errors=check(a.batch)
        print('\n'.join(errors) if errors else 'PASS: six real PNG hashes, near-16:9 native dimensions and per-shot evidence files; NATIVE SIZE NOT 1920x1080; HUMAN FACT/ART APPROVAL STILL REQUIRED')
        sys.exit(bool(errors))
    except (OSError,ValueError,KeyError,struct.error) as e:print('FAIL:',e);sys.exit(1)
