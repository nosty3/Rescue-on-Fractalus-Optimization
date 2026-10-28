"""Drabinka zysków: te same 155 startów "v9" z planu nosty3, ten sam protokół co fullbench.py, dla buildów
pośrednich (każdy dokłada jedną łatkę). Wyniki dopisywane do OUT.jsonl (wznawialne).
Użycie: ladderbench.py OUT.jsonl WORKERS VIDEO NAZWA=ŚCIEŻKA.car ..."""
import sys, json, os, time
from paths import WORK, NOSTY
from concurrent.futures import ThreadPoolExecutor
from fx import Emu, enter_flight, measure

out = sys.argv[1]; workers = int(sys.argv[2]); video = sys.argv[3]
roms = dict(a.split("=", 1) for a in sys.argv[4:])
R = WORK
plan = json.load(open(f"{NOSTY}/results/ntsc_isolated_main/plan.json"))
done = set()
if os.path.exists(out):
    for line in open(out):
        r = json.loads(line); done.add((r["video"], r["version"], r["trial"]))
jobs = [(name, rom, t) for t in plan["schedule"] if t["variant"] == "v9"
        for name, rom in roms.items() if (video, name, t["trial"]) not in done]


def run(job):
    name, rom, t = job
    with Emu(video) as e:
        h = enter_flight(e.a, rom, t["menu_frames"])
        m = measure(e.a, video, 60)
    return dict(video=video, version=name, trial=t["trial"], block=t["block"], menu_frames=t["menu_frames"],
                entry=h[:16], fps=m["fps"], intervals=m["intervals"], seconds=m["seconds"], end=m["end"])


t0 = time.time(); n = 0
with ThreadPoolExecutor(max_workers=workers) as ex, open(out, "a") as f:
    for r in ex.map(run, jobs):
        f.write(json.dumps(r) + "\n"); f.flush(); n += 1
        if n % 50 == 0:
            print(f"{n}/{len(jobs)} {time.time()-t0:.0f}s", flush=True)
print("KONIEC", n, "lotów", f"{time.time()-t0:.0f}s")
