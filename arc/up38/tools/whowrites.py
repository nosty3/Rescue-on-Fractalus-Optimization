"""Kto i kiedy pisze w adresy (pułapki zapisu): pełna sesja od boot, menu, START, lot z losowym sterowaniem.
Użycie: whowrites.py ROM FRAMES SEED PRESSES ADDR [ADDR...]"""
import sys, random
from collections import Counter
from fx import Emu

rom = sys.argv[1]; frames = int(sys.argv[2]); seed = int(sys.argv[3]); presses = int(sys.argv[4])
addrs = [int(x, 0) for x in sys.argv[5:]]
rnd = random.Random(seed)
hits = Counter()
with Emu("pal") as e:
    a = e.a
    a.boot(rom)
    for ad in addrs:
        a.watch_set(ad, mode="w")
    t0 = a.clock()["tick"]
    started = False; n = 0
    end = t0 + (3100 + frames) * 35568
    while a.clock()["tick"] < end and n < 5000:
        fr = (a.clock()["tick"] - t0) // 35568
        if not started and fr >= 3100:
            for _ in range(presses):
                a.joy(0, "n"); a.frame(30); a.joy(0, "c"); a.frame(30)
            a.consol(start=True); a.frame(100); a.consol(); started = True
        if started and n % 3 == 0:
            a.joy(0, rnd.choice(["c", "n", "s", "e", "w"]), fire=rnd.random() < 0.4)
        tb = a.clock()["tick"]
        a.frame(20)
        r = a.regs()
        ta = a.clock()["tick"]
        fr = (ta - t0) // 35568
        if ta - tb < 20 * 35568 - 200:          # zatrzymane wcześniej = pułapka zapisu
            hits[(r["PC"], a.cart_info()["bank"], a.peek(0x4A, 1)[0], fr // 500 * 500)] += 1
        n += 1
for k, v in sorted(hits.items(), key=lambda kv: kv[0][3]):
    print(f"PC {k[0]} bank {k[1]} $4A={k[2]} ramka~{k[3]}: {v}")
