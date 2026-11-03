; Bank 14, $90C2-$97FF (wolne w v11): dźwięk VBI, runda 2 (łatka vbi2_sound).
; Wejście ze stałego banku $B91C: lda #14 / sta $d500 / jmp snd_scan (operand $B921 przestawiony z $9801).
;
; 1) snd_scan: jak vbi_sound_idle ($9801, runda 1), ale kanały testowane parami (18 cykli na parę zamiast
;    2 x 11). Para aktywna -> stub pairK ustala Y = pierwszy aktywny kanał (14..1) i skacze do `exit`
;    ($9880: lda #2 / sta $d500 -> bank 2 $9885 -> oryginalna pętla $B92B z tym Y). Wszystkie bezczynne ->
;    snd_queue bez przełączania banku (oryginał: Y=0 -> $B9B0; A i flagi tam nadpisywane).
;
; 2) snd_queue: kolejka zdarzeń dźwięku, oryginał $B9B0-$B9E1 + przydział głosów $BAA3-$BAF5 + wybór
;    minimum $BB19 (bank 2 $9D3B) i maksimum $BB3E (bank 2 $9E7D). Stały bank $B9B0 dostaje
;    lda #14 / sta $d500 / jmp snd_queue (koniec oryginalnej pętli kanałów po aktywnych kanałach).
;    Co klatkę logiki (25 Hz) lot wrzuca trzy zdarzenia "przydziel" (kanały 13, 14, 12; $B327, $764A, $76A7),
;    a oryginał przy każdym liczy od nowa minimum głośności kanałów przydzielonych 1..12 ($0714-$0716),
;    choć wejścia ($0705,X i $066B,X dla X = 1..12) się nie zmieniły. Tu pętla ma dwa stany:
;    loop_i = minimum nieaktualne (na wejściu i po każdej zmianie $0705/$066B: kradzież, przeniesienie,
;    inicjalizacja kanału $BCAB), loop_v = $0714-$0716 równe temu, co policzyłaby $BB19. W stanie V
;    wywołania $BB19 oryginału są pomijane; po $BB3E bez przeniesienia (oryginał: $BB3E ustawia $0716 =
;    maksimum, potem $BB19 wraca do minimum) odtwarzane jest $0716 = $0714 - kanał Y (1..12) jest
;    przydzielony, więc $BB19 na pewno znalazłaby minimum i zapisała $0716 = $0714.
;    Zapisy do sprzętu (jsr $bb02: AUDF/AUDC kanału Y, jeśli ma głos) w tej samej kolejności i z tymi samymi
;    wartościami co oryginał. Rejestry na wyjściu martwe (VBI: $B6CB `lda $41`, potem bez X/Y). Wyjście przez
;    $9889 (runda 1: lda #2 / sta $d500 / bank 2 $988E rts), bo $B91C woła też menu/tytuł spoza VBI
;    (bank 2 musi zostać; z bankiem 14 na wyjściu START w menu nie wchodził do lotu).
;
; 3) min_calc / max_calc: to samo co $BB19 / $BB3E, ale bieżące ekstremum w Y, indeks w X (zamiast
;    $0716 w pamięci) i bez `and #$0f`: $066C-$0677 zawsze < 16 (wszystkie zapisy w kodzie to 0, 1, $0F,
;    wartość po `and #$0f` albo 4..15 z $7691; $066B = $A0 to kanał 0, nigdy nie skanowany). Wyniki
;    $0714-$0717 jak w oryginale (min: `<` czyli remis = niższy indeks; max: `>=` czyli remis = wyższy
;    indeks, pierwszy kandydat zawsze brany; $0717 bez zmian, gdy brak kandydatów).
 opt h-
 org $90c2

exit = $9880          ; runda 1: lda #2 / sta $d500 -> bank 2 $9885 (Y = aktywny kanał -> $B92B)

snd_scan
 lda $0631
 beq no_fx
 jsr $b9e2
no_fx
 lda #0
 sta $0718
 lda $06db+14
 ora $06a3+14
 ora $06db+13
 ora $06a3+13
 bne pair14
 lda $06db+12
 ora $06a3+12
 ora $06db+11
 ora $06a3+11
 bne pair12
 lda $06db+10
 ora $06a3+10
 ora $06db+9
 ora $06a3+9
 bne pair10
 lda $06db+8
 ora $06a3+8
 ora $06db+7
 ora $06a3+7
 bne pair8
 lda $06db+6
 ora $06a3+6
 ora $06db+5
 ora $06a3+5
 bne pair6
 lda $06db+4
 ora $06a3+4
 ora $06db+3
 ora $06a3+3
 bne pair4
 lda $06db+2
 ora $06a3+2
 ora $06db+1
 ora $06a3+1
 bne pair2
 jmp snd_queue

