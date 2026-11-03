"""scene_capture.py ROM OUT N MODE TRIAL [EVERY]: capture 64 KB states at the flight-loop jsr $8309 sites ($A32E/$A36C).
MODE: straight (neutral), random (random stick + fire every 2nd capture), descent (stick up ~1 s / centre ~3 s).
TRIAL: index into the v9 starts of nosty3's plan (menu_frames). EVERY: frames to skip between captures (0 = next)."""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import PLAN
from fx import Emu, enter_flight

rom, out, n_img, mode, trial = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
every = int(sys.argv[6]) if len(sys.argv) > 6 else 0
plan = json.load(open(PLAN))
t = [t for t in plan["schedule"] if t["variant"] == "v9"][trial]
os.makedirs(out, exist_ok=True)
rnd = random.Random(trial * 7 + len(mode))
dirs = ["c", "n", "s", "e", "w", "ne", "nw", "se", "sw"]
meta = []
with Emu("pal") as e:
    a = e.a
    enter_flight(a, rom, t["menu_frames"])
    a.frame(170)
    a.bp_set(0xA32E); a.bp_set(0xA36C)
    k = 0; tries = 0
    while k < n_img and tries < n_img * 3:
        tries += 1
        if mode == "random" and k % 2 == 0:
            a.joy(0, rnd.choice(dirs), fire=rnd.random() < 0.5)
        if mode == "descent":
            a.joy(0, "n" if (k // 3) % 4 == 0 else "c")
        if every:
            a.bp_clear_all(); a.frame(every); a.bp_set(0xA32E); a.bp_set(0xA36C)
        a.frame(400)
        r = a.regs()
        pc = int(r["PC"][1:], 16)
        if pc not in (0xA32E, 0xA36C):
            print("not in flight loop, pc", hex(pc), "mode", a.peek(0x4A, 1)[0]); break
        regs = {k2.lower(): int(v[1:], 16) for k2, v in r.items() if k2 in ("A", "X", "Y", "S", "P")}
        regs["sp"] = regs.pop("s")
        img = bytes(a.memdump(0, 0x10000))
        open(f"{out}/{k:05d}.in", "wb").write(img)
        meta.append(dict(k=k, pc=pc, regs=regs, bank=a.cart_info()["bank"], mode=img[0x4A], tick=a.clock()["tick"]))
        k += 1
json.dump(meta, open(f"{out}/meta.json", "w"))
print("captured", len(meta))
