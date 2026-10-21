; Private interpolation helper; called inside VBI. Updated operands are
; fully initialized before each use. DLI does not call this helper.
 opt h-
 org $7eeb
 lda #14
 sta $d500
 jsr $9000
 php
 pha
 lda #2
 sta $d500
 pla
 plp
 rts
 :($7f20-*) dta $ea
mix
 stx value1+1
 tax
high0
 lda $8000,x
 sta sum1+1
 lda $9e00,x
 tax
low0
 lda $8000,x
 clc
sum1
 adc #0
 sta sum2+1
value1
 ldx #0
high1
 lda $8000,x
sum2
 adc #0
 sta sum3+1
 lda $9e00,x
 tax
low1
 lda $8000,x
sum3
 adc #0
 rts
 ert * > $7fc2
 :($7fc2-*) dta $ea
