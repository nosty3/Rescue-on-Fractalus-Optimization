"""Udział nieba w lotach benchmarku: dla startów z planu nosty3 próbki co ~3 s lotu; r0 = pierwszy niezerowy
wiersz kolumny bufora tuż przed fillem (wiersze 1..43). Użycie: skyprobe.py ROM N_STARTÓW WORKERS"""
import sys, json, statistics
from paths import PLAN
from concurrent.futures import ThreadPoolExecutor
from fx import Emu, enter_flight

rom = sys.argv[1]; n = int(sys.argv[2]); workers = int(sys.argv[3])
plan = json.load(open(PLAN))
starts = [t for t in plan["schedule"] if t["variant"] == "v9"][:n]


def run(t):
    out = []
    with Emu("pal") as e:
        a = e.a
        enter_flight(a, rom, t["menu_frames"]); a.frame(170)
        for k in range(20):
            a.frame(150)
            a.bp_set(0xA33D); a.frame(400); a.bp_clear_all()
            if a.regs()["PC"] != "$a33d" or a.peek(0x4A, 1)[0] != 2:
                break
            mem = bytes(a.memdump(0x1010, 96 * 48))
            r0 = [next((r for r in range(1, 44) if mem[r * 96 + 51 + c]), 44) for c in range(42)]
            out.append(sum(r - 1 for r in r0) / (42 * 43))
    return out


with ThreadPoolExecutor(max_workers=workers) as ex:
    res = list(ex.map(run, starts))
per = [statistics.mean(r) for r in res if r]
print("udział nieba per lot:", [round(x, 2) for x in per])
print("średnio %.3f, mediana %.3f" % (statistics.mean(per), statistics.median(per)))
