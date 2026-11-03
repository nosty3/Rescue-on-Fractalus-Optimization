"""Łatki VBI, runda 2 (Fable, s2-vbi): ładowane przez build.py. Na bazie v11 (łatki rundy 1 już w środku).
Zajęte: bank 7 cały (tablice mnożenia, znacznik $9FFF = 7), bank 1 (kod rezydentny) $7F4B-$7F78 + operandy
$7C9C, $7CBD, $7565, $7EEB-$7EF8, $7F20-$7F45; bank 14 $90C2-$9484 (dźwięk) i $9490-$973D (interpolacja + 2 tablice);
stały bank $B922-$B923 (operand jmp) i $B9B0-$B9B7. Bez RAM-u roboczego (stan tylko w rejestrach i na stosie).
Weryfikacja: tools/vbieq.py (RAM, zapisy do sprzętu, SP, bank; --poison), G:/tmp/claude/atari/fractalus/s2vbi/
(mul_exhaustive.py = wszystkie 65536 pary mnożenia, cap_vbi2.py = nagrania stanów, vbitime2.py = pomiar natywny).
  vbi2_mul    mnożenie logiki lotu $7CD6 przez tablice (src/vbi2_mul.asm, tools/gen_vbi2_mul.py)
  vbi2_sound  dźwięk: test kanałów parami, kolejka zdarzeń bez powtarzania minimum, szybsze min/max
              (src/vbi2_snd14.asm)
  vbi2_interp interpolacja terenu $9000 (bank 14) wprost, bez $90A5 i pośrednich zapisów; lerp z v1 w X
              (src/vbi2_interp14.asm, src/vbi2_lerp.asm $7F20, src/vbi2_wrap.asm $7EEB)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _base_bytes(bank, cpu, n):
    """Bajty ROM-u bazowego (sprawdzian, że nikt inny nie pisał w to miejsce przed nami)."""
    import build
    rom = open(build.BASE, "rb").read()
    base = 0xA000 if bank == 15 else (0x4000 + bank * 0x2000 if bank < 2 else 0x8000)
    off = bank * 8192 + cpu - base
    return rom[off:off + n]


def _put_res(rom, cpu, data, expect):
    """Kod rezydentny: bank 0 = $4000-$5FFF, bank 1 = $6000-$7FFF (kopiowane do RAM przy starcie)."""
    assert 0x4000 <= cpu and cpu + len(data) <= 0x8000, hex(cpu)
    off = cpu - 0x4000
    assert rom[off:off + len(expect)] == expect, (hex(cpu), rom[off:off + len(expect)].hex())
    rom[off:off + len(data)] = data


def vbi2_mul(rom):
    from build import asm, put, org_of
    from gen_vbi2_mul import bank7
    t = bank7()
    assert len(rom[7 * 8192:8 * 8192]) == 8192 and rom[7 * 8192:8 * 8192] == _base_bytes(7, 0x8000, 8192)
    rom[7 * 8192:8 * 8192] = t
    code = asm("vbi2_mul")
    _put_res(rom, org_of("vbi2_mul"), code, expect=b"\xea" * len(code))
    for site in (0x7C9B, 0x7CBC, 0x7564):   # jsr $7cd6 -> jsr $7f4b
        _put_res(rom, site, bytes([0x20, 0x4B, 0x7F]), expect=bytes([0x20, 0xD6, 0x7C]))


def vbi2_sound(rom):
    from build import asm, put, org_of
    code = asm("vbi2_snd14")
    put(rom, 14, org_of("vbi2_snd14"), code, expect=b"\xff" * len(code))
    scan = org_of("vbi2_snd14")
    # $B91C: lda #14 / sta $d500 / jmp $9801 (runda 1) -> jmp snd_scan
    put(rom, 15, 0xB922, bytes([scan & 0xFF, scan >> 8]), expect=bytes([0x01, 0x98]))
    # snd_queue = pierwsza etykieta za stubami: adres z pliku listingu MADS? prościej: szukamy sekwencji
    # `lda #$1f / cmp $73 / bcs` w kodzie (jedyna taka w pliku)
    sig = bytes([0xA9, 0x1F, 0xC5, 0x73, 0xB0])
    i = code.find(sig)
    assert i >= 0 and code.find(sig, i + 1) < 0
    q = scan + i
    # $B9B0: lda #14 / sta $d500 / jmp snd_queue (oryginał: lda #$1f / cmp $73 / bcs / sta $73)
    put(rom, 15, 0xB9B0, bytes([0xA9, 0x0E, 0x8D, 0x00, 0xD5, 0x4C, q & 0xFF, q >> 8]),
        expect=bytes.fromhex("a91fc573b0028573"))


def vbi2_interp(rom):
    from build import asm, put, org_of
    code = asm("vbi2_interp14")
    put(rom, 14, org_of("vbi2_interp14"), code, expect=bytes([0xFF]) * len(code))
    for name in ("vbi2_lerp", "vbi2_wrap"):
        code = asm(name)
        cpu = org_of(name)
        _put_res(rom, cpu, code, expect=_base_bytes(1, cpu, len(code)))


PATCHES = {"vbi2_mul": vbi2_mul, "vbi2_sound": vbi2_sound, "vbi2_interp": vbi2_interp}
