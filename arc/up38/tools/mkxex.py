"""Buduje .xex Fractalusa dla Atari z pamięcią rozszerzoną (320K Rambo, 576K, 1088K): relokacja reloc.py +
decyzje xex/decisions.json, tryb intra w układzie kartridża, przejście do nowego układu pod $A155.

Segmenty pliku:
  1. $0500 wybór banku do ładowania + sprawdzenie pamięci (16 wartości PORTB = 16 różnych banków); INIT.
  2. Dla każdego banku rozszerzenia: [sel = PORTB] [INIT -> select: STA $D301] [$4000-$7FFF: 16 KB].
     Banki 0-6, 8-14: przeniesiony bank n ($4000) + przeniesiony bank 15 ($6000).
     Bank 7 (wolny w grze): oryginalne banki 3 i 4 dla trybu intra.
  3. PORTB = $FF (pamięć podstawowa), $8000-$9FFF oryginalny bank 4, $A000-$BFFF oryginalny bank 15 z łatkami
     trybu intra (STA $D500 -> JSR bankcopy, $A155 -> JMP transition).
  4. $0100 bankcopy + transition, $0180 start; RUN = start.
Użycie: mkxex.py [OUT.xex]"""
import sys, os, json, subprocess
from paths import WORK, MADS
from reloc import load_rom, instructions, extend, build, portb, USED

R = WORK
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else f"{R}/xex/fractalus-opus.xex"
PB = {n: portb(n) for n in range(16)}

LOW1 = f"""
        opt h-
        org $0100
; tryb intra: zamiast STA $D500 (A = 3 albo 4) kopiujemy oryginalny bank z banku rozszerzenia 7 pod $8000
bankcopy
        php
        sta sav_a
        stx sav_x
        sty sav_y
        ldx #$40
        cmp #3
        beq bc1
        ldx #$60
bc1     stx src+2
        lda #$80
        sta dst+2
        lda #${PB[7]:02x}
        sta $d301
        ldx #$20
        ldy #0
src     lda $4000,y
dst     sta $8000,y
        iny
        bne src
        inc src+2
        inc dst+2
        dex
        bne src
        lda #$ff
        sta $d301
        lda sav_a
        ldx sav_x
        ldy sav_y
        plp
        rts

; przejście z trybu intra do nowego układu: zamiast LDA #0 / STA $D500 pod $A155
transition
        ldx #$1f
        lda #0
tz      sta $0160,x
        dex
        bpl tz
        lda #${PB[0]:02x}
        sta $d301
        jmp $615a

sav_a   dta 0
sav_x   dta 0
sav_y   dta 0
        ert *>$0160
"""

LOW2 = """
        opt h-
        org $0180
; start: stan jak przy RUN kartridża (pamięć wyzerowana, obraz wyłączony), potem RUN gry $A122
start
        sei
        ldx #$ff
        txs
        lda #$ff
        sta $d301
        lda #0
        sta $022f
        sta $d400
        tay
        ldx #$04
        stx z+2
z       sta $0400,y
        iny
        bne z
        inc z+2
        ldx z+2
        cpx #$80
        bne z
        ldx #$7f
zz      sta $80,x
        dex
        bpl zz
        cli
        lda #$04
        ldx #$01
        ldy #$01
        jmp $a122
        ert *>$01c0
"""

MSG = "FRACTALUS UP38 NEEDS 320K RAMBO, 576K OR 1MB RAM"
CHECK = f"""
        opt h-
        org $0500
sel     dta $ff
select  lda sel
        sta $d301
        rts
; sprawdzenie: 16 wartości PORTB musi dać 16 różnych banków rozszerzenia
check
        ldx #15
c1      lda tab,x
        sta $d301
        txa
        sta $4000
        lda #$a5
        sta $4001
        dex
        bpl c1
        ldx #15
c2      lda tab,x
        sta $d301
        cpx $4000
        bne bad
        lda $4001
        cmp #$a5
        bne bad
        dex
        bpl c2
        lda #$ff
        sta $d301
        rts
bad     lda #$ff
        sta $d301
        ldy #{len(MSG) - 1}
b1      lda msg,y
        sta ($58),y
        dey
        bpl b1
        jmp *
tab     dta {",".join(f"${PB[n]:02x}" for n in range(16))}
msg     dta d'{MSG}'
        ert *>$0600
"""


