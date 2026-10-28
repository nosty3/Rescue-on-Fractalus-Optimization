"""Kto w pętli lotu sięga do RAM-u [LO, HI] (domyślnie $4000-$7FFF, mapa terenu)? Symulacja pełnej połówki
pętli ($A32E -> $A36C albo odwrotnie) na nagranych scenach; dla każdej instrukcji liczymy adres efektywny
(abs, abs,X, abs,Y, (zp),Y, (zp,X)) i zbieramy (bank, PC, tekst instrukcji, zakres adresów).
Użycie: maptrace.py ROM LOOPSCENES_DIR [LO HI]"""
import sys, json
from collections import defaultdict
from fxsim import Machine
from py65.disassembler import Disassembler

rom = open(sys.argv[1], "rb").read()
rom = rom[16:] if rom[:4] == b"CART" else rom
d = sys.argv[2]
lo = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x4000
hi = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0x7FFF
meta = json.load(open(f"{d}/meta.json"))
WAITS = {0x84A0, 0x84A6, 0x9FD5, 0x9FDB}
MEMOPS = set("LDA LDX LDY CMP CPX CPY ADC SBC AND ORA EOR BIT ASL LSR ROL ROR INC DEC STA STX STY JMP JSR".split())

hits = defaultdict(lambda: [0, 0xFFFF, 0])   # (bank, pc, text) -> [liczba, min ea, max ea]
for m in meta:
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read())
    mc = Machine(rom, img, m["bank"], m["regs"])
    mem = mc.mem; c = mc.cpu
    ds = Disassembler(c)
    stop = 0xA36C if m["pc"] == 0xA32E else 0xA32E
    c.pc = m["pc"]; steps = 0
    while True:
        pc = c.pc
        if pc in WAITS:
            mem[0x42] = 0
        if pc == stop and steps:
            break
        length, text = ds.instruction_at(pc)
        parts = text.split()
        if len(parts) > 1 and parts[0] in MEMOPS and parts[1].startswith(("$", "(")):
            arg = parts[1]; ea = None
            if arg.startswith("($") and arg.endswith("),Y"):
                z = int(arg[2:4], 16)
                ea = (mem[z] | mem[(z + 1) & 0xFF] << 8) + c.y
            elif arg.startswith("($") and arg.endswith(",X)"):
                z = (int(arg[2:4], 16) + c.x) & 0xFF
                ea = mem[z] | mem[(z + 1) & 0xFF] << 8
            elif arg.startswith("$"):
                base = arg.split(",")[0]
                v = int(base[1:], 16)
                if arg.endswith(",X"):
                    v += c.x
                elif arg.endswith(",Y"):
                    v += c.y
                ea = v & (0xFF if len(base) == 3 else 0xFFFF)
            if ea is not None and lo <= ea <= hi and parts[0] not in ("JMP", "JSR"):
                k = (mem.bank if 0x8000 <= pc < 0xA000 else -1, pc, text)
                h = hits[k]; h[0] += 1; h[1] = min(h[1], ea); h[2] = max(h[2], ea)
        c.step(); steps += 1
        if steps > 8_000_000:
            raise RuntimeError("limit")

print(f"sceny: {len(meta)}; instrukcje sięgające do ${lo:04X}-${hi:04X}: {len(hits)}")
for (b, pc, text), (n, a, z) in sorted(hits.items()):
    print(f"  bank {b:2d} ${pc:04X}  {text:22s} x{n:7d}  ${a:04X}-${z:04X}")
