#!/usr/bin/env python3
"""Original editable teaching diagram. No image model, network or inference."""
import argparse
import hashlib
import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'projects/csu-condenser-158s'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

class Canvas:
    def __init__(self,w,h,png=False):
        self.w=w;self.h=h;self.parts=[];self.image=None
        if png:
            from PIL import Image, ImageDraw
            self.image=Image.new('RGB',(w,h),'#101F30');self.draw=ImageDraw.Draw(self.image)
    def rect(self,box,fill,outline=None,width=2):
        x,y,x2,y2=box
        self.parts.append(f'<rect x="{x}" y="{y}" width="{x2-x}" height="{y2-y}" fill="{fill}" stroke="{outline or fill}" stroke-width="{width}"/>')
        if self.image:self.draw.rectangle(box,fill=fill,outline=outline,width=width)
    def line(self,points,color,width=4):
        self.parts.append(f'<polyline points="'+ ' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}"/>')
        if self.image:self.draw.line(points,fill=color,width=width)
    def circle(self,x,y,r,color):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')
        if self.image:self.draw.ellipse((x-r,y-r,x+r,y+r),fill=color)
    def polygon(self,points,color):
        self.parts.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="{color}"/>')
        if self.image:self.draw.polygon(points,fill=color)
    def svg(self):
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}"><title>Original teaching schematic, not to scale</title>'+''.join(self.parts)+'</svg>\n'

def arrow(c,points,color,width=5):
    c.line(points,color,width);x,y=points[-1];px,py=points[-2]
    if abs(x-px)>abs(y-py):
        sign=1 if x>px else -1;c.polygon([(x,y),(x-sign*14,y-9),(x-sign*14,y+9)],color)
    else:
        sign=1 if y>py else -1;c.polygon([(x,y),(x-9,y-sign*14),(x+9,y-sign*14)],color)

def draw_master(spec,focus='overview',phase=0,png=False):
    c=Canvas(*spec['canvas'],png);pal=spec['palette'];g=spec['components']
    bg=pal['background'];metal=pal['metal'];steam=pal['steam'];water=pal['cooling_water'];gold=pal['condensate'];air=pal['noncondensables']
    c.rect([0,0,c.w,c.h],bg)
    # Frame space is blank for later title, labels and narration overlays.
    c.rect(g['shell'],'#1C3445')
    # Open steam neck, hotwell mouth and extraction penetration.
    c.line([(300,650),(300,230),(650,230)],metal,5)
    c.line([(810,230),(1160,230),(1160,590)],metal,5)
    c.line([(1160,610),(1160,650),(1000,650)],metal,5)
    c.line([(300,650),(480,650)],metal,5)
    c.rect(g['steam_inlet'],'#254856')
    c.line([(650,120),(650,230)],metal,5)
    c.line([(810,120),(810,230)],metal,5)
    arrow(c,[(730,50),(730,170)],steam,7)
    c.rect(g['hotwell'],'#29343B')
    c.line([(480,650),(480,755),(718,755)],metal,5)
    c.line([(742,755),(1000,755),(1000,650)],metal,5)
    c.rect([485,705,995,750],gold)
    c.line(g['condensate_outlet'],metal,26);arrow(c,g['condensate_outlet'],gold,12)
    c.rect(g['left_waterbox'],'#17406A',metal,5)
    c.rect(g['right_waterbox'],'#17406A',metal,5)
    arrow(c,[(65,440),(178,440)],water,16)
    arrow(c,[(1280,410),(1470,410)],water,16)
    # Each tube wall, lumen and seal has the same geometry across all shots.
    for y in g['tube_centrelines_y']:
        c.rect([300,y-14,1160,y+14],metal)
        c.rect([300,y-7,1160,y+7],water)
        if focus in ['separation','cooling']:
            x=345+int(phase*700)
            arrow(c,[(x,y),(x+55,y)],'#84BEF3',4)
        if focus=='film':
            c.line([(310,y-17),(1148,y-17)],gold,4)
            c.line([(310,y+17),(1148,y+17)],gold,4)
    # Tube sheets surround sealed tube penetrations: no waterbox-to-shell link.
    for x in g['tube_sheets_x']:
        c.rect([x-8,296,x+8,569],'#97A9B8')
        for y in g['tube_centrelines_y']:c.rect([x-8,y-7,x+8,y+7],water)
    # Steam is symbolic, visible in the shell and never in the blue lumens.
    for x in [420,610,800,990]:
        arrow(c,[(x,255),(x,295)],steam,4)
    for y in [350,390,430,470,510]:
        for x in [440,720,910]:c.circle(x+int(phase*16),y,3,steam)
    c.rect(g['air_cooling_zone'],'#233848','#485A69',2)
    for x,y in [(1025,587),(1055,620),(1115,615)]:c.circle(x,y,4,air)
    c.circle(1085,583,3,steam)
    c.line(g['air_extraction_path'],metal,20);c.line(g['air_extraction_path'],'#354857',12)
    arrow(c,[(1190,600),(1310,600)],air,5);c.circle(1260,600,3,steam)
    # System block only: no invented vacuum pump internals or pipe fittings.
    c.rect([1320,655,1440,735],'#324756',metal,4)
    arrow(c,[(1380,735),(1380,795)],air,8)
    if focus=='structure':
        outline=steam if phase>.5 else '#485A69'
        c.line([(300,650),(300,230),(650,230)],outline,5)
        c.line([(810,230),(1160,230),(1160,590)],outline,5)
    if focus=='heat':
        # External condensate film -> metal -> tube-side water; heat is not mass.
        arrow(c,[(700,382),(700,397)],gold,4)
    if focus=='film':
        # Only below lowest row; no condensate goes through another tube.
        for x in [580,780,930]:
            y=555+int(phase*135);c.circle(x,y,5,gold)
    if focus in ['overview','separation']:
        arrow(c,[(580,559),(580,690)],gold,4)
    return c

