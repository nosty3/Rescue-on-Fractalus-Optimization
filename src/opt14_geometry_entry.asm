; Reuse the obsolete bank-2 raster body; preserve clear fallback.
 opt h-
 org $9863
 lda $80
 cmp #$55
 beq bank10
 cmp #$82
 beq bank11
 cmp #$af
 beq bank12
 lda #13
 jmp switch
bank10
 lda #10
 jmp switch
bank11
 lda #11
 jmp switch
bank12
 lda #12
 jmp switch
 ert * > $9890
 :($9890-*) dta $ff
switch
 sta $d500
