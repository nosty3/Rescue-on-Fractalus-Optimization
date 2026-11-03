"""Składa paczkę rundy 2 dla nosty3 (i jego agenta): fractalus v14 = v11 + 9 łatek rundy 2 (build s2_m8).
Zawartość: README EN/PL + AGENT.md + worklog (z <WORK>/handoff74/docs), źródła i generatory buildu v14,
narzędzia weryfikacji (+ przenośne kopie skryptów rundy 2 spoza repo z <WORK>/handoff74/extra), pliki gry,
łatka IPS z v11, ROM bazowy v11 (work/base), próbka nagranych stanów (work/scenes), wyniki 155 lotów, raport.
Wynik: <WORK>/release/<NAZWA>/ i <NAZWA>.zip obok (w zipie folder i tak nazywa się fractalus-v14).
Użycie: mkhandoff74.py [NAZWA_KATALOGU]   (domyślnie fractalus-v14)"""
import os, shutil, json, sys, hashlib, zipfile
from paths import WORK

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = sys.argv[1] if len(sys.argv) > 1 else "fractalus-v14"
OUT = f"{WORK}/release/{NAME}"
H74 = f"{WORK}/handoff74"
if os.path.exists(OUT):
    sys.exit(f"{OUT} już istnieje: usuń go najpierw (u nas: safe_delete.py -r)")

CAR_SHA = "8362476209a3740162c304b0eff710615af45656838f5f9a88fbe63e88160526"
V11_SHA = "ec01982121b70baca35f04568617965c3164e716e0a5eb3c6ebcbb123566a868"
PATCHES = "v11src vbi2_mul vbi2_sound vbi2_interp scene_grid scene_pre reorder proj2 loop2".split()

# źródła: src/v11 (łatka v11src) + pliki asm 8 pozostałych łatek (statyczne i generowane w czasie buildu)
SRC_STATIC = ["vbi2_mul", "vbi2_snd14", "vbi2_interp14", "vbi2_lerp", "vbi2_wrap",
              "reorder_b2", "reorder_b2w", "reorder_b3"]
SRC_GEN = ["scene_b10", "scene_b11", "scene_b12", "scene_b13", "scene_b4", "scene_post2",
           "proj3", "proj_fill14_0", "proj_fill14_1", "proj_fill14_2", "proj_pst2", "proj_pst3", "proj_ovf1",
           "proj_loop2", "proj_ptab2", "proj_fnb2"]
TOOLS = ["build", "paths", "patches_vbi2", "patches_scene", "patches_reorder", "patches_proj",
         "gen_proj", "gen_scene", "gen_scene7", "gen_vbi2_mul", "gen_fill9",
         "equiv", "equivwait", "fuzzseg", "fuzzseg2", "fuzzfill", "fuzzproj", "fuzzloop",
         "hang", "hangrand", "tearcheck", "vbieq", "vbisim", "bench", "fx", "fxsim",
         "capture", "capture_vbi", "mkhandoff74"]
EXTRA = ["entrydiff", "mul_exhaustive", "scene_capture", "scene_eq8309", "scene_fuzz8309", "scene_exh_pre",
         "scene_post_fuzz", "capture_vbi2", "check_v14"]
# próbka stanów (pełne zestawy to 229 MB): katalog źródłowy -> nazwa w work/scenes, liczba stanów
SCENES = [(f"{WORK}/scenes/f_n", "f_n", 24), (f"{WORK}/scenes/f_r1", "f_r1", 24),
          (f"{WORK}/s2vbi/cap/c_r7", "vbi_r7", 24), (f"{WORK}/s2scene/c_rnd", "scene_rnd", 24)]


def cp(src, dst):
    d = os.path.join(OUT, dst)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.copy2(src, d)


def put(dst, data, text=False):
    d = os.path.join(OUT, dst)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    if text:
        open(d, "w", encoding="utf-8", newline="\n").write(data)
    else:
        open(d, "wb").write(data)


def subst(text, reps, what):
    for a, b in reps:
        assert text.count(a) == 1, (what, a)
        text = text.replace(a, b)
    return text


def ips(old, new):
    """Łatka IPS (rekordy ciągłych zmian, max 65535 B) - jak w mkhandoff.py."""
    out = bytearray(b"PATCH"); i = 0
    while i < len(new):
        if old[i] == new[i]:
            i += 1; continue
        j = i
        while j < len(new) and j - i < 0xFFFF and (old[j] != new[j] or (j + 1 < len(new) and old[j + 1] != new[j + 1])):
            j += 1
        assert i != 0x454F46
        out += i.to_bytes(3, "big") + (j - i).to_bytes(2, "big") + new[i:j]
        i = j
    return bytes(out + b"EOF")


def apply_ips(old, patch):
    data = bytearray(old); p = 5
    while patch[p:p + 3] != b"EOF":
        off = int.from_bytes(patch[p:p + 3], "big"); n = int.from_bytes(patch[p + 3:p + 5], "big")
        data[off:off + n] = patch[p + 5:p + 5 + n]; p += 5 + n
    return bytes(data)


