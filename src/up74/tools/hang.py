"""Szuka zawieszenia: loty z planu (trial z listy) na ROM-ie; gdy przez 300 ramek nie ma obrazu ($B516),
wypisuje rejestry, bank i ostatnie instrukcje z historii CPU. Użycie: hang.py ROM N_PRÓB"""
import sys, json
from paths import PLAN
from fx import Emu, enter_flight

rom = sys.argv[1]; n = int(sys.argv[2])
plan = json.load(open(PLAN))
starts = [t for t in plan["schedule"] if t["variant"] == "v9"][:n]
for t in starts:
    with Emu("pal") as e:
        a = e.a
        enter_flight(a, rom, t["menu_frames"])
        a.config("history", "true")
        a.frame(170)
        a.bp_set(0xB516)
        ok = True
        for k in range(300):
            tb = a.clock()["tick"]
            a.frame(300)
            if a.regs()["PC"] != "$b516":
                print("trial", t["trial"], "ZAWIESZENIE po", k, "obrazach:", a.regs(), "bank", a.cart_info()["bank"],
                      "mode", a.peek(0x4A, 1)[0])
                for h in a.history(40)[-40:]:
                    print("   ", h["pc"], h["op"], "A", h["a"], "X", h["x"], "Y", h["y"], "S", h["s"], "nmi" if h.get("nmi") else "")
                ok = False
                break
        print("trial", t["trial"], "ok" if ok else "BŁĄD")
        if not ok:
            break
