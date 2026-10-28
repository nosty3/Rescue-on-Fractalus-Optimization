"""Benchmark FPS wg protokołu nosty3: zimny start, START po menu_frames z ich planu (te same momenty dla
każdego ROM-u = pary), 170 ramek rozgrzewki, licznik obrazów w $B516, czas z taktów emulowanego Atari.
Użycie: bench.py VIDEO N_PRÓB SEKUNDY WORKERS OUT.json ROM1 [ROM2 ...]"""
import sys, json, time, statistics
from paths import PLAN
from concurrent.futures import ThreadPoolExecutor
from fx import Emu, enter_flight, measure

video, n, secs, workers, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
roms = sys.argv[6:]
plan = json.load(open(PLAN))
starts = [t for t in plan["schedule"] if t["variant"] == "v9"][:n]
jobs = [(r, t) for t in starts for r in roms]


def run(job):
    rom, t = job
    with Emu(video) as e:
        h = enter_flight(e.a, rom, t["menu_frames"])
        m = measure(e.a, video, secs)
    return dict(rom=rom, trial=t["trial"], menu_frames=t["menu_frames"], entry=h[:16], fps=m["fps"],
                intervals=m["intervals"], end=m["end"])


t0 = time.time()
with ThreadPoolExecutor(max_workers=workers) as ex:
    rows = list(ex.map(run, jobs))
json.dump(rows, open(out, "w"), indent=1)
base = [r for r in rows if r["rom"] == roms[0]]
print(f"{len(rows)} lotów, {time.time()-t0:.0f}s")
for rom in roms:
    rs = [r for r in rows if r["rom"] == rom]
    mean = statistics.mean(r["fps"] for r in rs)
    line = f"{rom.split('/')[-1][:40]:40s} {mean:.4f} FPS"
    if rom != roms[0]:
        diffs = [b["fps"] / a["fps"] - 1 for a, b in zip(base, rs)]
        line += f"  vs pierwszy: {100*(mean/statistics.mean(r['fps'] for r in base)-1):+.2f}%" \
                f" (pary: średnio {100*statistics.mean(diffs):+.2f}%, min {100*min(diffs):+.1f}%, max {100*max(diffs):+.1f}%)"
        same_entry = sum(1 for a, b in zip(base, rs) if a["entry"] == b["entry"])
        line += f", identyczne wejście {same_entry}/{len(rs)}"
    print(line)
