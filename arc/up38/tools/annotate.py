"""Adnotacja listingu MADS cyklami z simprof.json: dla podanego banku i pliku .asm (asemblowanego z -l)
wypisuje linie źródła z % cykli potoku i liczbą wykonań na obraz.
Użycie: annotate.py BANK SRC.asm NSCEN [MIN_PCT]"""
import sys, json, subprocess, re, os
from paths import WORK, MADS
bank = int(sys.argv[1]); src = sys.argv[2]; nscen = int(sys.argv[3])
minpct = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
prof = json.load(open(f"{WORK}/simprof.json"))
cyc = {}; cnt = {}
for k, (v, c) in prof.items():
    b, pc = map(int, k.split(":"))
    if b == bank:
        cyc[pc] = v; cnt[pc] = c
total = sum(v for v, c in prof.values())
lst = f"{WORK}/build/obj/annot.lst"
subprocess.run([MADS, src, f"-o:{WORK}/build/obj/annot.bin",
                f"-l:{lst}"], capture_output=True)
for line in open(lst, encoding="latin-1"):
    m = re.match(r"\s*\d+\s+([0-9A-F]{4})\s+((?:[0-9A-F]{2} ?)+)\s*(.*)", line)
    if not m:
        continue
    addr = int(m.group(1), 16)
    if addr in cyc:
        pct = 100 * cyc[addr] / total
        if pct >= minpct:
            print(f"{addr:04X} {pct:5.2f}% x{cnt[addr]/nscen:6.1f}  {m.group(3).strip()}")
