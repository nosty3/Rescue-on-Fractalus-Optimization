"""Podsumowanie pełnego pomiaru (fullbench.py): średnie FPS (każdy lot z tą samą wagą, jak u nosty3), zyski,
95% przedziały bootstrap (bloki po 5 lotów, 50 000 replikacji), porównanie lot po locie z opublikowanymi
danymi nosty3 (oryginał: results/{video}_isolated_main, v10: results/v10/{video}).
Użycie: fullreport.py FULL.jsonl"""
import sys, json, random, statistics
from paths import NOSTY
from collections import defaultdict
R = f"{NOSTY}/results"
rows = [json.loads(l) for l in open(sys.argv[1])]
by = defaultdict(dict)
for r in rows:
    by[(r["video"], r["version"])][r["trial"]] = r


def boot(a, b, n=50000, seed=2026102303):
    """95% przedział zysku mean(b)/mean(a)-1, losowanie bloków po 5 lotów niezależnie w obu seriach."""
    rnd = random.Random(seed)
    ka, kb = sorted(a), sorted(b)
    blocks_a = [ka[i:i + 5] for i in range(0, len(ka), 5)]
    blocks_b = [kb[i:i + 5] for i in range(0, len(kb), 5)]
    out = []
    for _ in range(n):
        sa = [a[t] for blk in rnd.choices(blocks_a, k=len(blocks_a)) for t in blk]
        sb = [b[t] for blk in rnd.choices(blocks_b, k=len(blocks_b)) for t in blk]
        out.append(sum(sb) / len(sb) / (sum(sa) / len(sa)) - 1)
    out.sort()
    return out[int(0.025 * n)], out[int(0.975 * n)]


for video in ("pal", "ntsc"):
    vers = {v: {t: r["fps"] for t, r in by[(video, v)].items()} for v in ("original", "v10.1", "opus")}
    if not all(vers.values()):
        continue
    print(f"=== {video.upper()} (lotów: " + ", ".join(f"{k} {len(v)}" for k, v in vers.items()) + ")")
    m = {k: statistics.mean(v.values()) for k, v in vers.items()}
    for k in vers:
        print(f"  {k:9s} {m[k]:.4f} FPS  vs oryginał {100*(m[k]/m['original']-1):+6.2f}%")
    lo, hi = boot(vers["original"], vers["opus"], 20000)
    print(f"  opus vs oryginał: 95% bootstrap {100*lo:.2f}..{100*hi:.2f}%")
    common = sorted(set(vers["v10.1"]) & set(vers["opus"]))
    d = [vers["opus"][t] / vers["v10.1"][t] - 1 for t in common]
    print(f"  opus vs v10.1: {100*(m['opus']/m['v10.1']-1):+.2f}% (pary tych samych startów: średnio {100*statistics.mean(d):+.2f}%,"
          f" min {100*min(d):+.1f}%, max {100*max(d):+.1f}%, opus szybszy w {sum(1 for x in d if x > 0)}/{len(d)})")
    ends = {k: sum(1 for t, r in by[(video, k)].items() if r["end"]) for k in vers}
    print(f"  loty zakończone naturalnie przed 60 s: {ends}")
    # zgodność z opublikowanymi danymi nosty3
    for k, path, variant in (("original", f"{R}/{video}_isolated_main/benchmark.json", "original"),
                             ("v10.1", f"{R}/v10/{video}/benchmark.json", None)):
        try:
            pub = json.load(open(path))["rows"]
        except FileNotFoundError:
            continue
        pubfps = {r["trial"]: r["measurement"]["checkpoints"]["60"]["fps"] for r in pub
                  if variant is None or r["variant"] == variant}
        same = sum(1 for t in vers[k] if t in pubfps and abs(pubfps[t] - vers[k][t]) < 1e-9)
        print(f"  {k}: lotów identycznych z opublikowanymi nosty3: {same}/{len(pubfps)}; średnia opublikowana "
              f"{statistics.mean(pubfps.values()):.4f}")
