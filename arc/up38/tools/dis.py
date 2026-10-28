"""Deasembler fragmentu pamięci ze sceny (64 KB obraz + ROM z bankiem). Użycie: dis.py ROM SCENE.in BANK START END"""
import sys
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
from fxsim import Mem

rom = open(sys.argv[1], "rb").read()
if rom[:4] == b"CART":
    rom = rom[16:]
img = bytearray(open(sys.argv[2], "rb").read())
mem = Mem(img); mem.setup(rom); mem.select(int(sys.argv[3]))
mpu = MPU(memory=mem)
d = Disassembler(mpu)
a = int(sys.argv[4], 16); end = int(sys.argv[5], 16)
while a < end:
    n, txt = d.instruction_at(a)
    print(f"{a:04X} {bytes(mem[a:a+n]).hex():8s} {txt}")
    a += n
