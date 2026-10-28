"""Walidacja rastermodel.raster na odcinkach z symulatora (v10.1): wejście $982A w banku 2, porównanie occ
($260E..$26FF) po powrocie. Opcjonalnie zbiera dane odcinków do pliku (do analizy odrzucania)."""
import sys, json, pickle
from fxsim import Machine
from rastermodel import raster

rom = open(sys.argv[1], "rb").read()
if rom[:4] == b"CART":
    rom = rom[16:]
d = sys.argv[2]
dump = sys.argv[3] if len(sys.argv) > 3 else None
meta = json.load(open(f"{d}/meta.json"))
ok = bad = 0; segs = []
for m in meta:
    img = bytearray(open(f"{d}/{m['k']:05d}.in", "rb").read()); img[0x42] = 0
    mc = Machine(rom, img, m["bank"], m["regs"])
    mem = mc.mem
    st = {}

    def tr(c):
        global ok, bad
        if not st and c.pc == 0x982A and mem.bank == 2:
            st["ret"] = (mem[0x100 + c.sp + 1] | mem[0x100 + c.sp + 2] << 8) + 1
            st["sp"] = c.sp
            st["L"] = (mem[0x82], mem[0x84], mem[0x86])
            st["R"] = (mem[0x95], mem[0xEA], mem[0xF4])
            st["occ"] = bytearray(mem[0x260E:0x260E + 256])
            st["c0"] = c.processorCycles
        elif st and c.pc == st["ret"] and c.sp == st["sp"] + 2:
            occ = bytearray(st["occ"])
            plots = raster(st["L"], st["R"], occ)
            real = bytes(mem[0x260E:0x260E + 256])
            if bytes(occ[:0xD4]) == real[:0xD4]:
                ok += 1
            else:
                bad += 1
                if bad < 5:
                    diff = [i for i in range(0xD4) if occ[i] != real[i]]
                    print("ROZBIEŻNOŚĆ", st["L"], st["R"], diff[:8], [(occ[i], real[i]) for i in diff[:4]])
            if dump:
                segs.append(dict(L=st["L"], R=st["R"], occ=bytes(st["occ"]), cyc=c.processorCycles - st["c0"]))
            st.clear()

    mc.run(m["pc"], 0xA340 if m["pc"] == 0xA331 else 0xA37E, trace=tr)
print("odcinki zgodne", ok, "niezgodne", bad)
if dump:
    pickle.dump(segs, open(dump, "wb"))