def mads(text, name):
    """Asembluje tekst; zwraca (bajty, etykiety)."""
    src = f"{R}/xex/{name}.asm"; out = f"{R}/xex/{name}.bin"; lb = f"{R}/xex/{name}.lab"
    open(src, "w", encoding="cp1250").write(text)
    r = subprocess.run([MADS, src, f"-o:{out}", f"-t:{lb}"], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)
    labs = {}
    for line in open(lb):
        p = line.split()
        if len(p) == 3:
            try:
                labs[p[2].lower()] = int(p[1], 16)
            except ValueError:
                pass
    return open(out, "rb").read(), labs


def main():
    rom = load_rom(f"{R}/build/final.rom")
    ins = extend(rom, instructions(json.load(open(f"{R}/cov/all.json"))))
    dec = json.load(open(os.path.join(HERE, "..", "xex", "decisions.json")))
    ext, log = build(rom, ins, dec)
    low1, L1 = mads(LOW1, "xex_low1")
    low2, L2 = mads(LOW2, "xex_low2")
    chk, C = mads(CHECK, "xex_check")

    # oryginalne banki do trybu intra
    orig = {b: bytearray(rom[b * 8192:(b + 1) * 8192]) for b in (3, 4, 15)}
    orig[4][0x0887:0x088A] = bytes([0xBD, 0xE8, 0x90])        # DEC $90E8,X -> LDA (na kartridżu zapis ginie)
    for a in (0xA124, 0xA12F, 0xA137, 0xA14C):                # STA $D500 -> JSR bankcopy
        o = a - 0xA000
        assert orig[15][o:o + 3] == b"\x8d\x00\xd5", hex(a)
        orig[15][o:o + 3] = bytes([0x20, L1["bankcopy"] & 0xFF, L1["bankcopy"] >> 8])
    o = 0xA155 - 0xA000
    assert orig[15][o:o + 5] == bytes([0xA9, 0x00, 0x8D, 0x00, 0xD5])
    orig[15][o:o + 3] = bytes([0x4C, L1["transition"] & 0xFF, L1["transition"] >> 8])

    segs = []
    seg = lambda addr, data: segs.append((addr, bytes(data)))
    init = lambda addr: seg(0x02E2, bytes([addr & 0xFF, addr >> 8]))
    seg(0x0500, chk); init(C["check"])
    for n in USED + [7]:
        data = ext[n] if n != 7 else bytes(orig[3]) + bytes(orig[4])
        assert len(data) == 0x4000
        seg(C["sel"], bytes([PB[n]])); init(C["select"])
        seg(0x4000, data)
    seg(C["sel"], b"\xff"); init(C["select"])
    seg(0x8000, orig[4])
    seg(0xA000, orig[15])
    seg(0x0100, low1)
    seg(0x0180, low2)
    seg(0x02E0, bytes([L2["start"] & 0xFF, L2["start"] >> 8]))

    out = bytearray(b"\xff\xff")
    for addr, data in segs:
        end = addr + len(data) - 1
        out += bytes([addr & 0xFF, addr >> 8, end & 0xFF, end >> 8]) + data
    open(OUT, "wb").write(out)
    print(f"{OUT}: {len(out)} B, segmentów {len(segs)}; bankcopy ${L1['bankcopy']:04x} transition "
          f"${L1['transition']:04x} start ${L2['start']:04x}; zmian relokacji {len(log)}")


if __name__ == "__main__":
    main()
