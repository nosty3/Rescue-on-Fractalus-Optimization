"""v13: width-compiled ilmenit terrain workers integrated with v12.
The upstream tree generator is read, never modified.
"""
from pathlib import Path
import sys,re,subprocess,json,hashlib,dis,os
SRC=Path(__file__).resolve().parent;R=SRC.parents[1];O=R/'build/v13';O.mkdir(parents=True,exist_ok=True);P=O
sys.path.insert(0,str(SRC))
import ilmenit_generator as gen
BASE=(R/'build/v12-reference.rom').read_bytes();assert hashlib.sha256(BASE).hexdigest()=='4959a82ab36528a0448a40e6178fdb72d321e5d1e23c258036f5e22e51cfa20e'
MADS=Path(os.environ.get('FRACTALUS_MADS',str(R/'tools/mads/bin/windows_x86_64/mads.exe')))
(O/'workers').mkdir(exist_ok=True)
raw=(R/'src/v12/candidate.asm').read_text(encoding='utf-8');LAZY=raw[raw.index('\nlazy5\n')+1:raw.index('; Opus: wariant zimny')]
# Identical inline height/cache guard; lazy helper preserves framebuffer pointer and X.
OLD=' ldy $3900,x\n lda ($80),y'
NEW=' tya\n ldy $3900,x\n cmp $0100,y\n bcc clear_ok_{i}\n jsr lazy5\nclear_ok_{i}\n lda ($80),y'

def size(line):
 if not line.startswith(' '):return 0
 p=line.strip().split(None,1);op=p[0].lower();arg=p[1] if len(p)>1 else ''
 if op in ('opt','org'):return 0
 if op=='dta':return len(arg.split(','))
 if op.startswith('b') and op!='bit':return 2
 if op in ('jmp','jsr'):return 3
 if not arg or arg=='@':return 1
 if arg.startswith('#') or arg.startswith('('):return 2
 if re.match(r'^\$[0-9a-fA-F]{1,2}(?:,|$)',arg):return 2
 return 3

class UnsupportedLayout(Exception):pass

def split_body(body,cap=0x182c):
 labels={s:i for i,s in enumerate(body) if s and not s[0].isspace()};edges=[]
 for i,s in enumerate(body):
  p=s.strip().split()
  if s.startswith(' ') and len(p)==2 and p[0] in ('bcc','bcs','beq','bne','bmi','bpl','bvc','bvs','jmp','jsr') and p[1] in labels:
   j=labels[p[1]];edges.append((min(i,j),max(i,j)))
 chunks=[];start=0
 while start<len(body):
  used=0;cuts=[]
  for i in range(start,len(body)+1):
   if used>cap:break
   if i>start and not any(lo<i<=hi for lo,hi in edges):cuts.append(i)
   if i<len(body):used+=size(body[i])
  if not cuts:raise UnsupportedLayout((start,len(body)))
  end=cuts[-1];chunks.append(body[start:end]);start=end
 return chunks

