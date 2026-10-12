#!/usr/bin/env python3
"""Raster-layer motion rework. Explicit fluid advection independent of camera.
No model/API. Original PNGs immutable. Pillow + NumPy + SciPy; FFmpeg encoding.
"""
import argparse, hashlib, json, math, subprocess, shutil
from pathlib import Path
IDS=('SH009','SH010','SH011'); FPS=24; W,H=1672,820; OUTPUT=(1920,1080)
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def smooth(u):
    u=max(0,min(1,u)); return u*u*(3-2*u)
def load_inputs(project):
    permit=project/'motion/pilot02/permit.json'; script=project/'script/candidate.json'
    data=json.loads(permit.read_text(encoding='utf-8'))
    shots={s['shot_id']:s for s in json.loads(script.read_text(encoding='utf-8'))['shots']}
    inputs={s:project/'film-keyframes/batch01-v1'/f'{s}_keyframe.png' for s in ('SH003','SH007','SH008')+IDS}
    hashes={s:digest(f) for s,f in inputs.items()}
    if data['status']!='REWORK_TRIAL_ONLY' or data['scope']!=list(IDS): raise ValueError('Out of rework scope')
    if data['source_sha256']!=digest(script) or data['keyframe_sha256']!=hashes: raise ValueError('Stale rework permit')
    if any(shots[s]['duration_seconds']!=6 for s in IDS): raise ValueError('Reviewed timing changed')
    return shots,inputs,hashes,permit,script

def poly(points):
    from PIL import Image,ImageDraw
    import numpy as np
    m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(points,fill=255)
    return np.asarray(m,dtype=float)/255

def bezier(a,b,c,d,n=160):
    import numpy as np
    u=np.linspace(0,1,n)[:,None]
    q=(1-u)**3*a+3*(1-u)**2*u*b+3*(1-u)*u*u*c+u**3*d
    dist=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(q,axis=0),axis=1))]);return q,dist

