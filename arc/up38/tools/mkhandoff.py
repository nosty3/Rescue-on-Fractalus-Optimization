"""Składa paczkę dla nosty3 (i jego agenta): handoff/*.md, źródła, narzędzia, pliki gry, łatka IPS z v10.1,
wyniki pomiarów, raport, stan startowy katalogu roboczego. Wynik: <WORK>/handoff/fractalus-up38/ i .zip obok.
Użycie: mkhandoff.py [NAZWA_KATALOGU_ROBOCZEGO]   (w zipie folder i tak nazywa się fractalus-up38)"""
import os, shutil, json, subprocess, sys, hashlib, zipfile
from paths import WORK, NOSTY

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{WORK}/handoff/" + (sys.argv[1] if len(sys.argv) > 1 else "fractalus-up38")   # katalog roboczy paczki
if os.path.exists(OUT):
    sys.exit(f"{OUT} już istnieje: usuń go najpierw (u nas: safe_delete.py -r)")
os.makedirs(OUT)


def cp(src, dst):
    d = os.path.join(OUT, dst)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.copy2(src, d)


def ips(old, new):
    """Łatka IPS (rekordy ciągłych zmian, max 65535 B)."""
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


for f in ("README.md", "README_PL.md", "AGENT.md"):
    cp(f"{ROOT}/handoff/{f}", f)
cp(f"{ROOT}/STATUS.md", "docs/worklog_pl.md")
for f in sorted(os.listdir(f"{ROOT}/src")):
    if f.endswith(".asm"):
        cp(f"{ROOT}/src/{f}", f"src/{f}")
for f in sorted(os.listdir(f"{ROOT}/tools")):
    if f.endswith(".py"):
        cp(f"{ROOT}/tools/{f}", f"tools/{f}")
cp(f"{ROOT}/xex/decisions.json", "xex/decisions.json")

# pliki gry
rom = open(f"{WORK}/build/final.rom", "rb").read()
car = open(f"{WORK}/build/final.car", "rb").read()
assert hashlib.sha256(car).hexdigest().startswith("ddb7466a")
base = open(f"{NOSTY}/optimized version/Rescue on Fractalus! - optimized 128KB.rom", "rb").read()
patch = ips(base, rom)
assert apply_ips(base, patch) == rom
for name, data in (("bin/fractalus_up38.rom", rom), ("bin/fractalus_up38.car", car),
                   ("bin/up38_from_v10.1.ips", patch)):
    os.makedirs(os.path.dirname(f"{OUT}/{name}"), exist_ok=True)
    open(f"{OUT}/{name}", "wb").write(data)
cp(f"{WORK}/release/fractalus_up38_320k-1mb.xex", "bin/fractalus_up38_320k-1mb.xex")

# stan startowy katalogu roboczego (mapa instrukcji, stany maszyny dla xexrun)
cp(f"{WORK}/cov/all.json", "work/cov/all.json")
for f in ("run.img", "run.json", "post.img", "post.json"):
    cp(f"{WORK}/xex/{f}", f"work/xex/{f}")

# wyniki
cp(f"{WORK}/full155.jsonl", "results/full155.jsonl")
cp(f"{WORK}/ladder155.jsonl", "results/ladder155.jsonl")
cp(f"{WORK}/xex/bench155.jsonl", "results/xex_bench155_pal_1088k.jsonl")
rep = subprocess.run([sys.executable, f"{ROOT}/tools/fullreport.py", f"{WORK}/full155.jsonl"],
                     capture_output=True, text=True, encoding="utf-8", check=True,
                     env=dict(os.environ, PYTHONIOENCODING="utf-8")).stdout
open(f"{OUT}/results/fullreport.txt", "w", encoding="utf-8").write(rep)
cp(f"{WORK}/page/fractalus-opus.html", "report/index.html")
cp(f"{WORK}/page/data.js", "report/data.js")

# sumy kontrolne
lines = []
for dp, _, fs in os.walk(OUT):
    for f in sorted(fs):
        p = os.path.join(dp, f)
        lines.append(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {os.path.relpath(p, OUT).replace(os.sep, '/')}")
open(f"{OUT}/SHA256SUMS.txt", "w", newline="\n").write("\n".join(sorted(lines, key=lambda x: x[66:])) + "\n")

zp = f"{WORK}/handoff/fractalus-up38.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, _, fs in os.walk(OUT):
        for f in fs:
            p = os.path.join(dp, f)
            z.write(p, os.path.join("fractalus-up38", os.path.relpath(p, OUT)))
print(zp, os.path.getsize(zp), "B; plików", len(lines) + 1, "; IPS", len(patch), "B")
