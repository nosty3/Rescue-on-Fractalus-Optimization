"""Łatki sceny (agent s2-scene): siatka terenu `jsr $8309` (banki 10-13, tools/gen_scene.py).
Ładowane przez build.py. Źródła src/scene_b10..b13.asm generuje tools/gen_scene.py (wywoływany tu)."""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import asm, ROOT, MADS, OUT  # noqa: E402
import gen_scene  # noqa: E402

SRC = f"{ROOT}/src"


def _labels(name):
    lab = f"{OUT}/obj/{name}.lab"
    if os.path.exists(lab):
        os.remove(lab)
    r = subprocess.run([MADS, f"{SRC}/{name}.asm", f"-o:{OUT}/obj/{name}.bin", f"-t:{lab}"],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)
    out = {}
    for line in open(lab, encoding="latin-1"):
        t = line.split()
        if len(t) >= 3:
            try:
                out[t[-1].upper()] = int(t[-2], 16)
            except ValueError:
                pass
    return out


def scene_grid(rom):
    """45 punktów spirali terenu w bankach 10-13 przepisane (gen_scene.py); wynik w RAM-ie i rejestry na wyjściu
    identyczne. Zajmuje całe banki 10-13 (tablice $9D00-$9EFF i znacznik $9FFF zachowane)."""
    for b in (10, 11, 12, 13):
        orig = bytes(rom[b * 8192:(b + 1) * 8192])
        name = f"scene_b{b}"
        src, n = gen_scene.gen_source(b, orig)
        open(f"{SRC}/{name}.asm", "w", encoding="utf-8").write(src)
        lab = _labels(name)
        ends = [lab[f"PK{i}"] for i in range(n)] + [lab["CODE_END"]]
        sizes = [ends[i + 1] - ends[i] for i in range(n)]
        src, _ = gen_scene.gen_source(b, orig, sizes)
        open(f"{SRC}/{name}.asm", "w", encoding="utf-8").write(src)
        code = asm(name)
        assert len(code) == 8192, (name, len(code))
        assert code[0x1893:0x1896] == bytes([0x4C]) + _labels(name)["ENTRY"].to_bytes(2, "little")
        assert code[0x18E0:0x18E7] == orig[0x18E0:0x18E7] and code[0x1D00:0x1F00] == orig[0x1D00:0x1F00]
        assert code[0x1FFF] == b == orig[0x1FFF]
        rom[b * 8192:(b + 1) * 8192] = code


def scene_pre(rom):
    """Prelude of jsr $8309 (bank 2 $9148 + sin/cos $8055 + 4 products $8558) in bank 4 $9141-$9FFF (free run
    after the intro code) with tables (tools/gen_scene7.py). Bank 2 $8309: jmp $9148 (was jsr $9148 / jsr $8558);
    bank 2 $9148: lda #4 / sta $d500 -> bank 4 $914D jmp prelude; exit lda #2 / jmp $914A -> bank 2 $914D jmp $830F.
    The old bank-2 code $8055-$821B, $8558-$85D3, $9148-$91DF is no longer executed. Bank 4 $9FFF = 4 (was $FF):
    the VBI guard must restore bank 4 when it interrupts the prelude (checked: the guard never runs with bank 4
    selected in the original from boot through flight, so the intro is unaffected)."""
    import gen_scene7
    src = gen_scene7.gen_source(bytes(rom))
    open(f"{SRC}/scene_b4.asm", "w", encoding="utf-8").write(src)
    code = asm("scene_b4")
    assert len(code) == 0x2000 - 0x1141 and code[-1] == 4
    assert set(rom[4 * 8192 + 0x1141:5 * 8192]) == {0xFF}
    rom[4 * 8192 + 0x1141:5 * 8192] = code
    off = 2 * 8192 + 0x0309
    assert rom[off:off + 6] == bytes.fromhex("204891205885")
    rom[off:off + 3] = bytes.fromhex("4c4891")
    off = 2 * 8192 + 0x1148
    assert rom[off:off + 8] == bytes.fromhex("ad87288587ad8828")
    rom[off:off + 8] = bytes.fromhex("a9048d00d54c0f83")
    # post-pass $84FD unrolled at $8055 (old sin/cos, dead now); the exit of banks 10-13 jumps there
    open(f"{SRC}/scene_post2.asm", "w", encoding="utf-8").write(gen_scene7.gen_post(bytes(rom)))
    code = asm("scene_post2")
    rom[2 * 8192 + 0x55:2 * 8192 + 0x55 + len(code)] = code
    off = 2 * 8192 + 0x18E7
    assert rom[off:off + 5] == bytes.fromhex("68284cfd84")
    rom[off + 3:off + 5] = (0x8055).to_bytes(2, "little")


PATCHES = {"scene_grid": scene_grid, "scene_pre": scene_pre}
