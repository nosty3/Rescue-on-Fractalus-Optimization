"""Dopisuje ręczne decyzje relokacji do xex/decisions.json (pole "manual") i przelicza heurystykę (autodec.py).
Użycie: xexdec.py RODZAJ BANK ADRES [ADRES...]      (RODZAJ: hi, bank, keep, word, hibyte, bankbyte)
        xexdec.py wordtab|hitab BANK ADRES LICZBA
        xexdec.py patch BANK ADRES HEX"""
import sys, json, os, subprocess
from paths import WORK
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "..", "xex", "decisions.json")
d = json.load(open(p))
m = d.setdefault("manual", {})
kind, bank = sys.argv[1], int(sys.argv[2], 0)
if kind in ("wordtab", "hitab"):
    m.setdefault(kind, []).append([bank, int(sys.argv[3], 0), int(sys.argv[4], 0)])
elif kind == "patch":
    m.setdefault(kind, []).append([bank, int(sys.argv[3], 0), sys.argv[4]])
else:
    for a in sys.argv[3:]:
        e = [bank, int(a, 0)]
        if e not in m.setdefault(kind, []):
            m[kind].append(e)
json.dump(d, open(p, "w"), indent=0)
subprocess.run([sys.executable, os.path.join(HERE, "autodec.py"), f"{WORK}/build/final.rom",
                f"{WORK}/cov/all.json", p], check=True, capture_output=True)
print("ręczne:", {k: len(v) for k, v in m.items()})
