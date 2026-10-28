"""FPS .xex (pamięć rozszerzona) protokołem nosty3 jak fullbench.py: świeży emulator, START po menu_frames z planu
(liczonych od chwili przejścia z intra, bo .xex ładuje się dłużej niż start kartridża), pierwsza pętla lotu,
170 klatek rozgrzewki, licznik gotowych obrazów (po relokacji $7516) przez 60 s taktów.
Wyniki dopisywane do OUT.jsonl. Użycie: xexbench.py XEX OUT.jsonl WORKERS N [MEM] [VIDEO]"""
import sys, json, os, time
from paths import WORK, NOSTY
from concurrent.futures import ThreadPoolExecutor
from fx import Emu, FREQ

xex, out, workers, n = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
mem = sys.argv[5] if len(sys.argv) > 5 else "1088k"
video = sys.argv[6] if len(sys.argv) > 6 else "pal"
R = WORK
plan = json.load(open(f"{NOSTY}/results/ntsc_isolated_main/plan.json"))
trials = [t for t in plan["schedule"] if t["variant"] == "v9"][:n]
done = set()
if os.path.exists(out):
    done = {json.loads(l)["trial"] for l in open(out)}
num = lambda v: int(v.lstrip("$"), 16)


def run(t):
    freq = FREQ[video]
    with Emu(video) as e:
        a = e.a
        a.config("memory", mem)
        a.boot(xex)
        a.bp_set(0x617A); a.frame(8000); a.bp_clear_all()
        assert num(a.regs()["PC"]) == 0x617A
        a.frame(max(1, t["menu_frames"] - 1500))
        a.bp_set(0x632E); a.consol(start=True); a.frame(4000)
        assert num(a.regs()["PC"]) == 0x632E, a.regs()
        a.consol(); a.bp_clear_all()
        a.frame(170)
        a.bp_set(0x7516); a.frame(200)
        assert num(a.regs()["PC"]) == 0x7516
        start = a.clock()["tick"]; events = [0]; end = None
        while events[-1] < 60 * freq:
            a.frame(200)
            packed = a.eval_expr("pc+65536*db($4a)")
            mode, pc = packed >> 16, packed & 0xFFFF
            tick = a.clock()["tick"] - start
            if mode != 2:
                end = dict(mode=mode, pc=pc, at=tick / freq); break
            assert pc == 0x7516, hex(pc)
            events.append(tick)
        a.bp_clear_all()
    k = len(events) - 1
    fps = k / (events[-1] / freq) if k else 0
    return dict(video=video, version="xex", mem=mem, trial=t["trial"], fps=fps, intervals=k, end=end)


jobs = [t for t in trials if t["trial"] not in done]
t0 = time.time()
with ThreadPoolExecutor(max_workers=workers) as ex, open(out, "a") as f:
    for r in ex.map(run, jobs):
        f.write(json.dumps(r) + "\n"); f.flush()
print("KONIEC", len(jobs), f"{time.time() - t0:.0f}s")
