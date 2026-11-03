"""Zawieszenia przy losowym sterowaniu i strzelaniu (hang.py leci neutralnie): start z planu (menu_frames),
potem co 10 ramek losowy kierunek (9) i ogień 50%, przez SEKUNDY emulowanego czasu. Obraz liczony w $B516;
gdy przez 300 ramek nie ma obrazu w trybie lotu ($4A = 2), wypisuje rejestry, bank i ostatnie instrukcje.
Użycie: hangrand.py ROM N_LOTÓW SEKUNDY [SEED]"""
import sys, json, random
from paths import PLAN
from fx import Emu, enter_flight

rom = sys.argv[1]; n = int(sys.argv[2]); secs = int(sys.argv[3]); seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
rnd = random.Random(seed)
plan = json.load(open(PLAN))
starts = [t for t in plan["schedule"] if t["variant"] == "v9"][:n]
dirs = ["c", "n", "s", "e", "w", "ne", "nw", "se", "sw"]
total_ok = 0
for t in starts:
    with Emu("pal") as e:
        a = e.a
        enter_flight(a, rom, t["menu_frames"])
        a.config("history", "true")
        a.bp_set(0xB516)
        frames = 0; imgs = 0; since = 0; ok = True; modes = set()
        while frames < secs * 50:
            if frames % 10 == 0:
                a.joy(0, rnd.choice(dirs), fire=rnd.random() < 0.5)
            t0 = a.clock()["tick"]
            a.frame(10)
            dt = (a.clock()["tick"] - t0) // 35568
            frames += max(dt, 1)
            mode = a.peek(0x4A, 1)[0]; modes.add(mode)
            if a.regs()["PC"] == "$b516":
                imgs += 1; since = 0
            else:
                since += max(dt, 1)
            if since > 300 and mode == 2:
                print("trial", t["trial"], "ZAWIESZENIE po", imgs, "obrazach:", a.regs(), "bank", a.cart_info()["bank"])
                for h in a.history(40)[-40:]:
                    print("   ", h["pc"], h["op"], "A", h["a"], "X", h["x"], "Y", h["y"], "S", h["s"])
                ok = False
                break
        print("trial", t["trial"], "ok" if ok else "BŁĄD", "obrazów", imgs, "ramek", frames, "tryby $4A", sorted(modes), flush=True)
        total_ok += ok
print(f"lotów {n}, bez zawieszenia {total_ok}")