; para (k, k-1): Y = k gdy kanał k aktywny, inaczej k-1 (ten jest aktywny)
pair14
 ldy #14
 lda $06db+14
 ora $06a3+14
 bne go_exit
 dey
 bne go_exit
pair12
 ldy #12
 lda $06db+12
 ora $06a3+12
 bne go_exit
 dey
 bne go_exit
pair10
 ldy #10
 lda $06db+10
 ora $06a3+10
 bne go_exit
 dey
 bne go_exit
pair8
 ldy #8
 lda $06db+8
 ora $06a3+8
 bne go_exit
 dey
 bne go_exit
pair6
 ldy #6
 lda $06db+6
 ora $06a3+6
 bne go_exit
 dey
 bne go_exit
pair4
 ldy #4
 lda $06db+4
 ora $06a3+4
 bne go_exit
 dey
 bne go_exit
pair2
 ldy #2
 lda $06db+2
 ora $06a3+2
 bne go_exit
 dey
go_exit
 jmp exit

; ---------------------------------------------------------------- kolejka zdarzeń (oryginał $B9B0)
snd_queue
 lda #$1f
 cmp $73
 bcs q1
 sta $73
q1
 cmp $74
 bcs loop_i
 sta $74

; --- stan I: minimum nieaktualne
loop_i
 ldy $74
 cpy $73
 beq done
 lda $0719,y
 bpl start_i
 and #$7f
 tax
 jsr $bcab
 jmp next_i
start_i
 tay
 jsr $bb02
 cpx #0
 bne asg_i
 lda $066b,y
 and #$0f
 cmp $0714
 bcc next_i
 bne steal
 cpy $0715
 bcc next_i
steal                 ; kanał Y bez głosu zabiera głos kanałowi $0715 (oryginał $BABC)
 ldx $0715
 lda $0705,x
 sta $0705,y
 lda #0
 sta $0705,x
 jsr $bb02
 jsr min_calc
 jmp next_v
asg_i
 cpy #$0d
 bcc low_i
 jsr min_calc
 jmp next_v
low_i
 jsr max_calc
 ldx $0715
 cpx $0717
 beq nomove_i
 jsr move
nomove_i
 jsr min_calc
 jmp next_v
next_i
 dec $74
 bpl loop_i
 lda #$1f
 sta $74
 jmp loop_i
done
 jmp $9889            ; runda 1 gauge_exit: lda #2 / sta $d500 -> bank 2 $988E: rts (do $B6CB albo do menu)

; --- stan V: $0714-$0716 aktualne
loop_v
 ldy $74
 cpy $73
 beq done
 lda $0719,y
 bpl start_v
 and #$7f
 tax
 jsr $bcab
 jmp next_i
start_v
 tay
 jsr $bb02
 cpx #0
 bne asg_v
 lda $066b,y
 and #$0f
 cmp $0714
 bcc next_v
 bne steal
 cpy $0715
 bcs steal
 bcc next_v
asg_v
 cpy #$0d
 bcs next_v
 jsr max_calc
 ldx $0715
 cpx $0717
 beq nomove_v
 jsr move
 jsr min_calc
 jmp next_v
nomove_v
 lda $0714
 sta $0716
next_v
 dec $74
 bpl loop_v
 lda #$1f
 sta $74
 jmp loop_v

; głos kanału X (= $0715) przechodzi do kanału $0717 (oryginał $BADF), potem zapis AUDF/AUDC nowego kanału
move
 ldy $0717
 lda $0705,x
 sta $0705,y
 lda #0
 sta $0705,x
 jmp $bb02

; ---------------------------------------------------------------- minimum ($BB19): Y = min, X = kanał
.macro mink
 lda $0705+:1
 beq mk_:1
 cpy $066b+:1
 beq mk_:1
 bcc mk_:1
 ldy $066b+:1
 ldx #:1
mk_:1
.endm

min_calc
 ldy #$10
 ldx #0
 mink 1
 mink 2
 mink 3
 mink 4
 mink 5
 mink 6
 mink 7
 mink 8
 mink 9
 mink 10
 mink 11
 mink 12
 sty $0716
 cpy #$10
 beq mdone
 sty $0714
 stx $0715
mdone
 rts

; ---------------------------------------------------------------- maksimum ($BB3E): Y = max, X = kanał
.macro maxk
 lda $0705+:1
 beq xc_:1
 lda $0715
 cmp #:1
 bne xs_:1
xc_:1
 cpy $066b+:1
 beq xt_:1
 bcs xs_:1
xt_:1
 ldy $066b+:1
 ldx #:1
xs_:1
.endm

max_calc
 ldy #0
 ldx #0
 maxk 1
 maxk 2
 maxk 3
 maxk 4
 maxk 5
 maxk 6
 maxk 7
 maxk 8
 maxk 9
 maxk 10
 maxk 11
 maxk 12
 sty $0716
 cpx #0
 beq xdone
 stx $0717
xdone
 rts
 ert * > $9800
