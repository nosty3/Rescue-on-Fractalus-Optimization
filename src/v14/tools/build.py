"""Build: ROM bazowy + nasze łatki -> G:/tmp/claude/atari/fractalus/build/NAZWA.rom/.car
Baza: --base=v11 (domyślnie od sesji 2: v11 nosty3 = up38 + poprawki Astry) albo --base=v10.1 (łatki sesji 1).
Pliki baz w WORK/base/ (v10.1 wyciągnięty z historii gita nosty3, commit fd98b24).
Każda łatka: plik src/*.asm (MADS, opt h-, org = adres CPU) + bank + opcjonalne poprawki bajtów.
Na bazie v11 banki 5/6/8/9 mają źródła w src/v11/*.asm (od nosty3): łatka `v11src` asembluje je od nowa."""
import hashlib, subprocess, sys, os, json
from paths import WORK, NOSTY, MADS
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASES = {"v10.1": (f"{WORK}/base/v10.1.rom", "afa04d6802a03333516936b4912f8f7abf23a1837362ac2b0ceaa83b6b6414da"),
         "v11": (f"{WORK}/base/v11.rom", "ec01982121b70baca35f04568617965c3164e716e0a5eb3c6ebcbb123566a868")}
BASE, BASE_SHA = BASES["v11"]
OUT = f"{WORK}/build"


def asm(name):
    os.makedirs(f"{OUT}/obj/v11", exist_ok=True)
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


def v11src(rom):
    """Banki 5/6/8/9 z src/v11/*.asm (całe banki 8 KB). Bez zmian w źródłach = ROM bez zmian."""
    for bank, name in ((5, "raster5"), (6, "sky_b6"), (8, "sky_b8"), (9, "sky_b9")):
        code = asm(f"v11/{name}")
        assert len(code) == 8192, (name, len(code))
        rom[bank * 8192:(bank + 1) * 8192] = code


PATCHES = {"wait_beam": wait_beam, "v11src": v11src}

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
    while args and args[0].startswith("--"):
        k, v = args.pop(0)[2:].split("=", 1)
        if k == "name":
            name = v
        elif k == "base":
            BASE, BASE_SHA = BASES[v]
        else:
            sys.exit(f"nieznana opcja --{k}")
    names = args
    if not names:
        sys.exit("podaj łatki (na bazie v11 np. `v11src`, na bazie v10.1 zestaw final z STATUS.md)")
    rom = build([PATCHES[n] for n in names], name)
    print("zbudowano", f"{OUT}/{name}.car", "łatki:", names, "sha", hashlib.sha256(rom).hexdigest()[:16])
