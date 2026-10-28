"""Sumy cykli z simprof.json pogrupowane po etykietach źródła (listing MADS). Etykieta = ostatnia etykieta
w kolumnie 1 przed instrukcją; grupa = etykieta bez prefiksu głębokości dN_ i sufiksu adresu.
Użycie: labelsum.py BANK SRC.asm NSCEN [TOP]"""
import sys, json, subprocess, re
from paths import WORK, MADS
from collections import Counter
bank = int(sys.argv[1]); src = sys.argv[2]; nscen = int(sys.argv[3]); top = int(sys.argv[4]) if len(sys.argv) > 4 else 50
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
label = "?"; bylab = Counter(); bygrp = Counter(); entries = Counter()
for line in open(lst, encoding="latin-1"):
    m = re.match(r"\s*\d+\s+([0-9A-F]{4})\s+((?:[0-9A-F]{2} ?)+)\s*(.*)", line)
    lm = re.match(r"\s*\d+\s+(?:[0-9A-F]{4}\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*$", line)
    if lm and not m:
        label = lm.group(1); continue
    if m:
        txt = m.group(3).strip()
        parts = txt.split()
        if parts and not txt.startswith(" ") and len(parts) >= 2 and re.match(r"[A-Za-z_]", parts[0]) and parts[0].upper() not in (
                "LDA", "STA", "LDX", "LDY", "STX", "STY", "CMP", "CPX", "CPY", "ADC", "SBC", "AND", "ORA", "EOR",
                "BCC", "BCS", "BEQ", "BNE", "BMI", "BPL", "BVC", "BVS", "JMP", "JSR", "INC", "DEC", "ASL", "LSR",
                "ROL", "ROR", "BIT", "DTA"):
            label = parts[0]
        a = int(m.group(1), 16)
        if a in cyc:
            bylab[label] += cyc[a]
            g = re.sub(r"^d\d+_", "", label); g = re.sub(r"_?[0-9a-f]{4}$", "", g); g = re.sub(r"\d+$", "", g)
            bygrp[g] += cyc[a]
print("GRUPY:")
for g, v in bygrp.most_common(top):
    print(f"  {g:30s} {100*v/total:5.2f}%")
print("ETYKIETY:")
for g, v in bylab.most_common(top):
    print(f"  {g:30s} {100*v/total:5.2f}%")
