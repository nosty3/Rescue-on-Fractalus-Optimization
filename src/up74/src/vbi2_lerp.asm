; Kod rezydentny $7F20-$7F4A (43 bajty): interpolacja wysokości terenu, wołana tylko z $9000 (bank 14),
; tu z vbi2_interp14.asm (spec9000). Wejście A = v0, X = v1; strony tablic (bank 14 $8000-$8FFF, 16 stron
; wag) wpisuje wołający w operandy pA..pD (bajt starszy adresu). Wynik jak oryginał: łańcuch
; t2 + t1 (clc), + t3 z przeniesieniem, + t4 z przeniesieniem, gdzie t1 = T[15-wh][v0], t2 = T[15-wl][v0>>4],
; t3 = T[wh][v1], t4 = T[wl][v1>>4] (tabela $9E00 = i>>4). Oryginał trzymał v1 w operandzie `ldx #` (stx+ldx),
; tu v1 zostaje w X, a v0 idzie przez Y (lda abs,y): 56 zamiast 62 cykli. Y po powrocie = v0>>4 (martwe:
; spec9000 ładuje Y przed użyciem), flagi z ostatniego adc jak w oryginale.
 opt h-
 org $7f20
lerp2
 tay
pA lda $8000,y
 sta s1+1
 lda $9e00,y
 tay
pB lda $8000,y
 clc
s1 adc #0
 sta s2+1
pC lda $8000,x
s2 adc #0
 sta s3+1
 lda $9e00,x
 tax
pD lda $8000,x
s3 adc #0
 rts
 ert * > $7f4b
 ert pA <> $7f21
 ert pB <> $7f2b
 ert pC <> $7f34
 ert pD <> $7f40
