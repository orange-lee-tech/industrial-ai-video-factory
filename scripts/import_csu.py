#!/usr/bin/env python3
"""Import the supplied 26-shot XLSX using stdlib; preserve original XLSX locally, never upload it by default."""
import argparse,json,pathlib,re,sys,zipfile,xml.etree.ElementTree as ET
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def load_first_sheet(path):
  with zipfile.ZipFile(path) as z:
    shared=[]
    if 'xl/sharedStrings.xml' in z.namelist():
      root=ET.fromstring(z.read('xl/sharedStrings.xml'))
      shared=[''.join(t.text or '' for t in si.findall('.//m:t',NS)) for si in root.findall('m:si',NS)]
    root=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    output=[]
    for row in root.findall('.//m:sheetData/m:row',NS):
      obj={}
      for cell in row.findall('m:c',NS):
        ref=cell.get('r',''); col=re.match(r'[A-Z]+',ref)
        if not col: continue
        ci=0
        for k in col.group(): ci=ci*26+ord(k)-64
        v=cell.find('m:v',NS)
        if cell.get('t')=='inlineStr': value=''.join((x.text or '') for x in cell.findall('.//m:t',NS))
        elif v is None: value=''
        elif cell.get('t')=='s': value=shared[int(v.text)]
        else: value=v.text or ''
        obj[ci-1]=value
      output.append([obj.get(i,'') for i in range(max(obj.keys(),default=-1)+1)])
    return output

def main():
  a=argparse.ArgumentParser();a.add_argument('xlsx',type=pathlib.Path);a.add_argument('--out',default='projects/csu-condenser-158s/source/shot-plan.json');args=a.parse_args()
  rows=load_first_sheet(args.xlsx); head=rows[0]; data=[]
  for row in rows[1:]:
    if not row or not str(row[0]).strip().isdigit():continue
    def g(i):return str(row[i]) if i<len(row) and row[i] is not None else ''
    n=int(g(0)); dur=float(g(4)); data.append({'shot_id':f'SH{n:03d}','section':g(1),'start':g(2),'end':g(3),'duration_seconds':dur,'narration':g(5),'camera':g(6),'visual_prompt':g(7),'overlay':g(8),'sound':g(9),'production_method':g(10),'technical_review':g(11),'status':'DRAFT'})
  total=sum(x['duration_seconds'] for x in data)
  if len(data)!=26 or total!=158 or [x['shot_id'] for x in data]!=[f'SH{i:03d}' for i in range(1,27)]:raise ValueError(f'Expected 26 ordered shots / 158s; got {len(data)} / {total}')
  out=pathlib.Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps({'title':'凝汽器与真空系统','source':args.xlsx.name,'total_seconds':total,'shots':data},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(f'PASS: {len(data)} shots, {total:g}s -> {out} (still DRAFT; no technical approval implied)')
if __name__=='__main__':main()
