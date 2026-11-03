"""All simulator checks of v14 in one command, on the sample states in work/scenes (py65 + MADS, no emulator).
  1. rebuild v14 from src/ (tools/build.py) and compare with bin/fractalus_v14.rom byte for byte
  2. apply bin/v14_from_v11.ips to work/base/v11.rom and compare
  3. reference ROMs for the tools that need the same caller code on both sides:
       ref_b5   = v14 with bank 5 (rasteriser) taken from v11      -> fuzzseg.py, fuzzseg2.py
       ref_proj = build of the first 7 patches (without proj2 loop2) -> fuzzloop.py
     every other check compares v11 directly with v14
  4. the checks; each must report 0 mismatches
Usage: python tools/check_v14.py [--full]
  --full: larger N plus the exhaustive tests (65536 multiplications, 16384 scene headings); about an hour.
Expected known differences (dead state, printed but not counted): fuzzloop "different P" with xor bit 64 only
(V flag at $88E8, loop2), register differences at the rasteriser return (fuzzseg/fuzzseg2 finish the pipeline
with both register sets and compare the result)."""
import os, re, sys, subprocess, hashlib

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PKG, "tools"))
from paths import WORK  # noqa: E402

FULL = "--full" in sys.argv
PATCHES = "v11src vbi2_mul vbi2_sound vbi2_interp scene_grid scene_pre reorder proj2 loop2".split()
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
V11 = f"{WORK}/base/v11.rom"
UP = os.path.join(PKG, "bin", "fractalus_v14.rom")
SC = f"{WORK}/scenes"


def py(*args):
    r = subprocess.run([sys.executable, *args], cwd=PKG, env=ENV, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


rows = []


def report(name, ok, detail):
    rows.append((name, ok, detail))
    print(f"[{'OK' if ok else 'FAIL'}] {name}: {detail}", flush=True)


# 1. rebuild
rc, out = py("tools/build.py", "--name=v14_check", *PATCHES)
built = f"{WORK}/build/v14_check.rom"
report("rebuild from src/", rc == 0 and os.path.exists(built) and open(built, "rb").read() == open(UP, "rb").read(),
       out.strip().splitlines()[-1] if out.strip() else "no output")

# 2. IPS
v11 = bytearray(open(V11, "rb").read()); p = open(os.path.join(PKG, "bin", "v14_from_v11.ips"), "rb").read()
i = 5
while p[i:i + 3] != b"EOF":
    off = int.from_bytes(p[i:i + 3], "big"); n = int.from_bytes(p[i + 3:i + 5], "big"); i += 5
    if n == 0:
        cnt = int.from_bytes(p[i:i + 2], "big"); v11[off:off + cnt] = p[i + 2:i + 3] * cnt; i += 3
    else:
        v11[off:off + n] = p[i:i + n]; i += n
report("IPS on v11.rom", bytes(v11) == open(UP, "rb").read(), f"result sha {hashlib.sha256(v11).hexdigest()[:16]}")

# 3. reference ROMs
up = open(UP, "rb").read(); base = open(V11, "rb").read()
ref_b5 = f"{WORK}/build/ref_b5.rom"
open(ref_b5, "wb").write(up[:5 * 8192] + base[5 * 8192:6 * 8192] + up[6 * 8192:])
rc, out = py("tools/build.py", "--name=ref_proj", *PATCHES[:7])
ref_proj = f"{WORK}/build/ref_proj.rom"
report("reference ROMs", rc == 0, f"ref_b5 {sha(ref_b5)[:16]}, ref_proj {sha(ref_proj)[:16]}")

# 4. checks: (name, args, count regex)
N = (lambda quick, full: str(full if FULL else quick))
checks = [
    ("equiv v11 -> v14 (pipeline)", ["tools/equiv.py", "--hd152", V11, UP, f"{SC}/f_n", f"{SC}/f_r1"]),
    ("equivwait v11 -> v14 (work in the beam wait)",
     ["tools/equivwait.py", "--hd152"] + ([] if FULL else ["--n=0,3,10,1000"]) + [V11, UP, f"{SC}/f_n"]
     + ([f"{SC}/f_r1"] if FULL else [])),
    ("fuzzseg2 ref_b5 -> v14 (rasteriser)", ["tools/fuzzseg2.py", ref_b5, UP, f"{SC}/f_n", N(300, 5000), "1", "--hd152"]),
    ("fuzzseg ref_b5 -> v14 (rasteriser)", ["tools/fuzzseg.py", ref_b5, UP, f"{SC}/f_r1", N(300, 3000), "2", "--hd152"]),
    ("fuzzfill v11 -> v14 (fill)", ["tools/fuzzfill.py", V11, UP, N(500, 10000), "1"]),
    ("fuzzproj v11 -> v14 (projection)", ["tools/fuzzproj.py", V11, UP, f"{SC}/f_n", N(1000, 30000), "1"]),
    ("fuzzloop ref_proj -> v14 (edge loop)", ["tools/fuzzloop.py", ref_proj, UP, f"{SC}/f_n", N(100, 2000), "1"]),
    ("vbieq v11 -> v14 (VBI)", ["tools/vbieq.py", V11, UP, f"{SC}/vbi_r7", "--ignore=28d6", "--poison=1"]),
    ("scene_eq8309 v11 -> v14 (jsr $8309)", ["tools/scene_eq8309.py", V11, UP, f"{SC}/scene_rnd"]),
    ("scene_fuzz8309 v11 -> v14", ["tools/scene_fuzz8309.py", V11, UP, f"{SC}/scene_rnd", N(500, 4000), "1"]),
    ("scene_post_fuzz v11 -> v14", ["tools/scene_post_fuzz.py", V11, UP, N(500, 20000), f"{SC}/scene_rnd"]),
]
if FULL:
    checks += [("scene_exh_pre v11 -> v14 (all headings)", ["tools/scene_exh_pre.py", V11, UP, f"{SC}/scene_rnd"]),
               ("mul_exhaustive v11 -> v14 (65536 pairs)", ["tools/mul_exhaustive.py", V11, UP, f"{SC}/vbi_r7"])]
for name, args in checks:
    rc, out = py(*args)
    m = re.findall(r"(?:niezgodnych|mismatches)\s+(\d+)", out)
    pm = re.findall(r"różne flagi P (\d+)", out)
    last = out.strip().splitlines()[-1] if out.strip() else "no output"
    ok = rc == 0 and bool(m) and int(m[-1]) == 0 and (not pm or int(pm[-1]) == 0)
    report(name, ok, last)

bad = [r for r in rows if not r[1]]
print(f"\n{len(rows) - len(bad)}/{len(rows)} OK" + ("" if not bad else "; FAILED: " + ", ".join(r[0] for r in bad)))
sys.exit(1 if bad else 0)
