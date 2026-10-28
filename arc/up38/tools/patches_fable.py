"""Łatki Fable: potok rysowania w banku 2 (pętla krawędzi, clipping) + rzutowanie z dzieleniem w banku 3.
Ładowane przez build.py. Źródła generuje tools/gen_fable.py (wywoływany tu, bo adres powrotu z banku 3 zależy
od zawartości banku 2: pod ret+5 musi leżeć bajt $60).
Zajęte: bank 3 $963A-ret+4 oraz $9FFF (znacznik banku dla osłony VBI $BFEA), bank 2 $85D4-$87D2 (nowa pętla,
clipping, kopie), $885E-$8860 (jmp), $984C-$9853 (stuby)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import asm, put, ROOT  # noqa: E402
import gen_fable  # noqa: E402

SRC = f"{ROOT}/src"


def _label(name, label, strict=True):
    """Adres etykiety z tablicy etykiet MADS (-t) dla src/NAME.asm. strict=False: przebieg pomiarowy (błędy zasięgu
    gałęzi przed ustawieniem org bloków rzadkich nie przerywają; tablica etykiet i tak powstaje)."""
    import subprocess
    from build import MADS, OUT
    lab = f"{OUT}/obj/{name}.lab"
    if os.path.exists(lab):
        os.remove(lab)
    r = subprocess.run([MADS, f"{SRC}/{name}.asm", f"-o:{OUT}/obj/{name}.bin", f"-t:{lab}"],
                       capture_output=True, text=True)
    if r.returncode and strict:
        sys.exit(r.stdout + r.stderr)
    for line in open(lab, encoding="latin-1"):
        t = line.split()
        if len(t) >= 3 and t[-1].upper() == label.upper():
            return int(t[-2], 16)
    raise KeyError(label)


def proj_loop(rom):
    """Rzutowanie (bank 3) + nowa pętla krawędzi i szybki clipping (bank 2). Jedna łatka, bo pętla woła stub $984F."""
    # rzutowanie: najpierw adres `ret` bez wyrównania, potem wyrównanie tak, by w banku 2 pod ret+5 był rts ($60)
    # (bloki rzadkie 1. współrzędnej muszą kończyć się na $9847, więc ich org = $9847 - długość)
    open(f"{SRC}/fable_proj3.asm", "w", encoding="utf-8").write(gen_fable.gen_proj3())
    ret0 = _label("fable_proj3", "RET", strict=False)
    rare_org = 0x9847 - (_label("fable_proj3", "RAREEND", strict=False) - 0x963A)
    b2 = rom[2 * 8192:3 * 8192]
    for pad in range(0, 0x9FD0 - ret0 - 5):
        if b2[ret0 + pad + 5 - 0x8000] == 0x60:
            break
    else:
        raise RuntimeError("brak bajtu $60 w banku 2 na lądowanie powrotu z banku 3")
    open(f"{SRC}/fable_proj3.asm", "w", encoding="utf-8").write(gen_fable.gen_proj3(pad=pad, rare_org=rare_org))
    code = asm("fable_proj3")
    ret = _label("fable_proj3", "RET")
    assert ret == ret0 + pad and b2[ret + 5 - 0x8000] == 0x60, (hex(ret), pad)
    assert _label("fable_proj3", "RAREEND") == 0x9847
    assert ret + 5 <= 0x9FD0  # poniżej wait_beam2 ($9FD5) i stubów
    assert rom[3 * 8192 + 0x1FFF] == 0xFF
    put(rom, 3, rare_org, code, expect=b"\xff" * len(code))
    rom[3 * 8192 + 0x1FFF] = 3  # znacznik banku: osłona VBI ($BFDA/$BFEA) odtwarza bank 3 po przerwaniu
    # stuby w banku 2
    open(f"{SRC}/fable_stub2.asm", "w", encoding="utf-8").write(gen_fable.gen_stub2())
    code = asm("fable_stub2")
    put(rom, 2, 0x984C, code, expect=b"\xff" * len(code))
    # nowa pętla krawędzi + clipping w miejscu starego rzutowania; stare wejście pętli -> jmp
    open(f"{SRC}/fable_loop2.asm", "w", encoding="utf-8").write(gen_fable.gen_loop2())
    code = asm("fable_loop2")
    put(rom, 2, 0x85D4, code, expect=bytes.fromhex("bdb4240910"))
    put(rom, 2, 0x885E, bytes([0x4C, 0xD4, 0x85]), expect=bytes.fromhex("a000b9099b"))
    # prolog $87D3: sec / jmp $984F -> bank 3 pdisp -> prolog3 (bank 3) + bank 14 (tabele); koniec -> $9854 jmp $85D4
    put(rom, 2, 0x87D3, bytes([0x38, 0x4C, 0x4F, 0x98]), expect=bytes.fromhex("86a7a02018"))
    open(f"{SRC}/fable_pro14.asm", "w", encoding="utf-8").write(gen_fable.gen_pro14())
    code = asm("fable_pro14")
    assert rom[14 * 8192 + 0x1FFF] == 14
    put(rom, 14, 0x9950, code, expect=b"\xff" * len(code))
    # pętla epilogu $89A1 rozwinięta 4x w martwym kodzie starej pętli ($8860)
    open(f"{SRC}/fable_epi2.asm", "w", encoding="utf-8").write(gen_fable.gen_epi2())
    code = asm("fable_epi2")
    put(rom, 2, 0x8861, code, expect=bytes.fromhex("099bc8aa8e"))
    put(rom, 2, 0x89A1, bytes([0x4C, 0x61, 0x88]), expect=bytes.fromhex("a01f38ad1e27"))


PATCHES = {"proj_loop": proj_loop}
