from session import *
sys.path.insert(0,str(ROOT/'tools/pythonlib'))
from py65.devices.mpu6502 import MPU
import random,time
OUT=ROOT/'results/optimized';OUT.mkdir(exist_ok=True)
def cpu(rom,mem=None):
 m=list(mem) if mem is not None else [0]*65536
 m[0x8000:0xa000]=rom[0x4000:0x6000];m[0xa000:0xc000]=rom[0xe000:]
 return MPU(memory=m)
def run(c,entry,regs=None):
 c.pc=entry;c.sp=0xfd;c.memory[0x1fe]=0xfe;c.memory[0x1ff]=0x3f
 if regs:
  for dst,src in [('a','A'),('x','X'),('y','Y'),('p','P')]:setattr(c,dst,int(regs[src][1:],16))
 before=c.processorCycles;steps=0
 while c.pc!=0x3fff:
  c.step();steps+=1
  if steps>1000000:raise RuntimeError(('runaway',hex(c.pc),hex(entry)))
 return c.processorCycles-before

