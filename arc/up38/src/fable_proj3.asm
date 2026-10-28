; Rzutowanie punktów terenu (oryginał bank 2 $85D4-$87D1 + dzielenie $8224) przeniesione do banku 3.
; Generuje tools/gen_fable.py. Wejście: X = indeks punktu (0..44), bank 3 już wybrany (stub $984F w banku 2).
; Wyjście jak oryginał: $2400/$242D/$245A/$2487,X; flaga $10 w $24B4,X; $9F = licznik przesunięć; $AE-$B2 jak po
; oryginalnym drugim dzieleniu; $B5 scratch; X zachowany; + szybki test widoczności $8AF0 (rzadka ścieżka -> bank 2).
; Powrót: lda #2 / sta $D500 -> bank 2 rts (adres dobiera patches_fable.py).
 opt h-
 org $97f1
; --- ścieżki rzadkie 1. współrzędnej (blisko głowy rzutowania pod $9854) ---
c1ovf
 lda $22d2,x
 bmi c1ovfn
 lda #$40
 sta $242d,x
 lda #0
 sta $2400,x
 jmp c2reload
c1ovfn
 lda #$c0
 sta $242d,x
 lda #0
 sta $2400,x
 jmp c2reload
c1neg
 sec
 lda #0
 sbc $22a4,x
 sta $b0
 lda #0
 sbc $22d2,x
 tay
 jmp c1cmp
c1sh
 sty $b1
 ldy #0
c1shl
 asl $ae
 rol $af
 iny
 cpy #8
 beq c1ovf
 lda $b1
 cmp $af
 bcc c1divn
 bne c1shl
 lda $b0
 cmp $ae
 bcs c1shl
 lda $b1
c1divn
 sty $9f
 jmp div1
c1div0b
 tya
 jmp c1div0
rareend
 ert * > $9847
 :($9847-*) dta $ff
; $9847: rzadka ścieżka widoczności -> bank 2 $984C (jmp $8AF8); X = punkt, Y = $2276,X
 lda #2
 sta $d500
 :($984c-*) dta $ff
pdisp
 jmp prolog3
 :($984f-*) dta $ff
 lda #2
 sta $d500
 :($9854-*) dta $ff
; --- wejście: po stubie banku 2 pod $984F; C=0 rzutowanie (X = punkt), C=1 prolog $87D3 (X = $30/0) ---
proj
 bcs pdisp
 lda $24b4,x
 ora #$10
 sta $24b4,x
 lda $2300,x
 sta $ae
 lda $232e,x
 sta $af
 lda $22d2,x
 bmi c1neg
 tay
 lda $22a4,x
 sta $b0
 tya
c1cmp
 cmp $af
 bcc c1div0
 bne c1sh
 lda $b0
 cmp $ae
 bcc c1div0b
 bcs c1sh
c1div0
 ldy #0
 sty $9f
div1
 asl $b0
 rol @
 cmp $af
 bcc an0
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs an0
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
an0
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc an1
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs an1
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
an1
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc an2
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs an2
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
an2
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc an3
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs an3
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
an3
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc an4
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs an4
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
an4
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc an5
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs an5
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
an5
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc an6
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs an6
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
an6
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc an7
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs an7
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
an7
 rol $b2
 ldy $9f
 bne c1yn
 lda $22d2,x
 bmi c1y0n
 lda $b2
 lsr @
 sec
 adc $b2
 ror @
 lsr @
 ora #$80
 sta $2400,x
 lda #0
 sta $242d,x
 jmp c2noreload
c1yn
 lda #0
c1ynl
 asl $b2
 rol @
 dey
 bne c1ynl
 sta $b5
 lsr @
 tay
 lda $b2
 ror @
 clc
 adc $b2
 sta $b2
 tya
 adc $b5
 lsr @
 ror $b2
 lsr @
 ror $b2
 sta $b5
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
c1y0n
 lda $b2
 lsr @
 sec
 adc $b2
 ror @
 lsr @
 eor #$ff
 sec
 adc #$80
 sta $2400,x
 lda #0
 sta $242d,x
 jmp c2noreload
 :118 dta $ff
c2reload
 lda $2300,x
 sta $ae
 lda $232e,x
 sta $af
c2noreload
 lda $2388,x
 bmi c2neg
 tay
 lda $235b,x
 sta $b0
 tya
c2cmp
 cmp $af
 bcc c2div0
 bne c2sh
 lda $b0
 cmp $ae
 bcc c2div0b
 bcs c2sh
c2neg
 sec
 lda #0
 sbc $235b,x
 sta $b0
 lda #0
 sbc $2388,x
 tay
 jmp c2cmp
c2sh
 sty $b1
 ldy #0
c2shl
 asl $ae
 rol $af
 iny
 cpy #8
 beq c2ovf
 lda $b1
 cmp $af
 bcc c2divn
 bne c2shl
 lda $b0
 cmp $ae
 bcs c2shl
 lda $b1
c2divn
 sty $9f
 jmp div2
c2ovf
 lda $2388,x
 bmi c2ovfn
 lda #$40
 sta $2487,x
 lda #0
 sta $245a,x
 jmp adjust
c2ovfn
 lda #$c0
 sta $2487,x
 lda #0
 sta $245a,x
 jmp adjust
c2div0b
 tya
c2div0
 ldy #0
 sty $9f
