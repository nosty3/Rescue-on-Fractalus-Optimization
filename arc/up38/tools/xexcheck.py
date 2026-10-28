"""Test .xex w Altirrze (pamięć 1088K albo inna): boot, START po klatce START, losowy joystick i fire, co klatkę
historia CPU sprawdzana pod kątem PC spoza znanego kodu (mapa instrukcji po relokacji). Zrzuty ekranu co SHOT klatek.
Użycie: xexcheck.py XEX FRAMES [START] [SEED] [MEM] [SHOT]"""
import sys, json, random
from paths import WORK
from fx import Emu
from reloc import load_rom, instructions, extend, M

R = WORK
xex = sys.argv[1]; frames = int(sys.argv[2])
start = int(sys.argv[3]) if len(sys.argv) > 3 else 3500
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
mem = sys.argv[5] if len(sys.argv) > 5 else "1088k"
shot = int(sys.argv[6]) if len(sys.argv) > 6 else 0
num = lambda v: int(v.lstrip("$"), 16)
rom = load_rom(f"{R}/build/final.rom")
ins = extend(rom, instructions(json.load(open(f"{R}/cov/all.json"))))
known = {M(a) if b in (0, 1, 15) else a - 0x4000 for b, a in ins} | {0x7F80}
rnd = random.Random(seed)
DIRS = ["c", "c", "n", "s", "e", "w", "ne", "nw", "se", "sw"]
modes = {}
with Emu("pal") as e:
    a = e.a
    a.config("memory", mem); a.config("history", "true")
    a.boot(xex)
    a.bp_set(0x617A); a.frame(8000); a.bp_clear_all()
    if num(a.regs()["PC"]) != 0x617A:
        sys.exit(f"brak przejścia: PC {a.regs()['PC']}")
    for f in range(frames):
        if f == start:
            a.joy(0, "n"); a.frame(30); a.joy(0, "c"); a.frame(30)
            a.consol(start=True); a.frame(10); a.consol()
        elif f > start and f % 20 == 0:
            a.joy(0, rnd.choice(DIRS), fire=rnd.random() < 0.4)
        a.frame(1)
        h = a.history(40000)
        bad = [k for k, x in enumerate(h) if 0x4000 <= num(x["pc"]) < 0xC000 and num(x["pc"]) not in known
               or num(x["pc"]) < 0x0100]
        md = a.peek(0x4a)[0]; modes[md] = modes.get(md, 0) + 1
        if shot and f % shot == 0:
            a.screenshot(f"{R}/xex/shots/chk_{f:05d}.png")
        if bad:
            k = bad[0]
            print(f"klatka {f}: nieznany PC {h[k]['pc']} (tryb $4A {md})")
            for x in h[max(0, k - 30):k + 3]:
                print(" ", x["pc"], x["op"], "A", x["a"], "X", x["x"], "Y", x["y"], "S", x["s"],
                      "irq" if x["irq"] else "", "nmi" if x["nmi"] else "")
            a.screenshot(f"{R}/xex/shots/chk_bad.png")
            break
    else:
        print(f"{frames} klatek bez nieznanego PC; tryby $4A: {modes}")
    a.screenshot(f"{R}/xex/shots/chk_end.png")
