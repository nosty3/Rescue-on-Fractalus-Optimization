; s2-proj: rzadki koniec pętli krawędzi (żadna para po obu testach). Generuje tools/gen_proj.py.
 opt h-
P1R = $8224
 org $82b4
 ldy #72
fn
 dey
 bmi fnd
 ldx P1R,y
 lda $24b4,x
 and #$a0
 bne fn
 sty $272e
 beq fn
fnd
 ldy $272e
 cpy #$ff
 bne fn1
 lda $28db
 sta $272e
 jmp fn2
fn1
 tya
 asl @
 eor #$ff
 sec
 adc #144
 sta $272e
fn2
 ldx $8224
 lda $24b4,x
 and #$a0
 bne fn3
 ldx $826c
fn3
 ldy #0
 jmp $879d
 ert * > $8304
