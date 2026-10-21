; Bank 2 trampoline; preserve incoming carry/overflow.
 opt h-
 org $982f
 php
 cpx #3
 beq first
 cpx #51
 beq second
 plp
 stx $94
 ldy #42
 lda #0
 jmp $921a
first
 lda #6
 jmp switch
second
 lda #8
 jmp switch
 :($9860-*) dta $ff
switch
 sta $d500
 ert * <> $9863
