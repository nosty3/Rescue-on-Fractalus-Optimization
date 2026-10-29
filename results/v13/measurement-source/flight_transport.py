"""Validated bounded packet transport; virtual timing and game code unchanged."""
import json,math,base64,hashlib
def packet(a,command,count,prefix=None):
 # Snapshot every gate so a natural end inside a packet retains its exact RAM.
 block=command+'\nEVAL pc+65536*db($4a)\nCLOCK\nMEMDUMP 0 32768\n'
 a._sock.sendall(((prefix+'\n' if prefix else '')+block*count).encode())
 if prefix:assert json.loads(a._recv_line())['ok']
 rows=[]
 for _ in range(count):
  replies=[json.loads(a._recv_line()) for _ in range(4)]
  assert all(r.get('ok') for r in replies),replies[:3]
  rows.append((replies[1]['value'],replies[2]['tick'],replies[3]['data']))
 return rows

def measure(a,api,mode,seconds=60,max_batch=16):
 api.advance(a,170);a.bp_set(0xb516);a.frame(200);assert a.regs()['PC']=='$b516'
 start=a.clock()['tick'];events=[0];cues=[];termination=None;checks={};elapsed=0;nextcue=0;batches=0;gates=0;end_ram=None;done=False
 a.watch_set(0x4a,mode='w')
 while not done:
  prefix=None
  if mode=='steering':
   if elapsed>=math.ceil(nextcue*api.FREQ):
    direction='n' if nextcue%4==0 else 'c';prefix=f'JOY 0 {direction}';cues.append(dict(requested_second=nextcue,tick=elapsed,direction=direction));nextcue+=1 if direction=='n' else 3
   remaining=math.ceil(nextcue*api.FREQ)-elapsed
  else:remaining=math.ceil(seconds*api.FREQ)-elapsed
  if remaining>0:
   count=min(max_batch,max(1,remaining//200000));n=max(1,min(100000000,remaining//count));command=f'CYCLES {n}'
  else:count=1;command='FRAME 200'
  # Each gate takes at most n cycles, so the packet cannot cross a joystick cue.
  batch=packet(a,command,count,prefix);batches+=1;gates+=count
  for packed,tick,snapshot in batch:
   elapsed=tick-start;pc=packed&65535;game_mode=packed>>16
   if game_mode!=2:
    termination=dict(mode=game_mode,pc=hex(pc),elapsed_seconds=elapsed/api.FREQ,last_completed_image_seconds=events[-1]/api.FREQ);end_ram=base64.b64decode(snapshot);done=True;break
   if pc==0xb516:
    assert elapsed>events[-1],(elapsed,events[-1])
    events.append(elapsed)
    for sec in (15,30,60):
     if sec<=seconds and str(sec) not in checks and elapsed>=sec*api.FREQ:checks[str(sec)]=dict(intervals=len(events)-1,ticks=elapsed,seconds=elapsed/api.FREQ,fps=(len(events)-1)*api.FREQ/elapsed,complete_window=True)
    if elapsed>=seconds*api.FREQ:end_ram=base64.b64decode(snapshot);done=True;break
  # Any already executed suffix is excluded, including its RAM snapshots.
 assert len(events)>1 and end_ram is not None
 for sec in (15,30,60):
  if sec<=seconds and str(sec) not in checks:checks[str(sec)]=dict(intervals=len(events)-1,ticks=events[-1],seconds=events[-1]/api.FREQ,fps=(len(events)-1)*api.FREQ/events[-1],complete_window=False)
 a.bp_clear_all();api.verify(a)
 return dict(checkpoints=checks,termination=termination,events=events,cues=cues,end_ram_sha256=hashlib.sha256(end_ram).hexdigest()),dict(batches=batches,gates=gates)
