#!/usr/bin/env python3
"""Offline XLSX transcription; validates headers and cuts, never approves facts."""
import argparse
import hashlib
import json
import pathlib
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET
NS = {'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main', 'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
HEADERS = ['镜号','叙事段落','开始','结束','时长(秒)','配音＝字幕原文','镜头构图／运镜','AI画面提示词（勿让模型造文字）','后期画面标注','配乐／音效','画面实现方式','技术审校与避坑','制作状态']
def load_first_sheet(path):
    with zipfile.ZipFile(path) as z:
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            root=ET.fromstring(z.read('xl/sharedStrings.xml'))
            shared=[''.join(t.text or '' for t in si.findall('.//m:t',NS)) for si in root.findall('m:si',NS)]
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        first=wb.find('m:sheets/m:sheet',NS)
        if first is None: raise ValueError('Workbook has no sheets')
        rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rel=next((r for r in rels if r.get('Id')==first.get('{'+NS['r']+'}id')),None)
        if rel is None or rel.get('TargetMode')=='External': raise ValueError('Invalid worksheet relationship')
        target=rel.get('Target','')
        sheet=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
        if not sheet.startswith('xl/worksheets/'): raise ValueError('Unexpected worksheet target')
        root=ET.fromstring(z.read(sheet)); output=[]
        for row in root.findall('m:sheetData/m:row',NS):
            obj={}
            for cell in row.findall('m:c',NS):
                match=re.match(r'[A-Z]+',cell.get('r',''))
                if not match: raise ValueError('Cell has no column reference')
                ci=0
                for k in match.group(): ci=ci*26+ord(k)-64
                if cell.find('m:f',NS) is not None: raise ValueError('Formula cells require explicit value export')
                v=cell.find('m:v',NS)
                if cell.get('t')=='inlineStr': value=''.join(x.text or '' for x in cell.findall('.//m:t',NS))
                elif v is None: value=''
                elif cell.get('t')=='s': value=shared[int(v.text)]
                else: value=v.text or ''
                obj[ci-1]=value
            output.append([obj.get(i,'') for i in range(max(obj.keys(),default=-1)+1)])
        return output

def seconds(value):
    if not re.fullmatch(r'\d{2}:\d{2}',value) or int(value[3:])>=60: raise ValueError('Expected MM:SS: '+value)
    return int(value[:2])*60+int(value[3:])

def transcribe(rows,source_name,source_hash):
    if not rows or rows[0]!=HEADERS: raise ValueError('Unexpected headers; refuse positional mis-import')
    data=[]; cursor=0
    for row in rows[1:]:
        if not any(str(c).strip() for c in row): continue
        if len(row)<12 or not re.fullmatch(r'\d+',row[0].strip()): raise ValueError('Unexpected row or missing fields')
        n=int(row[0]); dur=float(row[4]); start=seconds(row[2]); end=seconds(row[3])
        if n!=len(data)+1 or dur!=(8 if n==26 else 6) or start!=cursor or end-start!=dur: raise ValueError(f'Invalid timeline at SH{n:03d}')
        if n<26 and not row[5].strip(): raise ValueError(f'Missing narration SH{n:03d}')
        cursor=end
        keys=['shot_id','section','start','end','duration_seconds','narration','camera','visual_prompt','overlay','sound','production_method','technical_review']
        data.append(dict(zip(keys,[f'SH{n:03d}',*row[1:4],dur,*row[5:12]]),status='DRAFT'))
    if len(data)!=26 or cursor!=158: raise ValueError(f'Expected 26 shots / 158s; got {len(data)} / {cursor}')
    return {'project_id':'csu-condenser-158s','title':'凝汽器与真空系统','source':source_name,'source_sha256':source_hash,'total_seconds':cursor,'shots':data}

def main():
    p=argparse.ArgumentParser();p.add_argument('xlsx',type=pathlib.Path)
    p.add_argument('--out',type=pathlib.Path,default=pathlib.Path('projects/csu-condenser-158s/source/shot-plan.json'))
    p.add_argument('--replace',action='store_true');a=p.parse_args()
    data=transcribe(load_first_sheet(a.xlsx),a.xlsx.name,hashlib.sha256(a.xlsx.read_bytes()).hexdigest())
    content=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    if a.out.exists() and a.out.read_text(encoding='utf-8')!=content and not a.replace: p.error('Output differs; use a new path or --replace after review')
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(content,encoding='utf-8')
    print(f'PASS: 26 shots / 158s -> {a.out}; transcription DRAFT')
if __name__=='__main__': main()
