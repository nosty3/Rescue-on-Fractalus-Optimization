; Bank 14, $9490-: interpolacja wysokości terenu (oryginał $9000-$90C1 w tym banku), wołana z $7EEB
; (vbi2_wrap.asm) w logice lotu 25 Hz ($7CE8 raz na takt, $7DE2 co drugi takt, $7A..).
; To samo co oryginał: cztery wysokości z mapy $0900 (16x16; wiersz = ($2800 & 15) << 4 w $61, kolumna =
; $27FE & 15, sąsiedni wiersz/kolumna modulo 16), dwie interpolacje w x (ułamek $27FD), jedna w z ($27FF),
; wynik w $62 przeskalowany jak oryginał (r + r/16 + (r/16)/2 z łańcuchem przeniesień), $61 = kolejny wiersz,
; $27F0-$27F5, $27FA, $27FB = 0 (oryginał zeruje je na końcu; nikt inny ich nie czyta), X = $27FD.
; Różnice tylko w kosztach: ustawianie stron wag (oryginał $90A5, 2 x jsr) z dwóch tablic 256 B wprost, wyniki pośrednie na stosie
; zamiast w $27F0-$27F5 (i tak zerowane), interpolacja lerp2 (vbi2_lerp.asm) z v1 w X.
 opt h-
 org $9490

pA = $7f21            ; instrukcje lda abs,y/x w lerp2 (bajt starszy operandu = +2): T[15-wh], T[15-wl], T[wh], T[wl]
pB = $7f2b
pC = $7f34
pD = $7f40
lerp2 = $7f20

; strony wag z ułamka X: wh = X >> 4, wl = X & 15; strona = $80 + waga (tablice wc_tab/wd_tab), 15-waga = eor $0f
.macro wset
 lda wc_tab,x
 sta pC+2
 eor #$0f
 sta pA+2
 lda wd_tab,x
 sta pD+2
 eor #$0f
 sta pB+2
.endm

spec9000
 ldx $27fd
 wset
 lda $2800
 asl
 asl
 asl
 asl
 sta $61
 lda $27fe
 and #$0f
 ora $61
 tay
 lda $0900,y          ; h00
 pha
 iny
 tya
 and #$0f
 ora $61
 tay
 ldx $0900,y          ; h10
 pla
 jsr lerp2
 pha                  ; r0
 clc
 lda $61
 adc #$10
 sta $61
 lda $27fe
 and #$0f
 ora $61
 tay
 lda $0900,y          ; h01
 pha
 iny
 tya
 and #$0f
 ora $61
 tay
 ldx $0900,y          ; h11
 pla
 jsr lerp2
 pha                  ; r1
 ldx $27ff
 wset
 pla
 tax
 pla
 jsr lerp2
 sta $62
 ldy #0
 sty $27f0
 sty $27f1
 sty $27f2
 sty $27f3
 sty $27f4
 sty $27f5
 sty $27fa
 sty $27fb
 ldx $27fd
 lsr
 lsr
 lsr
 lsr
 tay
 clc
 adc $62
 sta $62
 tya
 lsr
 adc $62
 sta $62
 rts

wc_tab
 .rept 256
 .byte [#>>4]|$80
 .endr
wd_tab
 .rept 256
 .byte [#&$0f]|$80
 .endr
 ert * > $9800
