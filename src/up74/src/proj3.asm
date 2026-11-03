; s2-proj: rzutowanie punktów terenu (bank 3). Generuje tools/gen_proj.py - nie edytować ręcznie.
; Bank 3 $963A-$97F0 zostaje $FF jak w masterze: kod przed lotem czyta te bajty (zmiana zmienia RAM na wejściu
; do lotu, bisekcja w Altirze: s2proj/bis.py). Obszar: $97F1-$9F82 (wyspy $9847-$9853 i $9D7E-$9D84 bez zmian).
 opt h-
c1ovf = $9fc4
c2ovf = $9feb
 org $97f1
 :($9800-*) dta $ff
; ===== $9800: wejścia rzadkie 1. współrzędnej + cofnięcia kroków 0-2 (zasięg gałęzi z dzielenia) =====
c1ge
 bne c1shj
 ldy $b0
 cpy $ae
 bcs c1shj
 jmp div1
c1shj
 jmp c1sh
c2reload
 lda $2300,x
 sta $ae
 lda $232e,x
 sta $af
 jmp c2noreload
 ert * > $9847-33
 :($9847-33-*) dta $ff
au0
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp az0
au1
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp az1
au2
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp az2
 ert * > $9847
 :($9847-*) dta $ff
; $9847: rzadka ścieżka widoczności -> bank 2 $984C (jmp $8AF8); X = punkt, Y = $2276,X
 lda #2
 sta $d500
 jmp $9f86
 lda #2
 sta $d500
 ert * <> $9854
; ===== $9854: rzutowanie (X = punkt) =====
proj
 lda $2300,x
 sta $ae
 lda $232e,x
 sta $af
 lda $22a4,x
 sta $b0
 lda $22d2,x
 bpl c1cmp
 lda #0
 sec
 sbc $b0
 sta $b0
 lda #0
 sbc $22d2,x
c1cmp
 cmp $af
 bcs c1ge
div1
 asl $b0
 rol @
 cmp $af
 bcc az0
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc au0
az0
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc az1
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc au1
az1
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc az2
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc au2
az2
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc az3
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc au3
az3
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc az4
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc au4
az4
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc az5
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc au5
az5
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc az6
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc au6
az6
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc az7
 bne az7
 lda $b0
 cmp $ae
az7
 rol $b2
; 1. współrzędna, n = 0: X = T[Q] albo 0 - T[Q], hi 0
 ldy $b2
 lda $22d2,x
 bpl c1p
 lda #0
 sec
 sbc tab,y
 sta $2400,x
 lda #0
 sta $242d,x
 jmp c2noreload
au3
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp az3
au4
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp az4
au5
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp az5
au6
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp az6
c2ge
 bne c2shj
 ldy $b0
 cpy $ae
 bcs c2shj
 jmp div2
c2shj
 jmp c2sh
bu0
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp bz0
bu1
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp bz1
bu2
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp bz2
 :12 dta $ff
c1p
 lda tab,y
 sta $2400,x
 lda #0
 sta $242d,x
c2noreload
 lda $235b,x
 sta $b0
 lda $2388,x
 bpl c2cmp
 lda #0
 sec
 sbc $b0
 sta $b0
 lda #0
 sbc $2388,x
c2cmp
 cmp $af
 bcs c2ge
div2
 asl $b0
 rol @
 cmp $af
 bcc bz0
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc bu0
bz0
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bz1
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc bu1
bz1
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bz2
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc bu2
bz2
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bz3
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs bz3
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
bz3
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bz4
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs bz4
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
bz4
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bz5
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs bz5
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
bz5
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bz6
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs bz6
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
bz6
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bz7
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs bz7
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
bz7
 rol $b2
; 2. współrzędna, n = 0: Y16 = (+-T[Q]) + adj ($270E[X >> 3]) jednym dodawaniem
 sta $b1
 lda $2388,x
 bpl c2p
 lda $242d,x
 bne c2nx
 lda $2400,x
 lsr @
 lsr @
 lsr @
 tay
 lda $270e,y
 bmi c2nm
 ldy $b2
 sec
 sbc tab,y
 sta $245a,x
 lda #0
 adc #0
 sta $2487,x
vis
 lda $24b4,x
 ora #$10
 sta $24b4,x
 ldy $2276,x
 lda $0a00,y
 bne rare
ret
 lda #2
 sta $d500
; ===== za przełącznikiem: tylko gałęzie i skoki =====
rare
 jmp $9847
c2nx
 ldy $b2
 lda #0
 sec
 sbc tab,y
 sta $245a,x
 lda #0
 sta $2487,x
 lda $242d,x
 jmp adjx