div2
 asl $b0
 rol @
 cmp $af
 bcc bn0
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs bn0
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
bn0
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bn1
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs bn1
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
bn1
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bn2
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs bn2
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
bn2
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bn3
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs bn3
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
bn3
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bn4
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs bn4
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
bn4
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bn5
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs bn5
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
bn5
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bn6
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs bn6
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
bn6
 rol $b2
 asl $b0
 rol @
 cmp $af
 bcc bn7
 tay
 lda $b0
 sbc $ae
 sta $b0
 tya
 sbc $af
 bcs bn7
 lda $b0
 adc $ae
 sta $b0
 tya
 clc
bn7
 rol $b2
 sta $b1
 ldy $9f
 beq c2y0
 jmp c2yn
c2y0
 lda #0
 sta $2487,x
 lda $2388,x
 bmi c2y0n
 lda $b2
 lsr @
 sec
 adc $b2
 ror @
 lsr @
 ora #$80
 sta $245a,x
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
vis
 ldy $2276,x
 lda $0a00,y
 bne rare
ret
 lda #2
 sta $d500
retend
; --- za przełącznikiem (bank 3; wykonanie trafia tu tylko gałęziami z c2y0/adjust/vis) ---
c2y0n
 lda $b2
 lsr @
 sec
 adc $b2
 ror @
 lsr @
 eor #$ff
 sec
 adc #$80
 sta $245a,x
 jmp adjust
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
rare
 jmp $9847
c2yn
 lda #0
c2ynl
 asl $b2
 rol @
 dey
 bne c2ynl
 sta $b5
 lsr @
 tay
 lda $b2
 ror @
 clc
 adc $b2
 sta $b2
 tya
 adc $b5
 lsr @
 ror $b2
 lsr @
 ror $b2
 sta $b5
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
; --- prolog rysowania terenu (oryginał $87D3-$885D), wejście przez pdisp; X = $30 albo 0 ---
; tabela $3920-$39D7 i $270E-$272D ($91E0) rozwinięte w banku 14 (fable_pro14.asm), wypełnienia $263A-$26E1 tu.
 ert * > $9d7e
 :($9d7e-*) dta $ff
prolog3
 stx $a7
hop14
 lda #14
 sta $d500
 lda #$67
 sta $263a
 sta $263b
 sta $263c
 sta $263d
 sta $263e
 sta $263f
 sta $2640
 sta $2641
 sta $2642
 sta $2643
 sta $2644
 sta $2645
 sta $2646
 sta $2647
 sta $2648
 sta $2649
 sta $264a
 sta $264b
 sta $264c
 sta $264d
 lda #$6b
 sta $264e
 sta $264f
 sta $2650
 sta $2651
 sta $2652
 sta $2653
 sta $2654
 sta $2655
 sta $2656
 sta $2657
 sta $2658
 sta $2659
 sta $265a
 sta $265b
 sta $265c
 sta $265d
 sta $265e
 sta $265f
 sta $2660
 sta $2661
 sta $2662
 sta $2663
 sta $2664
 sta $2665
 sta $2666
 sta $2667
 sta $2668
 sta $2669
 sta $266a
 sta $266b
 sta $266c
 sta $266d
 sta $266e
 sta $266f
 sta $2670
 sta $2671
 sta $2672
 sta $2673
 sta $2674
 sta $2675
 sta $2676
 sta $2677
 sta $2678
 sta $2679
 sta $267a
 sta $267b
 sta $267c
 sta $267d
 sta $267e
 sta $267f
 sta $2680
 sta $2681
 sta $2682
 sta $2683
 sta $2684
 sta $2685
 sta $2686
 sta $2687
 sta $2688
 sta $2689
 sta $268a
 sta $268b
 sta $268c
 sta $268d
 sta $268e
 sta $268f
 sta $2690
 sta $2691
 sta $2692
 sta $2693
 sta $2694
 sta $2695
 sta $2696
 sta $2697
 sta $2698
 sta $2699
 sta $269a
 sta $269b
 sta $269c
 sta $269d
 sta $269e
 sta $269f
 sta $26a0
 sta $26a1
 sta $26a2
 sta $26a3
 sta $26a4
 sta $26a5
 sta $26a6
 sta $26a7
 sta $26a8
 sta $26a9
 sta $26aa
 sta $26ab
 sta $26ac
 sta $26ad
 sta $26ae
 sta $26af
 sta $26b0
 sta $26b1
 sta $26b2
 sta $26b3
 sta $26b4
 sta $26b5
 sta $26b6
 sta $26b7
 sta $26b8
 sta $26b9
 sta $26ba
 sta $26bb
 sta $26bc
 sta $26bd
 sta $26be
 sta $26bf
 sta $26c0
 sta $26c1
 sta $26c2
 sta $26c3
 sta $26c4
 sta $26c5
 sta $26c6
 sta $26c7
 sta $26c8
 sta $26c9
 sta $26ca
 sta $26cb
 sta $26cc
 sta $26cd
 sta $26ce
 sta $26cf
 sta $26d0
 sta $26d1
 lda #$67
 sta $26d2
 sta $26d3
 sta $26d4
 sta $26d5
 sta $26d6
 sta $26d7
 sta $26d8
 sta $26d9
 sta $26da
 sta $26db
 sta $26dc
 sta $26dd
 sta $26de
 sta $26df
 sta $26e0
 sta $26e1
 lda $28
 sta $2907
 lda $29
 sta $2908
 lda #$80
 sta $28e7
 sta $28e8
 sta $2912
 sta $2913
 sta $2914
 sta $2915
 ldy $a7
 bne pro1
 sta $28ea
 sta $79
pro1
 lda #0
 sta $28ed
 sta $28fb
 sta $28fc
 lda $6a
 bmi pro2
 inc $28fc
pro2
 jmp $984f
 ert * > $9ff0