class LayerScene:
    def __init__(self,inputs):
        import numpy as np
        from PIL import Image,ImageDraw,ImageFilter
        from scipy.ndimage import gaussian_filter,binary_fill_holes,binary_erosion
        self.np=np;self.Image=Image;self.Draw=ImageDraw
        self.base={s:np.asarray(Image.open(inputs[s]).convert('RGB').resize((W,941),Image.Resampling.LANCZOS))[:H].astype(np.float32) for s in IDS}
        self.y,self.x=np.mgrid[:H,:W].astype(np.float32)
        # Geometric bounds stay clear of tube wall and hardware. Hue is an extra guard.
        b=self.base['SH009'];blue=(b[:,:,2]>b[:,:,0]+28)&(b[:,:,1]>b[:,:,0]+12)
        rows=[]
        for yy in (292,442,588):
            p=poly([(773,yy-26),(1671,yy-26),(1671,yy+29),(773,yy+29)])
            r=binary_fill_holes(blue&(p>.5));r=binary_erosion(r,iterations=1);rows.append(gaussian_filter(r.astype(float),.65)*p)
        chamber=poly([(326,210),(558,209),(572,692),(332,698)])*blue
        inlet=poly([(0,388),(166,388),(166,538),(0,538)])*blue
        self.water09=np.maximum.reduce(rows+[gaussian_filter(chamber,.7),gaussian_filter(inlet,.7)])
        b=self.base['SH010'];blue=(b[:,:,2]>b[:,:,0]+28)&(b[:,:,1]>b[:,:,0]+12)
        window=poly([(546,329),(1671,360),(1671,495),(542,520)])
        # Front lumen's blue-hue segmentation preserves the silver annular section.
        front=poly([(240,220),(490,220),(490,620),(240,620)])
        self.water10=gaussian_filter((blue&(np.maximum(window,front)>.5)).astype(float),.6)*np.maximum(window,front)
        # Tiles are sampled from accepted blue water art; joining mirrored ends avoids jumps.
        def tile(crop):
            a=np.asarray(crop,dtype=np.float32);a=np.concatenate([a,a[::-1]],axis=0);return np.concatenate([a,a[:,::-1]],axis=1)
        src=self.Image.fromarray(self.base['SH009'].astype('uint8'))
        self.tex09=tile(src.crop((810,269,1560,320)))
        self.tex_chamber=tile(src.crop((380,226,532,673)))
        src=self.Image.fromarray(self.base['SH010'].astype('uint8'))
        self.tex10=tile(src.crop((720,365,1450,489)))
        self.tex_steam=tile(src.crop((630,0,1650,185)))
        # A glossy real condensate droplet sprite from approved SH011, no flat gold ellipses.
        drop=np.asarray(self.Image.fromarray(self.base['SH011'].astype('uint8')).crop((646,678,692,738))).astype(float)
        da=binary_fill_holes((drop[:,:,0]>drop[:,:,2]+25)&(drop[:,:,1]>drop[:,:,2]+15))
        da=gaussian_filter(da.astype(float),.65)
        rgba=np.dstack([drop,(da*255)]).astype('uint8');self.drop_sprite=self.Image.fromarray(rgba)
        self.upper=190+(self.x-480)*.072
        self.wallcut=303+(self.x-520)*.041
        self.lowercut=544-(self.x-520)*.035
        self.bottom=659-(self.x-480)*.066
        longitudinal=(self.x>=545)&(self.x<1670)
        self.upperwall=longitudinal&(self.y>self.upper+3)&(self.y<self.wallcut-4)
        self.lowerwall=longitudinal&(self.y>self.lowercut+5)&(self.y<self.bottom-2)
        # Positive separation from coolant, including antialiasing guard pixels.
        self.metal=(self.upperwall|self.lowerwall).astype(float)*(self.water10<.001)
        self.vapor=poly([(580,0),(1672,0),(1672,278),(580,184)])
        self.vapor*=np.clip((self.upper-self.y-6)/16,0,1)
        self.vapor*=np.clip((self.x-580)/60,0,1)
        self.vapor=gaussian_filter(self.vapor,1.4)
        rng=np.random.default_rng(20511); noise=rng.normal(size=(160,500))
        noise=gaussian_filter(noise,5);noise=(noise-noise.min())/(noise.max()-noise.min())
        self.cloud=np.array(self.Image.fromarray((noise*255).astype('uint8')).resize((750,260)),dtype=float)/255
        self.cloud=np.concatenate([self.cloud,self.cloud[:,::-1]],axis=1)
        # Streamlines: inlet -> chamber branches -> tubes; mask hides passage behind tubesheet.
        self.paths=[]
        for yy in (292,442,588):
            q,d=bezier(np.array([18,455]),np.array([410,455]),np.array([395,yy]),np.array([770,yy]))
            tail=np.column_stack([np.linspace(770,1740,120),np.full(120,yy)])
            q=np.vstack([q,tail[1:]]);d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(q,axis=0),axis=1))]
            self.paths.append((q,d))
        self.sprite_cache={}
        # Quantitative inspection ROIs, source-space (no camera).
        self.rois={'SH009_water':(850,274,1520,316),'SH010_water':(730,380,1490,478),'SH011_water':(730,380,1490,478),'SH010_vapor':(850,35,1450,180),'SH011_vapor':(850,35,1450,180),'SH011_film':(650,558,1490,620),'SH009_structure':(595,180,668,705),'SH010_structure':(220,360,242,500),'SH011_structure':(220,360,242,500),'SH009_background':(30,30,160,100),'SH010_background':(30,30,160,100),'SH011_background':(30,30,160,100)}
    def advect(self,tex,t,macro=False):
        np=self.np
        # Shift to the RIGHT: output(x,t)=texture(x-vt,y). No sine-only shimmer.
        speed=210 if macro else 245
        xx=(self.x-speed*t).astype(np.float32)
        yy=self.y+(3*np.sin(self.x/115-t*2.3))
        if macro: yy=(yy-235)/370*(tex.shape[0]/2-1)
        else: yy=(yy-267)*.9
        ix=np.floor(xx).astype(int)%tex.shape[1]; iy=np.floor(yy).astype(int)%tex.shape[0]
        fx=(xx-np.floor(xx))[...,None];fy=(yy-np.floor(yy))[...,None]
        a=tex[iy,ix]*(1-fx)+tex[iy,(ix+1)%tex.shape[1]]*fx
        b=tex[(iy+1)%tex.shape[0],ix]*(1-fx)+tex[(iy+1)%tex.shape[0],(ix+1)%tex.shape[1]]*fx
        return a*(1-fy)+b*fy
    def sprite(self,r):
        import numpy as np
        from PIL import Image
        if r not in self.sprite_cache:
            y,x=np.mgrid[-1:1:complex(r),-1:1:complex(r*2)]
            a=np.exp(-3*(x*x+y*y))*(.7+.3*np.cos(x*12+y*8))
            ar=np.zeros((r,r*2,4),dtype=np.uint8); ar[:,:,:3]=[220,247,251];ar[:,:,3]=(a*125).astype('uint8')
            self.sprite_cache[r]=Image.fromarray(ar)
        return self.sprite_cache[r]
    def water_scene(self,t):
        np=self.np; out=self.base['SH009'].copy()
        fluid=self.advect(self.tex09,t)
        # Chamber texture has a slower curved circulation before split. Mostly continuous material motion.
        chamber_region=(self.x>326)&(self.x<572)&(self.y>210)&(self.y<700)
        chamber=self.advect(self.tex_chamber,t*.65)
        fluid=np.where(chamber_region[:,:,None],chamber,fluid)
        alpha=self.water09[:,:,None]*.94;out=out*(1-alpha)+fluid*alpha
        layer=self.Image.new('RGBA',(W,H));d=self.Draw.Draw(layer)
        for q,dist in self.paths:
            for j in range(15):
                s=(t*270+j*128)%dist[-1]
                seg=q[(dist>=s-42)&(dist<=s)]
                if len(seg)>1:d.line([tuple(a) for a in seg],fill=(225,251,255,100),width=2)
        rgba=np.asarray(layer).astype(float);alpha=rgba[:,:,3]/255*self.water09
        out=out*(1-alpha[:,:,None])+rgba[:,:,:3]*alpha[:,:,None]
        return np.clip(out,0,255).astype('uint8'), {'film_coverage':0,'water_velocity_px_s':245}
    def macro_scene(self,t,film_age=None):
        np=self.np; out=self.base['SH010'].copy()
        fluid=self.advect(self.tex10,t,True)
        a=self.water10[:,:,None]*.97;out=out*(1-a)+fluid*a
        # Steam density advects downward toward the surface, with slow tangential drift.
        ix=((self.x+25*t)%self.cloud.shape[1]).astype(int)
        iy=((self.y-55*t)%self.cloud.shape[0]).astype(int)
        noise=self.cloud[iy,ix]; vapor_alpha=self.vapor*(.09+.25*noise)
        sx=((self.x-630-22*t)%self.tex_steam.shape[1]).astype(int)
        sy=((self.y-55*t)%self.tex_steam.shape[0]).astype(int)
        cloudcolor=self.tex_steam[sy,sx]*.94+np.stack([178+noise*60,226+noise*27,239+noise*16],axis=2)*.06
        vapor_alpha=self.vapor*.82
        out=out*(1-vapor_alpha[:,:,None])+cloudcolor*vapor_alpha[:,:,None]
        mist=self.Image.new('RGBA',(W,H))
        for j in range(22):
            phase=(t*.30+j*.173)%1
            x=660+(j*137)%1000+26*phase
            wall=190+(x-480)*.072
            y=wall-195+phase*184
            r=60+((j*11)%35); spr=self.sprite(r)
            # Disappear at cold wall: vapor matter never travels into lumen.
            factor=math.sin(math.pi*phase)**.6
            if phase>.82:factor*=max(0,(1-phase)/.18)
            spr=spr.copy();spr.putalpha(spr.getchannel('A').point(lambda v:v*factor))
            mist.alpha_composite(spr,(int(x-r),int(y-r/2)))
        m=np.asarray(mist).astype(float);a=m[:,:,3]/255*self.vapor
        out=out*(1-a[:,:,None])+m[:,:,:3]*a[:,:,None]
        # Heat wavefronts cross only exposed metal, with a stable underlying structure.
        across=(self.y-self.upper)/(self.wallcut-self.upper)
        wave=(.5+.5*np.cos(across*math.pi*5-t*7-self.x*.006))**8
        heat=self.upperwall.astype(float)*wave*.17
        out=out*(1-heat[:,:,None])+np.array([255,160,91])*heat[:,:,None]
        heatlayer=self.Image.new('RGBA',(W,H)); d=self.Draw.Draw(heatlayer)
        for j,x in enumerate((810,1070,1340)):
            u=(t*.8+j*.3)%1; top=190+(x-480)*.072; cut=303+(x-520)*.041
            y=top-55+u*(cut-top+80)
            # Energy streak only, steam vapor mask is separate and ends outside metal.
            d.line([(x,y-22),(x,y+4)],fill=(232,129,77,165),width=5)
            d.polygon([(x,y+12),(x-7,y+1),(x+7,y+1)],fill=(227,120,68,165))
        h=np.asarray(heatlayer).astype(float);ha=h[:,:,3]/255
        out=out*(1-ha[:,:,None])+h[:,:,:3]*ha[:,:,None]
        coverage=0
        if film_age is not None:
            # Liquid coverage grows from contact zone; liquid and blue coolant masks are disjoint.
            growth=smooth(film_age/3.2)
            along=growth*np.ones_like(self.x)
            thickness=1.6+growth*9.5
            bottomdistance=np.abs(self.y-self.bottom)
            edge=np.exp(-(bottomdistance/thickness)**2)*((self.x>520)&(self.x<1670))
            surface=self.metal*(.10+.25*growth)*along
            surface*=.8+.2*np.sin(self.y*.1+self.x*.026-film_age*5)
            edge*=np.clip((self.bottom-self.y+3)/4,0,1)
            edge*=self.water10<.001
            filma=np.maximum(surface,edge*growth*.6)
            # Rich surface film derived from SH011 art, without its baked hanging drops.
            reference=self.base['SH011']; liquid=reference*.66+np.array([224,167,70])*.34
            out=out*(1-filma[:,:,None])+liquid*filma[:,:,None]
            # Continuous shaded film rivulets on exposed OUTSIDE lower surface.
            surface_u=np.clip((self.y-self.lowercut)/(self.bottom-self.lowercut),0,1)
            rivulet_alpha=np.zeros((H,W),dtype=float)
            for j,x in enumerate((615,790,970,1140,1330,1520)):
                center=x+14*surface_u**2
                stripe=np.exp(-((self.x-center)/(3+growth*3))**2)
                wave=.4+.6*(.5+.5*np.cos(surface_u*10-film_age*6-j))**3
                rivulet_alpha=np.maximum(rivulet_alpha,stripe*wave*growth*.45)
            rivulet_alpha*=self.lowerwall*(self.water10<.001)
            out=out*(1-rivulet_alpha[:,:,None])+np.array([241,195,103])*rivulet_alpha[:,:,None]
            # Moving reflective wavefronts on a continuous wetted exterior sheet.
            shine=(.5+.5*np.cos(surface_u*12-film_age*7-self.x*.018))**7
            sa=self.lowerwall*growth*shine*.19*(self.water10<.001)
            out=out*(1-sa[:,:,None])+np.array([255,224,165])*sa[:,:,None]
            # At the bottom surface, film collects, necks and then drains by gravity.
            drops=self.Image.new('RGBA',(W,H));d=self.Draw.Draw(drops)
            for j,x in enumerate((670,1170)):
                y=659-(x-480)*.066
                u=(film_age*.65+j*.43)%1
                if film_age>.8:
                    # Art-derived glossy liquid bulge at collection point.
                    spr=self.drop_sprite.resize((27,36),self.Image.Resampling.LANCZOS)
                    if u<.35:
                        factor=.45+.55*u/.35
                        spr=spr.resize((int(27*factor),int(36*factor)),self.Image.Resampling.LANCZOS)
                        yy=y+2
                    else:
                        yy=y+18+((u-.35)/.65)**2*128
                    drops.alpha_composite(spr,(int(x-spr.width/2),int(yy)))
            dr=np.asarray(drops).astype(float);da=dr[:,:,3]/255
            out=out*(1-da[:,:,None])+dr[:,:,:3]*da[:,:,None]
            coverage=float((filma>.08).sum())
        return np.clip(out,0,255).astype('uint8'), {'film_coverage_pixels':coverage,'film_age':film_age,'water_velocity_px_s':210,'steam_velocity_y_px_s':55}
    def scene(self,T):
        if T<6:return self.water_scene(T)
        # Same single-tube metal plate through 12s, not a SH010->SH011 image swap.
        return self.macro_scene(T-6,None if T<12 else T-12)
    def camera(self,T):
        # Intentional rigid camera, not uncontrolled background/metal drift.
        if T<6:
            u=smooth(T/6);return (1+.30*u,836+170*u,410+25*u)
        if T<7.1:
            u=smooth((T-6)/1.1);return (1.30+.9*u,1006-40*u,435)
        if T<12:
            u=smooth((T-7.1)/4.9);return (1.03+.09*u,866+25*u,405)
        u=smooth((T-12)/6);return (1.12-.07*u,891-12*u,405+8*u)
    def project(self,ar,cam):
        z,cx,cy=cam; cw=W/z;ch=H/z
        cx=max(cw/2,min(W-cw/2,cx));cy=max(ch/2,min(H-ch/2,cy))
        # One affine crop/resize for every world layer; no separate structure transform.
        return self.Image.fromarray(ar).transform((1920,942),self.Image.Transform.EXTENT,(cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2),self.Image.Resampling.BICUBIC)
    def output(self,T,narration,font,no_camera=False):
        from PIL import Image,ImageDraw,ImageFont
        ar,info=self.scene(T)
        if no_camera: shot=self.project(ar,(1,836,410))
        elif 6<=T<7.1:
            # Match-object zoom into the middle tube with an expanding macro aperture.
            water,_=self.water_scene(T);under=self.project(water,self.camera(T))
            over=self.project(ar,(1.03,866,405));u=smooth((T-6)/1.1)
            mask=Image.new('L',under.size);d=ImageDraw.Draw(mask);r=18+u*2200
            d.ellipse((1040-r,470-r,1040+r,470+r),fill=255)
            shot=Image.composite(over,under,mask)
        else:shot=self.project(ar,self.camera(T))
        out=Image.new('RGB',OUTPUT,'#f9fbfc');out.paste(shot,(0,0));d=ImageDraw.Draw(out)
        f=ImageFont.truetype(str(font),36);bb=d.textbbox((0,0),narration,font=f)
        d.text(((1920-(bb[2]-bb[0]))/2,988),narration,font=f,fill='#163e52')
        return out,ar,info