c2nm
 ldy $b2
 sec
 sbc tab,y
 sta $245a,x
 lda #$ff
 adc #0
 sta $2487,x
 jmp vis
c2p
 lda $242d,x
 bne c2px
 lda $2400,x
 lsr @
 lsr @
 lsr @
 tay
 lda $270e,y
 bmi c2pm
 ldy $b2
 clc
 adc tab,y
 sta $245a,x
 lda #0
 adc #0
 sta $2487,x
 jmp vis
c2pm
 ldy $b2
 clc
 adc tab,y
 sta $245a,x
 lda #$ff
 adc #0
 sta $2487,x
 jmp vis
c2px
 ldy $b2
 lda tab,y
 sta $245a,x
 lda #0
 sta $2487,x
 lda $242d,x
 jmp adjx
; ===== ogólna poprawka Y (ścieżki n > 0 i przepełnienia): jak oryginał $8792 =====
adjust
 lda $242d,x
 bne adjx
 lda $2400,x
 lsr @
 lsr @
 lsr @
 tay
 lda $270e,y
 bmi adjm
adjp
 clc
 adc $245a,x
 sta $245a,x
 lda $2487,x
 adc #0
 sta $2487,x
 jmp vis
adjx
 bmi adjneg
 lda $272d
 bmi adjm
 bpl adjp
adjneg
 lda $270e
 bmi adjm
 bpl adjp
adjm
 clc
 adc $245a,x
 sta $245a,x
 lda $2487,x
 adc #$ff
 sta $2487,x
 jmp vis
cu0
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp cz0
cu1
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp cz1
cu2
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp cz2
cu3
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp cz3
; ===== dzielenie z przesunięciem n > 0 (obie współrzędne); $9F = n albo n + 8 =====
nkdiv
 asl $b0
 rol @
 cmp $af
 bcc cz0
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc cu0
cz0
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc cz1
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc cu1
cz1
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc cz2
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc cu2
cz2
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc cz3
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc cu3
cz3
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc cz4
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc cu4
cz4
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc cz5
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc cu5
cz5
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc cz6
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc cu6
cz6
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc cz7
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcc cu7
cz7
 rol $b2
 sta $b1
 ldy $9f
 cpy #8
 bcs c2nkj
 dey
 beq c1n1
 jmp c1nk
c2nkj
 jmp c2nk
cu4
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp cz4
cu5
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp cz5
cu6
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp cz6
cu7
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
 jmp cz7
; 1. współrzędna, n > 0: V = Q << n, r = (V + V>>1) >> 2 (16 bitów), X = $80 +- r (jak oryginał c1yn)
; n = 1: r = floor(3Q/4) = (Q + Q>>1) >> 1 (suma 9-bitowa), $B5 = 0; X = $80 +- r
c1n1
 lda $b2
 lsr @
 clc
 adc $b2
 ror @
 sta $b2
 sty $b5
 ldy $22d2,x
 bmi c1n1n
 clc
 adc #$80
 sta $2400,x
 lda #0
 adc #0
 sta $242d,x
 jmp c2reload
c1n1n
 lda #$80
 sec
 sbc $b2
 sta $2400,x
 lda #0
 sbc #0
 sta $242d,x
 jmp c2reload
c2nk
 cpy #9
 bne c2nkg
 lda $b2
 lsr @
 clc
 adc $b2
 ror @
 sta $b2
 ldy #0
 sty $b5
 ldy $2388,x
 bmi c2n1n
 clc
 adc #$80
 sta $245a,x
 lda #0
 adc #0
 sta $2487,x
 jmp adjust
c2n1n
 lda #$80
 sec
 sbc $b2
 sta $245a,x
 lda #0
 sbc #0
 sta $2487,x
 jmp adjust
c2nkg
 tya
 sbc #9
 tay
 jsr rcalc
 lda $2388,x
 bmi c2ynn
 lda #$80
 clc
 adc $b2
 sta $245a,x
 lda $b5
 adc #0
 sta $2487,x
 jmp adjust
c2ynn
 lda #$80
 sec
 sbc $b2
 sta $245a,x
 lda #0
 sbc $b5
 sta $2487,x
 jmp adjust
rcalc
 dey
 bne rc3
 lda $b2
 lsr @
 clc
 adc $b2
 sta $b2
 lda #0
 rol @
 sta $b5
 rts
rc3
 lda #0
 sta $b5
 lda $b2
 asl @
 rol $b5
 adc $b2
 sta $b2
 bcc rc3a
 inc $b5
rc3a
 dey
 beq rc3d
rc3l
 asl $b2
 rol $b5
 dey
 bne rc3l
