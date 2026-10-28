"""Build: ROM v10.1 (nosty3) + nasze łatki -> G:/tmp/claude/atari/fractalus/build/fx.rom/.car
Każda łatka: plik src/*.asm (MADS, opt h-, org = adres CPU) + bank + opcjonalne poprawki bajtów."""
import hashlib, subprocess, sys, os, json
from paths import WORK, NOSTY, MADS
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = f"{NOSTY}/optimized version/Rescue on Fractalus! - optimized 128KB.rom"
BASE_SHA = "afa04d6802a03333516936b4912f8f7abf23a1837362ac2b0ceaa83b6b6414da"
OUT = f"{WORK}/build"


def asm(name):
    os.makedirs(f"{OUT}/obj", exist_ok=True)
    out = f"{OUT}/obj/{name}.bin"
    r = subprocess.run([MADS, f"{ROOT}/src/{name}.asm", f"-o:{out}"], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)
    return open(out, "rb").read()


def org_of(name):
    for line in open(f"{ROOT}/src/{name}.asm"):
        t = line.split(";")[0].split()
        if len(t) == 2 and t[0] == "org":
            return int(t[1].lstrip("$"), 16)
    raise ValueError(name)


def put(rom, bank, cpu, data, expect=None):
    base = 0xA000 if bank == len(rom) // 8192 - 1 else 0x8000
    off = bank * 8192 + cpu - base
    assert 0 <= cpu - base and cpu - base + len(data) <= 8192, (bank, hex(cpu), len(data))
    if expect is not None:
        assert rom[off:off + len(expect)] == expect, (bank, hex(cpu), rom[off:off + len(expect)].hex())
    rom[off:off + len(data)] = data


def build(patches, name="fx"):
    rom = bytearray(open(BASE, "rb").read())
    assert hashlib.sha256(rom).hexdigest() == BASE_SHA
    for p in patches:
        p(rom)
    os.makedirs(OUT, exist_ok=True)
    open(f"{OUT}/{name}.rom", "wb").write(rom)
    car = b"CART" + (14).to_bytes(4, "big") + (sum(rom) & 0xFFFFFFFF).to_bytes(4, "big") + bytes(4) + rom
    open(f"{OUT}/{name}.car", "wb").write(car)
    return rom


# --- łatki ---
def wait_beam(rom):
    code = asm("wait_beam")
    put(rom, 2, org_of("wait_beam"), code, expect=b"\xff" * len(code))
    put(rom, 2, 0x9214, bytes([0x4C, 0xD5, 0x9F]), expect=bytes.fromhex("4ca084"))


PATCHES = {"wait_beam": wait_beam}

# Łatki z osobnych modułów (tools/patches_*.py, każdy eksportuje słownik PATCHES) - żeby równoległe prace
# nie edytowały tego pliku. Kolejność: najpierw ten plik, potem moduły alfabetycznie.
import glob, importlib.util
for _f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "patches_*.py"))):
    _spec = importlib.util.spec_from_file_location(os.path.basename(_f)[:-3], _f)
    _mod = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_mod)
    PATCHES.update(_mod.PATCHES)

if __name__ == "__main__":
    args = sys.argv[1:]
    name = "fx"
    if args and args[0].startswith("--name="):
        name = args.pop(0).split("=", 1)[1]
    names = args or list(PATCHES)
    rom = build([PATCHES[n] for n in names], name)
    print("zbudowano", f"{OUT}/{name}.car", "łatki:", names, "sha", hashlib.sha256(rom).hexdigest()[:16])
