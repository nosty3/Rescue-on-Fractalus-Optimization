"""Łatka s2-reorder (pomysł #8 Fable): praca, która nie dotyka buforów obrazu, przed czekaniem na promień.
Ładowane przez build.py. Źródła src/reorder_b2.asm (pętla czekania z rzutowaniem, opis układu w nagłówku),
src/reorder_b2w.asm, src/reorder_b3.asm.
Bank 2: $87D7-$885D (martwe ciało starego prologu) = `pre`, $9214 jmp pre (było jmp $9FD5), $9FD5-$9FEE (stary
wait_beam, teraz nieużywany) = lądowania wywołania tablic prologu ($9FD5 lda #3 / sta $D500, $9FE2 rts).
$87D3 (sec / jmp $984F) i $9854 (jmp $85D4) bez zmian.
Bank 3: $984C jmp tail3 (było jmp $9D7E), $9F83 jmp $9FDD (koniec części tablicowej prologu), $9F86 tail3 = stx $a7
+ ogon skalarny prologu bajt w bajt jak dotąd (teraz wykonywany po czekaniu), $9FDA jmp $9D80, $9FDD lda #2 / sta $D500."""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import asm, put, ROOT, MADS, OUT  # noqa: E402

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


# bajty bazy w miejscach łatki (build sprawdza, że baza jest ta, na którą łatka była robiona)
OLD_PROLOG_B2 = bytes.fromhex(  # $87D7-$885D (martwe od proj_loop)
    "188a990039990139990239990339e88a990439990539990639990739e8986908a8c0d490dc8a18692e85b3a014a96788993a"
    "2699ce26d0f7a021a96b88994e26996f2699902699b126d0f1a5288d0729a5298d082920e091a9808de7288de8288d12298d13298d14"
    "298d1529a4a7d0058dea288579a9008ded288dfb288dfc28a56a3003eefc28")
WAIT_BEAM_B2 = bytes.fromhex("0848a54af00fa542f00bad0bd4c94a90f5c97cb0f168284c2f98")  # $9FD5-$9FEE
TAIL_B3 = bytes.fromhex(  # $9F83-$9FBE: ogon skalarny prologu (przenoszony do tail3 bez zmian)
    "a5288d0729a5298d0829a9808de7288de8288d12298d13298d14298d1529a4a7d0058dea288579a9008ded288dfb288dfc28a56a3003"
    "eefc284c4f98")


def reorder(rom):
    code = asm("reorder_b2")
    lab = _labels("reorder_b2")
    assert lab["PRE"] == 0x87D7 and 0x87D7 + len(code) <= 0x885E
    put(rom, 2, 0x87D3, bytes.fromhex("384c4f98"), expect=bytes.fromhex("384c4f98"))  # kontrola: wejście $87D3
    put(rom, 2, 0x87D7, code, expect=OLD_PROLOG_B2[:len(code)])
    put(rom, 2, 0x9214, bytes([0x4C]) + lab["PRE"].to_bytes(2, "little"), expect=bytes.fromhex("4cd59f"))
    put(rom, 2, 0x9854, bytes.fromhex("4cd485"), expect=bytes.fromhex("4cd485"))  # kontrola: koniec ogona
    code = asm("reorder_b2w")
    assert len(code) == len(WAIT_BEAM_B2)
    put(rom, 2, 0x9FD5, code, expect=WAIT_BEAM_B2)
    code = asm("reorder_b3")
    lab3 = _labels("reorder_b3")
    n_tail = 0x9FBF - 0x9F83
    assert len(code) == 0x9FE2 - 0x9F83
    put(rom, 3, 0x9F83, code, expect=TAIL_B3 + b"\xff" * (len(code) - n_tail))
    assert code[3:3 + 2] == bytes.fromhex("86a7") and code[5:5 + n_tail] == TAIL_B3  # tail3 = stx $a7 + stary ogon
    put(rom, 3, 0x984C, bytes([0x4C]) + lab3["TAIL3"].to_bytes(2, "little"), expect=bytes.fromhex("4c7e9d"))
    put(rom, 3, 0x9D7E, bytes.fromhex("86a7a90e8d00d5"), expect=bytes.fromhex("86a7a90e8d00d5"))  # kontrola: hop14


PATCHES = {"reorder": reorder}
