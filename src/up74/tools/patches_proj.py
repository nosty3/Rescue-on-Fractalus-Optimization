"""Łatki s2-proj (runda 2 rzutowania i pętli krawędzi, na wierzchu proj_loop Fable zawartego w bazie v11).
Ładowane przez build.py. Generator: tools/gen_proj.py (pisze src/proj3.asm i stuby).
Kolejność w buildzie: `proj2` PO `reorder` (reorder sprawdza bajty $87D3 i $984C, które tu się zmieniają).
Zajęte: bank 3 $97F1-$9F82 (rzutowanie Fable + jego wypełnienie occ; wyspy $9847-$9853 i $9D7E-$9D84 zachowane),
bank 3 $9FC4-$9FD6 i $9FE8-$9FFE, bank 14 $973E-$97FF, $9D88-$9DFF, $9F00-$9FCD + $9D78 (wypełnienie occ), bank 2
$9FE3-$9FE7, $87D3 (jmp $9FE3); loop2: bank 2 $85D4-$87D2, $8224-$82F? (stare dzielenie).
UWAGA: bank 3 $963A-$97F0 (FF) jest czytany przed lotem - nie ruszać (zmiana zmienia RAM na wejściu do lotu)."""
import os, sys, hashlib, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import asm, put, ROOT, MADS, OUT  # noqa: E402
import gen_proj  # noqa: E402

SRC = f"{ROOT}/src"
# bank 3 $963A-$9D7D w masterze (v11 + reorder): stare rzutowanie Fable; sprawdzane skrótem
B3_SHA = "01d5c8418b2bd15e563e5b8553078b3a0242a44b8c7be160795d87689d666bce"
FILL3_SHA = "b6bb7e22fb4601a404101e68cb8cb8f301438b407fc4f514eb810349230985c8"  # bank 3 $9D85-$9F82 (Fable fill_seq)


def _labels(name, strict=True):
    lab = f"{OUT}/obj/{name}.lab"
    if os.path.exists(lab):
        os.remove(lab)
    r = subprocess.run([MADS, f"{SRC}/{name}.asm", f"-o:{OUT}/obj/{name}.bin", f"-t:{lab}"],
                       capture_output=True, text=True)
    if r.returncode:
        if strict:
            sys.exit(r.stdout + r.stderr)
        return None
    out = {}
    for line in open(lab, encoding="latin-1"):
        t = line.split()
        if len(t) >= 3:
            try:
                out[t[-1].upper()] = int(t[-2], 16)
            except ValueError:
                pass
    return out


