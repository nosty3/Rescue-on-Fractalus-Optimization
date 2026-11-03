; s2-proj: przepełnienie 1. współrzędnej. Generuje tools/gen_proj.py.
 opt h-
 org $9fc4
 lda #$40
 ldy $22d2,x
 bpl o1
 lda #$c0
o1
 sta $242d,x
 lda #0
 sta $2400,x
 jmp $980e
 ert * > $9fda