def render(project=PROJECT,png=False):
    spec_path=project/'references/master-spec.json';task_path=project/'tasks/keyframes.json';script_path=project/'script/candidate.json'
    spec=json.loads(spec_path.read_text(encoding='utf-8'));tasks=json.loads(task_path.read_text(encoding='utf-8'))
    records=[]
    for j in tasks['jobs']:
        if j['master_sha256']!=sha(spec_path) or j['script_sha256']!=sha(script_path):raise ValueError('Stale keyframe task: regenerate/review tasks')
        for name,phase in [('start',0),('end',1)]:
            c=draw_master(spec,j['focus'],phase,png)
            dest=project/'keyframes'/j['shot_id'];dest.mkdir(parents=True,exist_ok=True)
            svg=dest/(name+'.svg');svg.write_text(c.svg(),encoding='utf-8')
            record={'shot_id':j['shot_id'],'position':name,'status':'DRAFT','master_id':spec['master_id'],'master_sha256':sha(spec_path),'script_sha256':sha(script_path),'task_sha256':sha(task_path),'renderer_sha256':sha(Path(__file__)),'backend':'original-deterministic-diagram','seed':0,'svg':str(svg.relative_to(project)),'svg_sha256':sha(svg)}
            if png:
                target=dest/(name+'.png');c.image.save(target);record.update(png=str(target.relative_to(project)),png_sha256=sha(target))
            records.append(record)
    (project/'keyframes/index.json').write_text(json.dumps({'status':'DRAFT','frames':records},indent=2)+'\n',encoding='utf-8')
    (project/'references/master.svg').write_text(draw_master(spec).svg(),encoding='utf-8')
    print(f'RENDERED: {len(records)} draft SVG'+(' + PNG' if png else '')+'; no approval implied')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,default=PROJECT);p.add_argument('--png',action='store_true');a=p.parse_args();render(a.project.resolve(),a.png)