os.makedirs(OUT)
for f in ("README.md", "README_PL.md", "AGENT.md"):
    cp(f"{H74}/docs/{f}", f)
cp(f"{H74}/docs/worklog_pl.md", "docs/worklog_pl.md")
cp(f"{H74}/docs/results.md", "results/results.md")

for f in sorted(os.listdir(f"{ROOT}/src/v11")):
    if f.endswith(".asm"):
        cp(f"{ROOT}/src/v11/{f}", f"src/v11/{f}")
for n in SRC_STATIC + SRC_GEN:
    cp(f"{ROOT}/src/{n}.asm", f"src/{n}.asm")
for n in TOOLS:
    t = open(f"{ROOT}/tools/{n}.py", encoding="utf-8").read()
    if n == "fx":    # klon nosty3 z paths.NOSTY (FRACTALUS_NOSTY), nie na sztywno <WORK>/repo
        t = subst(t, [("from paths import WORK, BRIDGE\n", "from paths import WORK, BRIDGE, NOSTY\n"),
                      ('REPO = f"{WORK}/repo"', "REPO = NOSTY")], n)
    if n == "paths":  # w paczce domyślny katalog roboczy = <paczka>/work (bez naszego dysku G:)
        t = subst(t, [('WORK = os.environ.get("FRACTALUS_WORK", "G:/tmp/claude/atari/fractalus" if os.path.isdir("G:/tmp/claude/atari/fractalus")\n'
                       '                      else _local).replace("\\\\", "/")',
                       'WORK = os.environ.get("FRACTALUS_WORK", _local).replace("\\\\", "/")')], n)
    put(f"tools/{n}.py", t, text=True)
for n in EXTRA:
    cp(f"{H74}/extra/{n}.py", f"tools/{n}.py")
assert not any('"G:/' in open(f"{OUT}/tools/{f}", encoding="utf-8").read() for f in os.listdir(f"{OUT}/tools")
               if f not in ("mkhandoff74.py",)), "ścieżka G:/ w kodzie narzędzi paczki (w docstringach wolno)"

# pliki gry + IPS z v11
car = open(f"{WORK}/build/s2_m8.car", "rb").read()
rom = open(f"{WORK}/build/s2_m8.rom", "rb").read()
assert hashlib.sha256(car).hexdigest() == CAR_SHA and car[16:] == rom
assert open(f"{WORK}/release/fractalus-v14.car", "rb").read() == car
v11 = open(f"{WORK}/base/v11.rom", "rb").read()
assert hashlib.sha256(v11).hexdigest() == V11_SHA
patch = ips(v11, rom)
assert apply_ips(v11, patch) == rom
put("bin/fractalus_v14.car", car)
put("bin/fractalus_v14.rom", rom)
put("bin/v14_from_v11.ips", patch)
put("work/base/v11.rom", v11)   # = "optimized version/Rescue on Fractalus! - optimized 128KB.rom" z repo nosty3 @3726a11

# próbka nagranych stanów
for src, name, n in SCENES:
    meta = json.load(open(f"{src}/meta.json"))[:n]
    for m in meta:
        cp(f"{src}/{m['k']:05d}.in", f"work/scenes/{name}/{m['k']:05d}.in")
    put(f"work/scenes/{name}/meta.json", json.dumps(meta), text=True)

# wyniki i raport
for s in ("pal", "pal_descent", "ntsc", "ntsc_descent"):
    cp(f"{WORK}/s2full155_m8_{s}.json", f"results/full155_v14_{s}.json")
cp(f"{WORK}/page2/fractalus-runda2.html", "report/index.html")

# bez długich myślników w tekstach dla ludzi
for f in ("README.md", "README_PL.md", "AGENT.md", "docs/worklog_pl.md", "results/results.md"):
    t = open(f"{OUT}/{f}", encoding="utf-8").read()
    assert "\u2014" not in t and "\u2013" not in t, f

# sumy kontrolne
lines = []
for dp, _, fs in os.walk(OUT):
    for f in sorted(fs):
        p = os.path.join(dp, f)
        lines.append(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {os.path.relpath(p, OUT).replace(os.sep, '/')}")
open(f"{OUT}/SHA256SUMS.txt", "w", newline="\n").write("\n".join(sorted(lines, key=lambda x: x[66:])) + "\n")

zp = f"{WORK}/release/{NAME}.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for dp, _, fs in sorted(os.walk(OUT)):
        for f in sorted(fs):
            p = os.path.join(dp, f)
            z.write(p, os.path.join("fractalus-v14", os.path.relpath(p, OUT)).replace(os.sep, "/"))
print(zp, os.path.getsize(zp), "B; plików", len(lines) + 1, "; IPS", len(patch), "B; łatki:", " ".join(PATCHES))
