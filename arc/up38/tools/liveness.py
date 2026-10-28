"""Czy bajty strony zerowej (lista) są czytane, zanim zostaną zapisane, po zakończeniu potoku rysowania?
Symulacja od początku połówki pętli ($A32E/$A36C) przez cały obraz i dalej przez następną połówkę;
od momentu wyjścia z fillu ($A340/$A37E) śledzimy odczyty/zapisy (tryby adresowania zp i abs).
Użycie: liveness.py ROM LOOPSCENES_DIR"""
import sys, json
from collections import Counter
from fxsim import Machine

ADDRS = set([0x82, 0x83, 0x84, 0x85, 0x86] + list(range(0x95, 0xA0)) + list(range(0xEA, 0xFF)))
rom = open(sys.argv[1], "rb").read()
rom = rom[16:] if rom[:4] == b"CART" else rom
d = sys.argv[2]
meta = json.load(open(f"{d}/meta.json"))
WAITS = {0x84A0, 0x84A6, 0x9FD5, 0x9FDB}

# tabela trybów: opkod -> (rodzaj dostępu, tryb). Liczymy tylko zp/zp,X/zp,Y/abs/abs,X/abs,Y efektywne adresy.
import py65.devices.mpu6502 as M
dis = M.MPU().disassemble if hasattr(M.MPU(), "disassemble") else None

READ_OPS = set("LDA LDX LDY CMP CPX CPY ADC SBC AND ORA EOR BIT".split())
RMW_OPS = set("ASL LSR ROL ROR INC DEC".split())
WRITE_OPS = set("STA STX STY".split())
from py65.disassembler import Disassembler

reads_first = Counter()
for m in meta:
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read())
    mc = Machine(rom, img, m["bank"], m["regs"])
    mem = mc.mem; c = mc.cpu
    ds = Disassembler(c)
    after = 0xA340 if m["pc"] == 0xA32E else 0xA37E
    stop = 0xA36C if m["pc"] == 0xA32E else 0xA32E
    c.pc = m["pc"]; tracking = False; written = set(); steps = 0; laps = 0
    while True:
        pc = c.pc
        if pc in WAITS:
            mem[0x42] = 0
        if pc == after:
            tracking = True
        if pc == stop and steps:
            laps += 1
            if laps == 2:
                break
        if tracking:
            length, text = ds.instruction_at(pc)
            parts = text.split()
            op = parts[0]
            if len(parts) > 1 and op in READ_OPS | RMW_OPS | WRITE_OPS:
                arg = parts[1]
                ea = None
                if arg.startswith("$") and "," not in arg and "(" not in arg:
                    ea = int(arg[1:], 16)
                elif arg.startswith("$") and arg.endswith(",X"):
                    ea = (int(arg[1:-2], 16) + c.x) & (0xFF if len(arg) == 5 else 0xFFFF)
                elif arg.startswith("$") and arg.endswith(",Y"):
                    ea = (int(arg[1:-2], 16) + c.y) & (0xFF if len(arg) == 5 else 0xFFFF)
                if ea in ADDRS and ea not in written:
                    if op in READ_OPS | RMW_OPS:
                        reads_first[(ea, pc, mem.bank if 0x8000 <= pc < 0xA000 else -1)] += 1
                    if op in WRITE_OPS | RMW_OPS:
                        written.add(ea)
        c.step(); steps += 1
        if steps > 6_000_000:
            raise RuntimeError("limit")
print("odczyty przed zapisem po potoku (adres, PC, bank): liczba")
for k, v in sorted(reads_first.items()):
    print(f"  ${k[0]:02x} @ ${k[1]:04x} bank {k[2]}: {v}")
