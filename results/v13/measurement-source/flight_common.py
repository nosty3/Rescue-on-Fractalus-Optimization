"""Independent stock Atari lifecycle for current cartridge benchmarks."""
from pathlib import Path
import os,sys,subprocess,time
R=Path(__file__).resolve().parents[1]
class Video:
 def __init__(self,name):self.name=name;self.FREQ=(3546895 if name=='pal' else 3579545)/2;self.FRAME_TICKS=114*(312 if name=='pal' else 262)
 @property
 def EXE(self):
  directory=Path(os.environ['FRACTALUS_BRIDGE_DIR']) if os.environ.get('FRACTALUS_BRIDGE_DIR') else next((R/'tools/bridge').glob('*'))
  return directory/('AltirraBridgeServer.exe' if os.name=='nt' else 'AltirraBridgeServer')
 def verify(self,a):
  c=a.config();assert (c['video'],c['memory'],c['machine'])==(self.name,'64K','800XL') and not any(c[k] for k in ('rapidus','vbxe','u1mb'));return c
 def advance(self,a,n):
  t=a.clock()['tick'];a.frame(n);delta=a.clock()['tick']-t;assert abs(delta-n*self.FRAME_TICKS)<=self.FRAME_TICKS;self.verify(a)
 def Emulator(self,folder,name):return Emulator(self,folder,name)
pal=Video('pal');ntsc=Video('ntsc')
class Emulator:
 def __init__(self,video,folder,name):self.video=video;self.folder=Path(folder);self.name=name
 def __enter__(self):
  directory=Path(os.environ['FRACTALUS_BRIDGE_DIR']) if os.environ.get('FRACTALUS_BRIDGE_DIR') else next((R/'tools/bridge').glob('*'))
  sys.path.insert(0,str(directory/'sdk/python'));from altirra_bridge import AltirraBridge
  self.folder.mkdir(parents=True,exist_ok=True);temp=R/'tools';temp.mkdir(exist_ok=True);env=os.environ.copy();env['TEMP']=env['TMP']=str(temp)
  self.log=(self.folder/f'{self.name}-server.log').open('wb');exe=directory/('AltirraBridgeServer.exe' if os.name=='nt' else 'AltirraBridgeServer')
  self.p=subprocess.Popen([str(exe),'--bridge=tcp:127.0.0.1:0'],cwd=R,env=env,stdout=self.log,stderr=self.log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
  token=temp/f'altirra-bridge-{self.p.pid}.token'
  for _ in range(200):
   if token.exists():
    try:self.a=AltirraBridge.from_token_file(str(token));break
    except Exception:pass
   if self.p.poll() is not None:raise RuntimeError('Emulator exited during startup')
   time.sleep(.05)
  else:raise RuntimeError('Emulator startup timeout')
  a=self.a;a.pause();a.bp_clear_all();a.consol();a.joy(0,'center')
  for key,value in [('addons','stock'),('machine','800XL'),('memory','64K'),('video',self.video.name),('history','off')]:a.config(key,value)
  return self
 def __exit__(self,*exc):
  try:self.a.quit()
  finally:
   try:self.p.wait(timeout=10)
   except subprocess.TimeoutExpired:self.p.terminate();self.p.wait(timeout=10)
   self.log.close()