def main():
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,default=Path('projects/csu-condenser-158s'));p.add_argument('--out',type=Path,required=True);p.add_argument('--font',type=Path,required=True);p.add_argument('--execute',action='store_true');p.add_argument('--test-frames',action='store_true');args=p.parse_args()
    shots,inputs,hashes,permit,script=load_inputs(args.project)
    identity={'backend':'raster-advection-film-v2','inputs':hashes,'script_sha256':digest(script),'permit_sha256':digest(permit),'renderer_sha256':digest(__file__),'font_sha256':digest(args.font),'fps':24,'size':list(OUTPUT),'paid_calls':0}
    key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest();out=args.out;out.mkdir(parents=True,exist_ok=True)
    video=out/'SH009-SH011_motion_v2_18s.mp4';run=out/'run.json'
    if run.exists() and video.exists():
        old=json.loads(run.read_text());
        if old.get('key')==key and old.get('video_sha256')==digest(video):print('REUSED verified render');return
    if video.exists():raise ValueError('Preserve earlier render; use a new output directory')
    if not(args.execute or args.test_frames):print(json.dumps({'status':'DRY_RUN','key':key,**identity},indent=2));return
    scene=LayerScene(inputs)
    if args.test_frames:
        for T in (0,3,5.95,6.6,9,11.95,12,13,15,17.95):
            im,ar,info=scene.output(T,shots[IDS[min(2,int(T//6))]]['narration'],args.font)
            im.save(out/f'test_{T:05.2f}.jpg',quality=95)
        print('TEST_FRAMES_READY');return
    import numpy as np,csv
    from PIL import Image
    for name in ('ffmpeg','ffprobe'):
        if not shutil.which(name):raise ValueError('Missing '+name)
    evidence=out/'evidence';evidence.mkdir(exist_ok=True)
    for name,mask in [('water09',scene.water09),('water10',scene.water10),('vapor',scene.vapor),('metal',scene.metal)]:Image.fromarray((mask*255).astype('uint8')).save(evidence/f'mask_{name}.png')
    tmp=out/'render.partial.mp4'
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    proofcmd=cmd.copy();proofcmd[-1]=str(out/'camera_off_evidence.mp4')
    proofproc=subprocess.Popen(proofcmd,stdin=subprocess.PIPE)
    measure=[];previous=None
    try:
        for i in range(432):
            T=i/24;idx=min(2,int(T//6));sid=IDS[idx]
            fr,ar,info=scene.output(T,shots[sid]['narration'],args.font)
            # Measure before camera and encode; cuts excluded separately by shot ID.
            gray=ar@np.array([.299,.587,.114]);record={'frame':i,'time':T,'shot_id':sid,**info}
            if previous is not None and i%144!=0:
                record['scene_gray_MAD']=float(np.abs(gray-previous).mean())
                for name,(x0,y0,x1,y1) in scene.rois.items():
                    if name.startswith(sid):record[name+'_MAD']=float(np.abs(gray[y0:y1,x0:x1]-previous[y0:y1,x0:x1]).mean())
            measure.append(record);previous=gray
            if i%144 in (0,72,143):fr.save(evidence/f'{sid}_{i%144:03d}_render.jpg',quality=95)
            if i in (48,49,50,51,52,216,217,218,219,220,360,361,362,363,364):
                Image.fromarray(ar).save(evidence/f'source_{i:03d}.jpg',quality=98)
            proc.stdin.write(fr.tobytes())
            if 48<=i<96 or 192<=i<240 or 336<=i<384:
                fixed=Image.new('RGB',OUTPUT,'#f9fbfc');fixed.paste(scene.project(ar,(1,836,410)),(0,0))
                proofproc.stdin.write(fixed.tobytes())
            if i%48==47:print(f'frame {i+1}/432',flush=True)
        proc.stdin.close();proofproc.stdin.close()
        if proofproc.wait()!=0:raise RuntimeError('Motion evidence encoder failed')
        if proc.wait()!=0:raise RuntimeError('Encoder failed')
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(tmp)]))
        if abs(float(probe['format']['duration'])-18)>.001 or int(probe['streams'][0]['nb_frames'])!=432:raise ValueError('Timing failure')
        if {s:digest(f) for s,f in inputs.items()}!=hashes:raise ValueError('Source PNG changed')
        tmp.replace(video)
        # Source-space metrics reveal water movement independently of camera.
        metrics={}
        for sid in IDS:
            rows=[r for r in measure if r['shot_id']==sid and 'scene_gray_MAD' in r]
            keys=sorted({k for r in rows for k in r if k.endswith('MAD')})
            metrics[sid]={k:float(np.mean([r[k] for r in rows if k in r])) for k in keys}
        result={'status':'ENCODED_PENDING_HUMAN_RETEST','key':key,**identity,'video_sha256':digest(video),'probe':probe,'motion_metrics_before_camera':metrics,'source_immutability':True,'camera_off_video_sha256':digest(out/'camera_off_evidence.mp4'),'mask_checks':{'vapor_coolant_overlap_pixels':int(((scene.vapor>.01)&(scene.water10>.01)).sum()),'film_coolant_overlap_pixels':int(((scene.metal>.01)&(scene.water10>.01)).sum())},'human_acceptance':'PENDING','physical_simulation':False,'mapping':[{'shot_id':sid,'start':i*6,'end':(i+1)*6,'film_start':48+i*6,'film_end':54+i*6,'narration':shots[sid]['narration'],'metal_plate':'SH010 shared through SH011' if i else 'SH009','keyframe_role':'film reference + rebuilt liquid layer' if i==2 else 'immutable art plate'} for i,sid in enumerate(IDS)],'dependencies':{'numpy':np.__version__,'Pillow':__import__('PIL').__version__,'scipy':__import__('scipy').__version__}}
        run.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(out/'motion_per_frame.json').write_text(json.dumps(measure,ensure_ascii=False)+'\n')
        (out/'narration.srt').write_text(''.join(f'{i+1}\n00:00:{i*6:02d},000 --> 00:00:{(i+1)*6:02d},000\n{shots[sid]["narration"]}\n\n' for i,sid in enumerate(IDS)))
        print(json.dumps(metrics,indent=2));print('ENCODED',video)
    except BaseException:
        if proc.poll() is None:proc.kill();proc.wait()
        if proofproc.poll() is None:proofproc.kill();proofproc.wait()
        raise
if __name__=='__main__':main()
