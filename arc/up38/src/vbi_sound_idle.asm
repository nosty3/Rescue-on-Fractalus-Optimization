; Bank 14, kod VBI (fork VBI). Dwie łatki dzielą wspólny układ wyjść do banku 2:
;  $9880: lda #2 / sta $d500 -> dalej bank 2 $9885 (vbi_sound_exit.asm: Y=0 -> $B9B0, inaczej $B92B)
;  $9889: lda #2 / sta $d500 -> dalej bank 2 $988E (`rts`, vbi_sound_exit.asm)
; (Po `sta $d500` w oknie banku następna instrukcja pobiera się już z banku 2.)
;
; 1) Dźwięk ($B91C): szybkie pominięcie bezczynnych kanałów. Wejście ze stałego banku $B91C:
;   lda #14 / sta $d500 / jmp vbi_sound_idle
; Oryginał ($B924-$B9AD) dla każdego kanału Y=14..1 sprawdza $06DB,Y, $06A3,Y i flagę $0718 (28 cykli
; na bezczynny kanał). Flaga $0718 jest zerowana przed pętlą i rośnie tylko na ścieżce aktywnego kanału,
; więc dopóki kolejne kanały są bezczynne, oryginał nic nie zmienia poza Y. Tu: rozwinięty test
; $06DB+k | $06A3+k (10 cykli/kanał); przy pierwszym aktywnym kanale wracamy do oryginalnej pętli w $B92B
; z tym samym Y (dalej wszystko jak w oryginale). Po wszystkich bezczynnych: $B9B0 z Y=0 (jak oryginał;
; A i flagi $B9B0 i tak nadpisuje `lda #$1f`).
;
; 2) Wskaźnik kokpitu ($A83E, ścieżka $A852: nowa wartość Y <> $062B): oryginał rysuje 8 segmentów
; w pętli (ok. 70 cykli/segment, adres z tablicy $A9F8). Tu: rozwinięte, adresy i znaki stałe.
; Segment X (7..0) świeci, gdy X < Y: parzysty -> ($b4|$80 : $34), nieparzysty -> 2 znaki
; ($b7|$80, $b8 : $37, $38). Stan końcowy zmiennych jak po oryginalnej pętli: $BB/$BC = $3364,
; $BD = $BE = $FF, $BF = Y, $C0 = 0, $062B = Y, X = 0. A, Y i flagi nadpisuje wołający ($A94D).
 opt h-
 org $9801
vbi_sound_idle
 lda $0631
 beq no_fx
 jsr $b9e2
no_fx
 lda #0
 sta $0718
 .rept 14, 14-#
 lda $06db+:1
 ora $06a3+:1
 bne active_:1
 .endr
 ldy #0
 ert * <> $9880
exit
 lda #2
 sta $d500
 ert * <> $9885
active_14
 ldy #14
 bne exit
 ert * <> $9889
gauge_exit
 lda #2
 sta $d500
 ert * <> $988e
 .rept 13, 13-#
active_:1
 ldy #:1
 bne exit
 .endr

; segment parzysty: X, adres
.macro seg_even
 lda #$34
 cpy #:1+1
 bcc @+
 lda #$b4
@ sta :2
.endm
; segment nieparzysty: X, adres
.macro seg_odd
 lda #$37
 ldx #$38
 cpy #:1+1
 bcc @+
 lda #$b7
 ldx #$b8
@ sta :2
 stx :2+1
.endm

 ert * <> $98c2
vbi_gauge
 sty $062b
 sty $bf
 seg_odd 7, $34b7
 seg_even 6, $3487
 seg_odd 5, $3456
 seg_even 4, $3426
 seg_odd 3, $33f5
 seg_even 2, $33c5
 seg_odd 1, $3394
 seg_even 0, $3364
 lda #$64
 sta $bb
 lda #$33
 sta $bc
 lda #$ff
 sta $bd
 sta $be
 ldx #0
 stx $c0
 jmp gauge_exit
 ert * > $9eff
