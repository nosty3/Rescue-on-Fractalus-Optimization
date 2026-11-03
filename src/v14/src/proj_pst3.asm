; s2-proj: bank 3 $9FE8 (lądowanie z banku 2 $9FE3) -> tail3, $9FEB przepełnienie 2. współrzędnej.
; Generuje tools/gen_proj.py.
 opt h-
 org $9fe8
 jmp $9f86
 ert * <> $9feb
 lda #$40
 ldy $2388,x
 bpl o2
 lda #$c0
o2
 sta $2487,x
 lda #0
 sta $245a,x
 jmp $9b41
 ert * > $9fff
