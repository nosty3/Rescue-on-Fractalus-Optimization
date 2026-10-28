"""Uruchamia oba symulatory w kroku (xexsim.py) od stanu RUN kartridża, z decyzjami relokacji z xex/decisions.json.
Scenariusz wejścia: START wciśnięty w klatkach [START, START+8), potem losowy joystick i fire co 20 klatek.
Użycie: xexrun.py STEPS [SEED] [START_FRAME] [--stop ADDR]"""
import sys, json, random, time, os
from paths import WORK
from reloc import load_rom, instructions, extend, build
import xexsim

R = WORK
HERE = os.path.dirname(os.path.abspath(__file__))
steps = int(float(sys.argv[1]))
seed = int(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else 1
start = int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else 300
stop = int(sys.argv[sys.argv.index("--stop") + 1], 0) if "--stop" in sys.argv else None

rom = load_rom(f"{R}/build/final.rom")
ins = extend(rom, instructions(json.load(open(f"{R}/cov/all.json"))))
dec = json.load(open(os.path.join(HERE, "..", "xex", "decisions.json")))
ext, log = build(rom, ins, dec)
state = sys.argv[sys.argv.index("--state") + 1] if "--state" in sys.argv else "post"
img = open(f"{R}/xex/{state}.img", "rb").read()
regs = json.load(open(f"{R}/xex/{state}.json"))
resident = ext[0][:0x2000] + ext[1][:0x2000] if state == "post" else None
rnd = random.Random(seed)
DIRS = [0xFF, 0xFE, 0xFD, 0xFB, 0xF7, 0xFA, 0xF6, 0xF9, 0xF5]   # środek, góra, dół, lewo, prawo, skosy
plan = {}


def inputs(f):
    if start <= f < start + 8:
        return {"consol": 0x06}
    if f >= start + 60:
        k = f // 20
        if k not in plan:
            plan[k] = {"porta": rnd.choice(DIRS), "trig": 0 if rnd.random() < 0.4 else 1}
        return plan[k]
    return {}


t0 = time.time()
r = xexsim.run(rom, ext, img, regs, steps, inputs, report_every=500_000, stop_at=stop, resident=resident)
print(f"wynik: ok={r['ok']} krok {r['step']} ({time.time() - t0:.0f} s) {r['why']}")
if not r["ok"]:
    print("ostatnie kroki (PC A, PC B, bank, A X Y [A], A X Y [B]):")
    for t in r["trail"][-25:]:
        print(f"  ${t[0]:04x} ${t[1]:04x} b{t[2]:<2} | {t[3]:02x} {t[4]:02x} {t[5]:02x} | {t[6]:02x} {t[7]:02x} {t[8]:02x}")
    lm = sorted(xexsim.run.last_mapped.items(), key=lambda x: -x[1][2])[:12]
    print("ostatnie zmapowane zapisy (adres <- PC bank krok A/B):")
    for ad, (pc, b, st, va, vb) in lm:
        if ad < 0x100 or ad >= 0x200:
            print(f"  ${ad:04x} <- ${pc:04x} b{b} krok {st} ${va:02x}/${vb:02x}")
else:
    print("klatka:", r.get("frame"), "DLI:", r.get("dli"))
    mw = r["mapped_w"]
    print(f"zapisy ze zmapowaną wartością: {len(mw)} miejsc")
    for k, v in sorted(mw.items())[:60]:
        print(f"  PC ${k[0]:04x} bank {k[1]} -> ${k[2]:04x} {k[3]} x{v}")
