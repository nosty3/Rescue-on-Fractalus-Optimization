"""Realny czas VBI w Altirrze: takty od wejścia $B46C do $E462 (z DMA i zagnieżdżonymi DLI), średnio na ramkę.
Użycie: vbitime.py ROM MENU_FRAMES N_RAMEK [SEED]"""
import sys, random
from fx import Emu, enter_flight

rom = sys.argv[1]; mf = int(sys.argv[2]); n = int(sys.argv[3]); seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
rnd = random.Random(seed)
with Emu("pal") as e:
    a = e.a
    enter_flight(a, rom, mf)
    a.frame(170)
    a.bp_set(0xB46C); a.bp_set(0xE462)
    tot = 0; cnt = 0; t0 = None; f0 = a.clock()["tick"]
    while cnt < n:
        if seed and cnt % 25 == 0 and t0 is None:
            a.joy(0, rnd.choice(["c", "n", "s", "e", "w"]), fire=rnd.random() < 0.5)
        a.frame(3)
        pc = a.regs()["PC"]; t = a.clock()["tick"]
        if pc == "$b46c":
            t0 = t
        elif pc == "$e462" and t0 is not None:
            tot += t - t0; cnt += 1; t0 = None
    el = a.clock()["tick"] - f0
print(f"{rom.split('/')[-1]}: VBI średnio {tot/cnt:.1f} taktów/ramkę ({100*tot/el:.2f}% czasu)")
