"""RAM at the flight entry of two ROMs: cold boot, START after menu_frames of plan entry TRIAL (as bench.py), stop
at the first $A32E and compare RAM $0000-$7FFF. 0 differences = both ROMs enter the same flight (same planet).
Used in round 2 after every change that touched free $FF bytes (see the bank 3 $963A-$97F0 pitfall in AGENT.md).
Usage: entrydiff.py ROM_A ROM_B TRIAL [pal|ntsc]"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import PLAN  # noqa: E402
from fx import Emu, enter_flight  # noqa: E402

video = sys.argv[4] if len(sys.argv) > 4 else "pal"
plan = json.load(open(PLAN))
t = [t for t in plan["schedule"] if t["variant"] == "v9"][int(sys.argv[3])]
mems = []
for rom in sys.argv[1:3]:
    with Emu(video) as e:
        enter_flight(e.a, rom, t["menu_frames"])
        mems.append(bytes(e.a.memdump(0, 0x8000)))
d = [i for i in range(0x8000) if mems[0][i] != mems[1][i]]
print(f"trial {t['trial']} menu_frames {t['menu_frames']}: {len(d)} bytes differ",
      [(hex(i), mems[0][i], mems[1][i]) for i in d[:40]])
