"""NMOS-6502 test harness rejecting instructions unsupported by py65."""
from test_clear128 import *
class CheckedMPU(MPU):
 def step(self):
  assert self.disassemble[self.memory[self.pc]][0]!='???',('unsupported opcode',hex(self.pc),hex(self.memory[self.pc]))
  return super().step()
MPU=CheckedMPU
def machine(rom,mem):return MPU(memory=Memory(rom,mem))