def proj2(rom):
    b2 = rom[2 * 8192:3 * 8192]
    b3 = bytes(rom[3 * 8192:4 * 8192])
    region = b3[0x963A - 0x8000:0x9D7E - 0x8000]
    h = hashlib.sha256(region).hexdigest()
    assert h == B3_SHA, ("bank 3 $963A-$9D7D inny niż w masterze", h)
    # wyrównanie powrotu: bajt $60 w banku 2 pod ret+5
    ok = None
    for pad in range(0, 64):
        open(f"{SRC}/proj3.asm", "w", encoding="utf-8").write(gen_proj.gen_proj3(pad=pad))
        lab = _labels("proj3", strict=False)
        if lab is None:
            continue
        ret = lab["RET"]
        if b2[ret + 5 - 0x8000] == 0x60:
            ok = (pad, ret)
            break
    assert ok, "brak wyrównania powrotu"
    code = asm("proj3")
    assert len(code) == 0x9F83 - 0x97F1
    assert code[0x9847 - 0x97F1:0x9854 - 0x97F1] == region[0x9847 - 0x963A:0x9854 - 0x963A]
    assert code[0x9D7E - 0x97F1:0x9D85 - 0x97F1] == b3[0x9D7E - 0x8000:0x9D85 - 0x8000]
    fill = b3[0x9D85 - 0x8000:0x9F83 - 0x8000]
    assert hashlib.sha256(fill).hexdigest() == FILL3_SHA, "bank 3 $9D85-$9F82 (wypełnienie occ) inne niż w masterze"
    put(rom, 3, 0x97F1, code)
    assert rom[3 * 8192 + 0x163A:3 * 8192 + 0x17F1] == b"\xff" * (0x97F1 - 0x963A)  # czytane przed lotem: bez zmian
    assert rom[3 * 8192 + 0x1FFF] == 3
    # wypełnienie occ w banku 14 (wolne FF), koniec prologu banku 14 ($9D78 jmp HOP) -> pierwszy kawałek
    for k, (org, src) in enumerate(gen_proj.gen_fill14()):
        open(f"{SRC}/proj_fill14_{k}.asm", "w", encoding="utf-8").write(src)
        c = asm(f"proj_fill14_{k}")
        put(rom, 14, org, c, expect=b"\xff" * len(c))
    put(rom, 14, 0x9D78, bytes([0x4C]) + gen_proj.FILL_CHUNKS[0][0].to_bytes(2, "little"),
        expect=bytes.fromhex("4c809d"))
    assert rom[14 * 8192 + 0x1FFF] == 14
    # prolog: $87D3 jmp $9FE3 (bank 2: lda #3 / sta $D500) -> bank 3 $9FE8 jmp tail3
    open(f"{SRC}/proj_pst2.asm", "w", encoding="utf-8").write(gen_proj.gen_prolog_stub2())
    put(rom, 2, 0x9FE3, asm("proj_pst2"), expect=b"\xff" * 5)
    lab = _labels("proj3")
    open(f"{SRC}/proj_pst3.asm", "w", encoding="utf-8").write(gen_proj.gen_prolog_stub3(lab["ADJUST"]))
    code = asm("proj_pst3")
    put(rom, 3, 0x9FE8, code, expect=b"\xff" * len(code))
    open(f"{SRC}/proj_ovf1.asm", "w", encoding="utf-8").write(gen_proj.gen_ovf1(lab["C2RELOAD"]))
    code = asm("proj_ovf1")
    put(rom, 3, gen_proj.OVF1, code, expect=b"\xff" * len(code))
    put(rom, 2, 0x87D3, bytes.fromhex("4ce39f"), expect=bytes.fromhex("384c4f"))
    print(f"proj2: pad {ok[0]}, ret ${ok[1]:04x}")


B2_SHA = "54ab0cc5564a47cd4b1d1a4a05a6f452db4dd199e093bbf23b122351af16eb78"  # bank 2 $85D4-$87D2 w masterze


def loop2(rom):
    """Pętla krawędzi bank 2 $85D4-$87D2 (gen_proj.gen_loop2). Wymaga proj2 (rzutowanie bez testu C na wejściu)."""
    assert rom[2 * 8192 + 0x7D3:2 * 8192 + 0x7D6] == bytes.fromhex("4ce39f"), "najpierw proj2"
    region = bytes(rom[2 * 8192 + 0x5D4:2 * 8192 + 0x7D3])
    assert hashlib.sha256(region).hexdigest() == B2_SHA, "bank 2 $85D4-$87D2 inny niż w masterze"
    t = rom[2 * 8192 + 0x1B09:2 * 8192 + 0x1B09 + 144]
    pairs = [(t[2 * k], t[2 * k + 1]) for k in range(72)]
    open(f"{SRC}/proj_loop2.asm", "w", encoding="utf-8").write(gen_proj.gen_loop2(pairs))
    code = asm("proj_loop2")
    assert len(code) == 0x87D3 - 0x85D4
    put(rom, 2, 0x85D4, code)
    # tablice par w martwym starym dzieleniu $8224-$8303
    old = bytes(rom[2 * 8192 + 0x224:2 * 8192 + 0x304])
    assert hashlib.sha256(old).hexdigest() == DIV_SHA, "bank 2 $8224-$8303 inny niż w masterze"
    open(f"{SRC}/proj_ptab2.asm", "w", encoding="utf-8").write(gen_proj.gen_pairtabs(pairs))
    code = asm("proj_ptab2")
    put(rom, 2, gen_proj.TABS, code)
    lab = _labels("proj_loop2")
    open(f"{SRC}/proj_fnb2.asm", "w", encoding="utf-8").write(gen_proj.gen_fnb(lab["FDONE"]))
    code = asm("proj_fnb2")
    assert gen_proj.FNB == gen_proj.TABS + 144
    put(rom, 2, gen_proj.FNB, code)


DIV_SHA = "3abffa363f6a98c75c1544cebb38cca500b5230cfdcd76d4cafe7181cde8e9c9"  # bank 2 $8224-$8303 (stare dzielenie)


PATCHES = {"proj2": proj2, "loop2": loop2}
