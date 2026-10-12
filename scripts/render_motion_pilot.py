#!/usr/bin/env python3
"""Fixed-raster, deterministic 18s trial; never promotes production approval.
Requires Pillow, ffmpeg, ffprobe, a user-scoped trial permit and supplied CJK font.
"""
import argparse, hashlib, json, math, shutil, subprocess
from pathlib import Path
IDS = ('SH009','SH010','SH011')
FPS = 24
SIZE = (1920,1080)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arrow(d, a, b, color, width=3):
    d.line([a,b],fill=color,width=width)
    vx,vy=b[0]-a[0],b[1]-a[1]; n=math.hypot(vx,vy); ux,uy=vx/n,vy/n
    d.polygon([b,(b[0]-ux*12-uy*6,b[1]-uy*12+ux*6),(b[0]-ux*12+uy*6,b[1]-uy*12-ux*6)],fill=color)
def smooth_path(points, n=50):
    a,b,c=points
    return [((1-u)**2*a[0]+2*(1-u)*u*b[0]+u*u*c[0],(1-u)**2*a[1]+2*(1-u)*u*b[1]+u*u*c[1]) for u in [i/n for i in range(n+1)]]
def frame(base, idx, t, narration, font):
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    im=base.copy(); layer=Image.new('RGBA',im.size); d=ImageDraw.Draw(layer)
    # Source-space coordinates: no camera transform, no structural deformation.
    if idx==0:
        for y in (291,440,586):
            for j in range(4):
                x=780+(t*120+j*250)%840
                d.line([(max(775,x-60),y),(x,y)],fill=(178,242,255,125),width=4)
                arrow(d,(x-18,y),(x+9,y),(224,252,255,225),3)
    elif idx==1:
        # Explicit heat-flow symbols, not fluid paths or mixing through the wall.
        for j,x in enumerate((790,1080,1380)):
            wall=218+(x-790)*.063
            alpha=int(145+50*math.sin(t*2.4+j))
            arrow(d,(x,wall-95),(x,wall+80),(210,84,66,alpha),4)
            phase=(t*.6+j*.33)%1
            yy=wall-90+phase*158
            d.ellipse((x-5,yy-5,x+5,yy+5),fill=(245,126,92,230))
    else:
        # Continuous, restrained exterior film. Geometry remains static underneath.
        upper=[(x,190+(x-510)*.071) for x in range(510,1670,8)]
        lower=[(x,656-(x-490)*.071) for x in range(490,1670,8)]
        d.line(upper, fill=(202,149,51,65),width=6)
        d.line(lower, fill=(202,145,36,95),width=8)
        # Surface rivulets remain on exposed lower tube exterior, never in blue lumen.
        for j,x in enumerate((600,770,945,1120,1320,1510)):
            start=557-(x-600)*.04; end=656-(x-490)*.071
            pts=smooth_path(((x,start),(x+17,(start+end)/2),(x+27,end)))
            d.line(pts,fill=(210,159,65,22),width=15)
            u=(t*.38+j*.17)%1; k=int(u*40)
            d.line(pts[k:k+9],fill=(246,207,126,155),width=3)
        # Restrained gravity discharge at two actual lower-edge collection points.
        for j,(x,y) in enumerate(((667,651),(1172,618))):
            phase=(t*.62+j*.46)%1
            if phase<.42:
                r=2+phase*10
                d.ellipse((x-r,y,x+r,y+r*2),fill=(210,150,42,195))
            else:
                u=(phase-.42)/.58; yy=y+12+92*u*u
                d.ellipse((x-4,yy-6,x+4,yy+6),fill=(215,157,51,int(210*(1-u*.7))))
    im=Image.alpha_composite(im.convert('RGBA'),layer)
    # Independent typesetting in the reserved white band, never AI-generated text.
    d=ImageDraw.Draw(im)
    names=('管内冷却水流动','管外蒸汽向管壁放热','管外液膜连续汇流')
    small=ImageFont.truetype(str(font),21); main=ImageFont.truetype(str(font),33)
    d.rounded_rectangle((42,30,390,85),radius=12,fill=(255,255,255,225))
    d.text((60,40),IDS[idx]+'  ·  '+names[idx],font=small,fill=(35,63,80))
    if idx==1:
        d.text((1110,64),'红色箭头仅表示热流',font=small,fill=(161,67,53))
    if idx==2:
        d.text((1110,64),'金色为液膜示踪色',font=small,fill=(145,103,32))
    # Keep source imagery in full view; no crop or anisotropic stretch.
    im=ImageOps.contain(im.convert('RGB'),SIZE,Image.Resampling.LANCZOS)
    out=Image.new('RGB',SIZE,'white'); out.paste(im,((SIZE[0]-im.width)//2,(SIZE[1]-im.height)//2))
    d=ImageDraw.Draw(out); f=ImageFont.truetype(str(font),38)
    bb=d.textbbox((0,0),narration,font=f); w=bb[2]-bb[0]
    d.text(((1920-w)/2,975),narration,font=f,fill=(27,56,72))
    return out

def authorized_inputs(project):
    script=project/'script/candidate.json'; permit=project/'motion/pilot01/permit.json'
    permit_data=json.loads(permit.read_text()); shots={s['shot_id']:s for s in json.loads(script.read_text())['shots']}
    inputs={s:project/'film-keyframes/batch01-v1'/f'{s}_keyframe.png' for s in ('SH003','SH007','SH008')+IDS}
    hashes={s:sha(f) for s,f in inputs.items()}
    if permit_data['scope']!=list(IDS) or permit_data['status']!='CONDITIONAL_TRIAL_ONLY': raise ValueError('Trial scope mismatch')
    if permit_data['source_sha256']!=sha(script) or permit_data['keyframe_sha256']!=hashes: raise ValueError('Stale permit: script/image changed')
    if any(shots[s]['duration_seconds']!=6 for s in IDS): raise ValueError('Reviewed timing changed')
    return script, permit, shots, inputs, hashes

def main():
    from PIL import Image, ImageDraw, ImageFilter
    p=argparse.ArgumentParser(); p.add_argument('--project',type=Path,default=Path('projects/csu-condenser-158s')); p.add_argument('--out',type=Path,required=True); p.add_argument('--font',type=Path,required=True); p.add_argument('--execute',action='store_true'); a=p.parse_args()
    script, permit, shots, inputs, hashes = authorized_inputs(a.project)
    if not a.font.is_file(): raise ValueError('Supply a locally installed CJK font')
    identity={'backend':'fixed-raster-film-v1','script_sha256':sha(script),'permit_sha256':sha(permit),'renderer_sha256':sha(__file__),'inputs':hashes,'font_sha256':sha(a.font),'fps':FPS,'size':SIZE}
    key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    a.out.mkdir(parents=True,exist_ok=True); video=a.out/'SH009-SH011_18s.mp4'; run=a.out/'run.json'
    if run.exists():
        old=json.loads(run.read_text())
        if old.get('render_key')==key and video.exists() and old.get('video_sha256')==sha(video): print('REUSED verified render'); return
    if video.exists() and a.execute: raise ValueError('Different existing render: choose a new output directory to preserve history')
    if not a.execute: print(json.dumps({'status':'DRY_RUN','render_key':key,**identity},ensure_ascii=False,indent=2)); return
    for tool in ('ffmpeg','ffprobe'):
        if not shutil.which(tool): raise ValueError(f'Missing {tool}')
    partial=a.out/'render.partial.mp4'
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(partial)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for idx,s in enumerate(IDS):
            base=Image.open(inputs[s]).convert('RGB')
            # Local animation-only correction: remove baked hanging drops with a
            # feathered patch from matching SH010 background; original PNG stays intact.
            if s=='SH011':
                clean=Image.open(inputs['SH010']).convert('RGB').resize(base.size)
                mask=Image.new('L',base.size); md=ImageDraw.Draw(mask)
                md.rectangle((643,670,690,741),fill=255); md.rectangle((1151,638,1194,698),fill=255)
                mask=mask.filter(ImageFilter.GaussianBlur(6)); base=Image.composite(clean,base,mask)
            for i in range(FPS*6):
                fr=frame(base,idx,i/FPS,shots[s]['narration'],a.font)
                if i in (0,72,143): fr.save(a.out/f'{s}_{i:03d}.png')
                proc.stdin.write(fr.tobytes())
            print(s,'rendered',flush=True)
        proc.stdin.close()
        if proc.wait()!=0: raise RuntimeError('ffmpeg failed')
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(partial)]))
        st=probe['streams'][0]
        if abs(float(probe['format']['duration'])-18)>0.001 or int(st['nb_frames'])!=432: raise ValueError('Encoded timing mismatch')
        partial.replace(video)
        if hashes!={s:sha(f) for s,f in inputs.items()}: raise ValueError('Inputs mutated')
        result={'status':'ENCODED_AWAITING_HUMAN_REVIEW','render_key':key,**identity,'video_sha256':sha(video),'probe':probe,'paid_inference_calls':0,'audio':'NONE','mapping':[{'shot_id':s,'sample_start':i*6,'sample_end':(i+1)*6,'film_start':48+i*6,'film_end':54+i*6,'narration':shots[s]['narration']} for i,s in enumerate(IDS)]}
        run.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        (a.out/'narration.srt').write_text(''.join(f'{i+1}\n00:00:{i*6:02d},000 --> 00:00:{(i+1)*6:02d},000\n{shots[s]["narration"]}\n\n' for i,s in enumerate(IDS)))
        print('ENCODED',video,sha(video))
    except BaseException:
        if proc.poll() is None: proc.kill(); proc.wait()
        raise
if __name__=='__main__': main()
