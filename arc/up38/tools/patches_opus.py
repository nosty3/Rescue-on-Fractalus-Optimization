"""Łatki Opus dla pętli głównej (rasteryzacja, kasowanie, fill, niebo). Ładowane przez build.py."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import asm, put  # noqa: E402


def raster_cull(rom):
    """Bank 5: rasteryzacja v10 + rekurencyjne odrzucanie zasłoniętych poddrzew (src/raster5c.asm, gen_raster.py --nolazy)."""
    code = asm("raster5c")
    assert len(code) == 8192 and code[-1] == 5
    rom[5 * 8192:6 * 8192] = code


def clear_beam(rom):
    """Kasowanie wierszami od góry z wyścigiem z promieniem (banki 6/8, gen_clear.py) + pełne czekanie dopiero
    przed rysowaniem gór. Zastępuje wait_beam: $9214 -> $982F bez czekania; nietypowe X przez wait_beam2."""
    for bank in (6, 8):
        code = asm(f"clear_b{bank}")
        assert len(code) == 8192 and code[-1] == bank
        rom[bank * 8192:(bank + 1) * 8192] = code
    code = asm("wait_beam2")
    put(rom, 2, 0x9FD5, code, expect=b"\xff" * len(code))
    put(rom, 2, 0x9214, bytes([0x4C, 0x2F, 0x98]), expect=bytes.fromhex("4ca084"))
    # wrapper nosty3 ($982F): ścieżka nietypowego X kończy się jmp $921A -> przez czekanie wait_beam2
    put(rom, 2, 0x983F, bytes([0x4C, 0xD5, 0x9F]), expect=bytes.fromhex("4c1a92"))


def sky(rom):
    """Niebo bez kasowania (gen_sky.py + gen_raster.py): bank 5 rasteryzacja z odrzucaniem i leniwym zerowaniem,
    banki 6/8 kasowanie od granicy nieba (+ piksel obiektów w banku 8), bank 9 fill od granicy.
    Wymaga wait_beam (czekanie przed kasowaniem). Bank 2 $8B80: przełączenie na bank 8 + powroty."""
    code = asm("raster5")
    assert len(code) == 8192 and code[-1] == 5
    rom[5 * 8192:6 * 8192] = code
    for bank in (6, 8, 9):
        code = asm(f"sky_b{bank}")
        assert len(code) == 8192 and code[-1] == bank, bank
        rom[bank * 8192:(bank + 1) * 8192] = code
    orig = bytes.fromhex("98dd0e269027f025c097b0218ce228b9ca288580b9fa288581bc0039bd003885b54a05b5255811809180ace22860")
    put(rom, 2, 0x8B80, b"", expect=orig)
    put(rom, 2, 0x8B80, bytes.fromhex("a9088d00d5"))                       # wejście 1: lda #8 / sta $d500
    put(rom, 2, 0x8B88, bytes.fromhex("8d6601a9088d00d5"))                 # wejście 2: sta $0166 / lda #8 / sta $d500
    # $8B90: powrót bez piksela z wejścia 1 - te same porównania co oryginał (A = Y, flagi jak przy wyjściu)
    put(rom, 2, 0x8B90, bytes.fromhex("98dd0e269004f002c09760"))
    # $8B9B: powrót bez piksela z wejścia 2 - A z wejścia, flagi z cpy #$97 jak w oryginale
    put(rom, 2, 0x8B9B, bytes.fromhex("ad6601c09760"))
    # $8BA1: powrót z pikselem - A = zapisany bajt, flagi N/Z z ldy $28E2 jak w oryginale
    put(rom, 2, 0x8BA1, bytes.fromhex("ad6501ace22860"))


PATCHES = {"raster_cull": raster_cull, "clear_beam": clear_beam, "sky": sky}
