"""Łatki VBI (fork VBI): ładowane przez build.py.
Zajęte: bank 14 $9801-$9Exx (vbi_sound_idle.asm), bank 2 $9885-$988E (vbi_sound_exit.asm),
stały bank: $B91C-$B923 (dźwięk) i $A852-$A859 (wskaźnik). Obie łatki wymagają wspólnych plików asm."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _common(rom):
    from build import asm, put, org_of
    if rom[14 * 8192 + 0x1801] != 0xFF:  # wspólny kod już wstawiony przez drugą łatkę
        return
    code = asm("vbi_sound_idle")
    put(rom, 14, org_of("vbi_sound_idle"), code, expect=b"\xff" * len(code))
    code = asm("vbi_sound_exit")
    put(rom, 2, org_of("vbi_sound_exit"), code, expect=b"\xff" * len(code))


def vbi_sound_idle(rom):
    from build import put
    _common(rom)
    # $B91C: lda #14 / sta $d500 / jmp $9801; reszta do $B92A nieosiągalna
    put(rom, 15, 0xB91C, bytes([0xA9, 0x0E, 0x8D, 0x00, 0xD5, 0x4C, 0x01, 0x98]),
        expect=bytes.fromhex("ad3106f00320e2b9"))


def vbi_gauge(rom):
    from build import put
    if rom[14 * 8192 + 0x1801] == 0xFF:
        _common(rom)
    # $A852: lda #14 / sta $d500 / jmp $98C2 (ścieżka przerysowania pierwszego wskaźnika);
    # pętla $A85F zostaje dla drugiego wskaźnika ($A8A5)
    put(rom, 15, 0xA852, bytes([0xA9, 0x0E, 0x8D, 0x00, 0xD5, 0x4C, 0xC2, 0x98]),
        expect=bytes.fromhex("8c2b0684bfa9ff85"))


PATCHES = {"vbi_sound_idle": vbi_sound_idle, "vbi_gauge": vbi_gauge}
