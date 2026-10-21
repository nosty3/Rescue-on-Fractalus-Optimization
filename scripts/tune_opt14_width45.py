from opt14_common import *
import sys
rows=[]
for depths in ['1,2,3,4','2,3,4,5','0,1,2,3','1,2','2,3','3,4','2','3','4']:
 a=subprocess.run([sys.executable,str(ROOT/'scripts/build_opt14_width45.py'),'--depths',depths],capture_output=True,text=True)
 if a.returncode:print('build failed',depths,a.stdout+a.stderr,flush=True);continue
 b=subprocess.run([sys.executable,str(ROOT/'scripts/test_opt14_renderer.py'),'opt14_division','opt14_width45'],capture_output=True,text=True)
 assert b.returncode==0,b.stdout+b.stderr
 data=json.loads((OUT/'opt14_width45-renderer-tests.json').read_text());saved=sum(r['saved'] for r in data['scenes']);rows.append({'depths':depths,'saved':saved});print(rows[-1],flush=True)
(OUT/'width45-tuning.json').write_text(json.dumps(rows,indent=2));best=max(rows,key=lambda r:r['saved']);print('BEST',best,flush=True)
subprocess.run([sys.executable,str(ROOT/'scripts/build_opt14_width45.py'),'--depths',best['depths']],check=True)
subprocess.run([sys.executable,str(ROOT/'scripts/test_opt14_renderer.py'),'opt14_division','opt14_width45'],check=True)
