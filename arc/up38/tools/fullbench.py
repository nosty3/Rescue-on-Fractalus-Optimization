"""Pełny pomiar protokołem nosty3 (docs/benchmarks/METHOD_PL.md): po 155 lotów na wersję i standard, świeży proces
emulatora, zimny start, START po menu_frames z jego zamrożonego planu (ziarno 2026102303), 170 ramek rozgrzewki,
joystick w środku, licznik gotowych obrazów w $B516, okno 60 s z taktów emulowanego Atari, loty zakończone
naturalnie zostają w średniej. Oryginał na starty "original" z planu, v10.1 i nasz na starty "v9" (jak jego v10).
Wyniki dopisywane na bieżąco do OUT.jsonl (wznawialne). Użycie: fullbench.py OUT.jsonl WORKERS [pal|ntsc ...]"""
import sys, json, os, time
from paths import WORK, NOSTY
from concurrent.futures import ThreadPoolExecutor
from fx import Emu, enter_flight, measure

out = sys.argv[1]; workers = int(sys.argv[2]); videos = sys.argv[3:] or ["pal", "ntsc"]
R = WORK
ROMS = {"original": (f"{NOSTY}/original/Rescue on Fractalus!.rom", "original"),
        "v10.1": (f"{NOSTY}/optimized version/Rescue on Fractalus! - optimized 128KB.car", "v9"),
        "opus": (f"{R}/build/final.car", "v9")}
plan = json.load(open(f"{NOSTY}/results/ntsc_isolated_main/plan.json"))
done = set()
if os.path.exists(out):
    for line in open(out):
        r = json.loads(line); done.add((r["video"], r["version"], r["trial"]))
jobs = []
for video in videos:
    for t in plan["schedule"]:
        for name, (rom, sched) in ROMS.items():
            if t["variant"] == sched and (video, name, t["trial"]) not in done:
                jobs.append((video, name, rom, t))


def run(job):
    video, name, rom, t = job
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