def prepare(width,left=False):
 for minimum in (6,12,24,None):
  cull=minimum if not left and 11<=width<=64 and width not in (42,50,52,53) else None
  s=gen.source(width,16,clip=True,dead_x=True,left_clip=left,cull_min=cull,cull_precheck=cull is not None,layout='linear')
  # Replace each accepted pixel store with the v11 lazy-clear protocol.
  count=0
  while OLD in s:s=s.replace(OLD,NEW.format(i=count),1);count+=1
  body=s.splitlines()[2:s.splitlines().index('hot_end')]
  cold=s.split('cold_helpers_begin\n',1)[1].split('cold_helpers_end',1)[0].splitlines()
  cold=[x for x in cold if not x.startswith(';')]
  if left or sum(map(size,cold))<=0x9e00-0x990a:break
 else:raise RuntimeError('helpers too large')
 cold_size=sum(map(size,cold));cold_at=0x990a if cold_size<=0x9e00-0x990a else ((0x982f-cold_size)//256)*256
 return split_body(body,min(0x182c,cold_at-0x8000-3)),cold,cull,count

def assemble(name,s):
 src=O/'workers'/(name+'.asm');out=src.with_suffix('.bin');src.write_text(s,encoding='utf-8')
 r=subprocess.run([str(MADS),str(src),'-o:'+str(out),'-t:'+str(src.with_suffix('.lab'))],capture_output=True,text=True)
 assert not r.returncode,(name,r.stdout,r.stderr)
 b=out.read_bytes();assert len(b)==8192;return b

def worker(width,left=False,first=16):
 chunks,cold,cull,npixels=prepare(width,left);result=[]
 for index,body in enumerate(chunks):
  bank=first+index;code=[' opt h-',' org $8000']+body
  if index+1<len(chunks):code+=[' jmp $9e00']
  cold_size=sum(map(size,cold));cold_at=0x990a if cold_size<=0x9e00-0x990a else ((0x982f-cold_size)//256)*256
  if cold_at<0x982f:code+=[f' ert * > ${cold_at:04x}',f' :(${cold_at:04x}-*) dta $ff']+cold
  code+=[' ert * > $982f',' :($982f-*) dta $ff',' jmp $8000',' :($985b-*) dta $ff',' jmp $8000',' :($9900-*) dta $ff',' php',' pha',' lda #2',' sta $d500',' ert * <> $9907',' :($990a-*) dta $ff']
  if cold_at==0x990a:code+=cold
  code+=[' ert * > $9e00',' :($9e00-*) dta $ff',' php',' pha',f' lda #{bank+1}',' sta $d500',' ert * <> $9e07',' pla',' plp',' jmp $8000',' :($9e10-*) dta $ff']+LAZY.splitlines()+[' ert * > $9f78',' :($9f78-*) dta $ff','row_lo',' dta '+','.join(str((0x1010+96*(151-h))&255) for h in range(104,152)),' :($9fb0-*) dta $ff','row_hi',' dta '+','.join(str((0x1010+96*(151-h))>>8) for h in range(104,152)),' :($9fff-*) dta $ff',f' dta {bank}']
  stem=f'{"left" if left else "normal"}-{width:03}-b{bank:03}'
  result.append(assemble(stem,'\n'.join(code)+'\n'))
 return result,dict(width=width,left=left,banks=len(chunks),cull_min=cull,pixels=npixels)

def expanded(size):
 rom=bytearray(BASE)+bytearray([255])*(size-len(BASE));rom[-8192:]=BASE[-8192:];assert rom[-20]==15;rom[-20]=size//8192-1
 return rom

def install(selected,size,profile=False):
 rom=expanded(size);normal=[0]*128;left=[0]*128;bank=16;entries=[]
 for width,isleft in selected:
  bins,meta=worker(width,isleft,bank);assert bank+len(bins)<=size//8192-1
  (left if isleft else normal)[width]=bank
  for b in bins:rom[bank*8192:(bank+1)*8192]=b;bank+=1
  entries.append(dict(meta,first_bank=bank-len(bins)))
 # Old bank-2 fill code is unreachable since bank9 handles fill.
 rom[0x5400:0x5480]=bytes(normal);rom[0x5480:0x5500]=bytes(left)
 selector=''' opt h-
 org $9c42
 php
 stx $60
 lda $95
 cmp $82
 bcc fallback
 beq fallback
 sec
 sbc $82
 bmi fallback
 tax
 lda $82
 cmp #44
 bcc left_case
 cmp #212
 bcs fallback
 lda $9400,x
 jmp selected
left_case
 lda $95
 cmp #45
 bcc fallback
 lda $9480,x
selected
 beq fallback
 ldx $60
 plp
 jmp $9858
fallback
 ldx $60
 plp
 lda #5
 jmp $9fef
 ert * > $9d20
'''
 src=O/'selector.asm';src.write_text(selector);out=O/'selector.bin';r=subprocess.run([str(MADS),str(src),'-o:'+str(out)],capture_output=True,text=True);assert not r.returncode,r.stdout+r.stderr;code=out.read_bytes();rom[0x5c42:0x5c42+len(code)]=code
 assert rom[0x582a:0x582f]==bytes.fromhex('a9058d00d5');rom[0x582a:0x582d]=bytes.fromhex('4c429c')
 assert rom[0x5858:0x585b]==b'\xff'*3;rom[0x5858:0x585b]=bytes.fromhex('8d00d5')
 # Fallback handover: bank 2 $9fef -> bank 5 $9ff2.
 # $9e50 belongs to the mixer; $9875 belongs to live geometry dispatch.
 assert rom[0x5fef:0x5ff2]==b'\xff'*3
 rom[0x5fef:0x5ff2]=bytes.fromhex('8d00d5')
 assert rom[5*8192+0x1ff2:5*8192+0x1ff5]==b'\xff'*3
 rom[5*8192+0x1ff2:5*8192+0x1ff5]=rom[5*8192+0x182f:5*8192+0x1832]
 assert rom[0x5d3b:0x5fd5]==BASE[0x5d3b:0x5fd5]
 assert rom[0x582f:0x5858]==BASE[0x582f:0x5858]
 assert rom[0x585b:0x5a55]==BASE[0x585b:0x5a55]
 return bytes(rom),dict(entries=entries,used_extra_banks=bank-16,free_extra_banks=size//8192-1-bank)

def save(size,selected):
 rom,meta=install(selected,size);name=f'Rescue on Fractalus! - optimized v13 {size//1024}KB';(O/(name+'.rom')).write_bytes(rom);typ={262144:23,524288:24,1048576:25}[size];(O/(name+'.car')).write_bytes(b'CART'+typ.to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom);meta.update(size=size,sha256=hashlib.sha256(rom).hexdigest(),source='v12 + ilmenit width generator + existing HD/lazy clear',version='v13');(O/f'manifest-{size//1024}.json').write_text(json.dumps(meta,indent=2));print(size//1024,'KB',meta['used_extra_banks'],'banks',flush=True);return rom

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('action',choices=['probe','build']);args=p.parse_args()
 if args.action=='probe':
  for w in (16,32,48,64,81,100,127):
   code,meta=worker(w);print(meta,flush=True)
 else:
  plans=json.loads((SRC/'selection.json').read_text())
  for kb,rows in plans.items():save(int(kb)*1024,[tuple(x) for x in rows])