rc3d
 rts
 ert * > $9d7e
 :($9d7e-*) dta $ff
; $9D7E-$9D84 bez zmian (stary prolog3: stx $a7; hop14: lda #14 / sta $D500 -> bank 14)
 dta $86,$a7,$a9,$0e,$8d,$00,$d5
; $9D85: powrót z banku 14 (wypełnienie occ $263A-$26E1 przeniesione do banku 14) -> koniec części tablicowej
 jmp $9f83
c1sh
 sta $b1
 asl $ae
 rol $af
 cmp $af
 bcc c1sh1
 bne c1sh2
 lda $b0
 cmp $ae
 lda $b1
 bcs c1sh2
c1sh1
 ldy #1
 sty $9f
 jmp nkdiv
c1sh2
 ldy #1
c1shl
 asl $ae
 rol $af
 iny
 cpy #8
 beq c1ovfj
 cmp $af
 bcc c1divn
 bne c1shl
 lda $b0
 cmp $ae
 lda $b1
 bcs c1shl
c1divn
 sty $9f
 jmp nkdiv
c1ovfj
 jmp c1ovf
c2sh
 sta $b1
 ldy #8
c2shl
 asl $ae
 rol $af
 iny
 cpy #16
 beq c2ovfj
 cmp $af
 bcc c2divn
 bne c2shl
 lda $b0
 cmp $ae
 lda $b1
 bcs c2shl
c2divn
 sty $9f
 jmp nkdiv
c2ovfj
 jmp c2ovf
 ert * > $9e00
 :($9e00-*) dta $ff
; ===== T[Q] = $80 + ((Q + Q>>1 + 1) >> 2) =====
tab
 dta $80,$80,$81,$81,$81,$82,$82,$82,$83,$83,$84,$84,$84,$85,$85,$85
 dta $86,$86,$87,$87,$87,$88,$88,$88,$89,$89,$8a,$8a,$8a,$8b,$8b,$8b
 dta $8c,$8c,$8d,$8d,$8d,$8e,$8e,$8e,$8f,$8f,$90,$90,$90,$91,$91,$91
 dta $92,$92,$93,$93,$93,$94,$94,$94,$95,$95,$96,$96,$96,$97,$97,$97
 dta $98,$98,$99,$99,$99,$9a,$9a,$9a,$9b,$9b,$9c,$9c,$9c,$9d,$9d,$9d
 dta $9e,$9e,$9f,$9f,$9f,$a0,$a0,$a0,$a1,$a1,$a2,$a2,$a2,$a3,$a3,$a3
 dta $a4,$a4,$a5,$a5,$a5,$a6,$a6,$a6,$a7,$a7,$a8,$a8,$a8,$a9,$a9,$a9
 dta $aa,$aa,$ab,$ab,$ab,$ac,$ac,$ac,$ad,$ad,$ae,$ae,$ae,$af,$af,$af
 dta $b0,$b0,$b1,$b1,$b1,$b2,$b2,$b2,$b3,$b3,$b4,$b4,$b4,$b5,$b5,$b5
 dta $b6,$b6,$b7,$b7,$b7,$b8,$b8,$b8,$b9,$b9,$ba,$ba,$ba,$bb,$bb,$bb
 dta $bc,$bc,$bd,$bd,$bd,$be,$be,$be,$bf,$bf,$c0,$c0,$c0,$c1,$c1,$c1
 dta $c2,$c2,$c3,$c3,$c3,$c4,$c4,$c4,$c5,$c5,$c6,$c6,$c6,$c7,$c7,$c7
 dta $c8,$c8,$c9,$c9,$c9,$ca,$ca,$ca,$cb,$cb,$cc,$cc,$cc,$cd,$cd,$cd
 dta $ce,$ce,$cf,$cf,$cf,$d0,$d0,$d0,$d1,$d1,$d2,$d2,$d2,$d3,$d3,$d3
 dta $d4,$d4,$d5,$d5,$d5,$d6,$d6,$d6,$d7,$d7,$d8,$d8,$d8,$d9,$d9,$d9
 dta $da,$da,$db,$db,$db,$dc,$dc,$dc,$dd,$dd,$de,$de,$de,$df,$df,$df
c1nk
 jsr rcalc
 lda $22d2,x
 bmi c1ynn
 lda #$80
 clc
 adc $b2
 sta $2400,x
 lda $b5
 adc #0
 sta $242d,x
 jmp c2reload
c1ynn
 lda #$80
 sec
 sbc $b2
 sta $2400,x
 lda #0
 sbc $b5
 sta $242d,x
 jmp c2reload
 ert * > $9f83
 :($9f83-*) dta $ff
