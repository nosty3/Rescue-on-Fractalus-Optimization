"""Dane do strony-raportu: FPS każdego lotu (oryginał, v10.1, opus; PAL i NTSC) z full155.jsonl oraz drabinka
(L1-L4 z ladder155.jsonl, L5 = opus). Pisze data.js z `window.FX = {...}`.
Użycie: pagedata.py FULL.jsonl LADDER.jsonl OUT.js"""
import sys, json, statistics as st
from collections import defaultdict

full, ladder, out = sys.argv[1:4]
by = defaultdict(dict)
for path in (full, ladder):
    try:
        for line in open(path):
            r = json.loads(line)
            by[(r["video"], r["version"])][r["trial"]] = r
    except FileNotFoundError:
        pass

data = {"flights": {}, "ladder": [], "entrySame": {}}
for video in ("pal", "ntsc"):
    data["flights"][video] = {k: [[t, round(r["fps"], 4)] for t, r in sorted(by[(video, k)].items())]
                              for k in ("original", "v10.1", "opus")}
ref = by[("pal", "v10.1")]
for k in ("L1", "L2", "L3", "L4"):
    rows = by[("pal", k)]
    data["entrySame"][k] = [sum(1 for t in rows if t in ref and rows[t]["entry"] == ref[t]["entry"]), len(rows)]
orig = st.mean(r["fps"] for r in by[("pal", "original")].values())
for k in ("original", "v10.1", "L1", "L2", "L3", "L4", "opus"):
    rows = by[("pal", k)]
    if len(rows) == 155:
        m = st.mean(r["fps"] for r in rows.values())
        data["ladder"].append({"id": k, "fps": round(m, 4), "gain": round(100 * (m / orig - 1), 2)})
open(out, "w", encoding="utf-8").write("window.FX = " + json.dumps(data, separators=(",", ":")) + ";\n")
print(json.dumps({"ladder": data["ladder"], "entrySame": data["entrySame"]}, indent=1))
