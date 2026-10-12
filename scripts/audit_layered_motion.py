#!/usr/bin/env python3
"""Decode actual MP4s; quantify camera-off water movement and extract QA frames.
NumPy/Pillow required; results are evidence, not an automatic artistic PASS.
"""
import argparse,json,subprocess,hashlib
from pathlib import Path

def main():
 import numpy as np
 from PIL import Image,ImageDraw,ImageFont
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--font',type=Path,required=True);a=p.parse_args();o=a.out
 run=json.loads((o/'run.json').read_text());v=o/'SH009-SH011_motion_v2_18s.mp4';proof=o/'camera_off_evidence.mp4';ev=o/'evidence'
 assert hashlib.sha256(v.read_bytes()).hexdigest()==run['video_sha256']
 assert hashlib.sha256(proof.read_bytes()).hexdigest()==run['camera_off_video_sha256']
 def decode(path):
  data=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vf','scale=960:540','-f','rawvideo','-pix_fmt','gray','-'])
  return np.frombuffer(data,dtype=np.uint8).reshape(-1,540,960).astype(np.float32)
 movie=decode(v);fixed=decode(proof);assert len(movie)==432 and len(fixed)==144
 def box(ar,b):
  x0,y0,x1,y1=b;return ar[:,round(y0*471/820):round(y1*471/820),round(x0*960/1672):round(x1*960/1672)]
 def dx_est(a,b):
  errors=[]
  for d in range(-10,11):
   if d>0:x,y=a[:,:-d],b[:,d:]
   elif d<0:x,y=a[:,-d:],b[:,:d]
   else:x,y=a,b
   errors.append(float(np.abs(x-y).mean()))
  return int(np.argmin(errors))-10
 summary={}
 rois=[(850,274,1500,316),(730,380,1490,478),(730,380,1490,478)]
 metal=[(595,180,668,705),(220,360,242,500),(220,360,242,500)]
 for j,sid in enumerate(['SH009','SH010','SH011']):
  segment=movie[j*144:(j+1)*144];control=fixed[j*48:(j+1)*48]
  water=box(control,rois[j]);structure=box(control,metal[j]);bg=box(control,(30,30,160,100))
  shifts=[dx_est(water[k],water[k+1]) for k in range(47)]
  summary[sid]={'actual_main_adjacent_gray_MAD_960x540':float(np.abs(segment[1:]-segment[:-1]).mean()),'camera_off_adjacent_gray_MAD_960x540':float(np.abs(control[1:]-control[:-1]).mean()),'camera_off_water_ROI_adjacent_gray_MAD':float(np.abs(water[1:]-water[:-1]).mean()),'camera_off_structure_ROI_MAD':float(np.abs(structure[1:]-structure[:-1]).mean()),'camera_off_background_ROI_MAD':float(np.abs(bg[1:]-bg[:-1]).mean()),'water_shift_median_px_per_frame_at_half_resolution':float(np.median(shifts)),'positive_shift_frames':sum(x>0 for x in shifts),'measured_pairs':47}
  # Actual decoded consecutive camera-off ROI frames, not generated stills.
  sheet=Image.new('RGB',(1200,500),'#f7fafb');d=ImageDraw.Draw(sheet);font=ImageFont.truetype(str(a.font),19)
  for k in range(5):
   crop=water[12+k].astype('uint8');im=Image.fromarray(crop).convert('RGB').resize((1150,65))
   sheet.paste(im,(25,45+k*90));d.text((25,20+k*90),f'{sid} 连续帧 {j*48+12+k}（24fps，关闭运镜）',font=font,fill='#1b4256')
  sheet.save(ev/f'{sid}_consecutive_water.jpg',quality=96)
 # Nine full-resolution frames decoded from actual main MP4.
 board=Image.new('RGB',(1440,900),'#edf2f5');d=ImageDraw.Draw(board);font=ImageFont.truetype(str(a.font),19)
 for row,sid in enumerate(['SH009','SH010','SH011']):
  for col,T in enumerate((row*6+.04,row*6+3,row*6+5.95)):
   f=ev/f'{sid}_decoded_{col}.jpg'
   subprocess.run(['ffmpeg','-y','-v','error','-ss',str(T),'-i',str(v),'-frames:v','1','-q:v','2',str(f)],check=True)
   im=Image.open(f).resize((480,270));board.paste(im,(480*col,300*row+30));d.text((480*col+10,300*row+4),f'{sid}  {T:.2f}s',font=font,fill='#1b4256')
 board.save(o/'decoded_review_board.jpg',quality=95)
 # Consecutive film/heat crops from actual camera-off clip, accompanied by full video.
 for name,j,b in [('SH010_heat',1,(770,205,1480,324)),('SH011_film',2,(640,553,1470,650))]:
  region=box(fixed[j*48:(j+1)*48],b)
  summary[name]={'ROI_gray_MAD_camera_off':float(np.abs(region[1:]-region[:-1]).mean())}
  sheet=Image.new('RGB',(1200,620),'#f7fafb');d=ImageDraw.Draw(sheet)
  for k in range(5):
   d.text((20,20+k*120),f'{name}  连续帧 {j*48+12+k}',font=font,fill='#1b4256')
   sheet.paste(Image.fromarray(region[12+k].astype('uint8')).convert('RGB').resize((1160,85)),(20,45+k*120))
  sheet.save(ev/f'{name}_consecutive.jpg',quality=95)
 result={'decode_status':'COMPLETE','main_frames':len(movie),'control_frames':len(fixed),'metrics_units':'8-bit grayscale absolute difference; half-resolution actual decoded frames, cuts excluded','metrics':summary,'mask_checks':run['mask_checks'],'source_metrics_before_camera':run['motion_metrics_before_camera'],'human_acceptance':'PENDING_RETEST','warning':'Motion magnitude is not artistic or engineering acceptance. Compare original full MP4, not only metrics.'}
 (o/'decoded-qa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
