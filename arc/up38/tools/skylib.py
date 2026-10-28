"""Wspólne fragmenty kodu nieba (gen_sky.py, gen_raster.py)."""


def lazy(name):
    """Leniwe zerowanie: A = h (<= 151), Y = kolumna bajtów, X zachowany, $80/$81 nietknięte.
    Stare niebo w wierszach rr..D-1 (rr = max(151-h, 1), D = 152 - HD) -> 0, łańcuchem zapisów od wiersza D-1
    w górę ekranu, z wyjściem co 4 wiersze (wiersz k podzielny przez 4, gdy k <= rr): nadmiarowo wyzerowane
    wiersze k..rr-1 to też stare niebo, więc nowa granica D := k zostaje spójna. HD := 152 - k."""
    L = [f"{name}", " stx $0160",
         " eor #$ff", " clc", " adc #152", f" bne {name}a", " lda #1",          # rr = 151 - h, min. 1
         f"{name}a", " sta $0161",
         " lda #152", " sec", " sbc $0100,y", " tax",                           # X = D
         " cpx $0161", f" beq {name}e", f" bcc {name}e",
         f" lda {name}lo-2,x", " sta $0170", f" lda {name}hi-2,x", " sta $0171",  # wejście: wiersz D-1
         " ldx $0161", " lda #0", " jmp ($0170)",
         f"{name}e", " ldx $0160", " rts"]
    for k in range(43, 0, -1):
        L += [f"{name}r{k}", f" sta ${0x1010 + 96 * k:04x},y"]
        if k % 4 == 0:
            L += [f" cpx #{k}", f" bcc {name}n{k}", f" lda #{152 - k}", f" jmp {name}f", f"{name}n{k}"]
    L += [" lda #151",
          f"{name}f", " sta $0100,y",
          f"{name}x", " ldx $0160", " rts",
          f"{name}lo", " dta " + ",".join(f"<{name}r{k}" for k in range(1, 44)),
          f"{name}hi", " dta " + ",".join(f">{name}r{k}" for k in range(1, 44))]
    return L
