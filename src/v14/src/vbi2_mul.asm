; Kod rezydentny (bank 1 -> RAM $6000-$7FFF), $7F4B-$7F9F: dotąd 85 bajtów NOP za `rts` $7F4A (nikt tam
; nie skacze). Mnożenie logiki lotu zamiast pętli shift-add $7CD6 (ok. 130 cykli): dwie tablice w banku 7
; (tools/gen_vbi2_mul.py), ok. 70 cykli z przełączeniem banku. Wołane z $7C9B, $7CBC, $7564 (jsr $7cd6 -> jsr $7f4b).
; Wejście: $6B = M, $28D6 = N. Wyjście jak oryginał: A = f(M, N), $6B = 0. $28D6 oryginał zostawia przesunięte
; o liczbę iteracji - martwe (jedyny odczyt $28D6 w całym kodzie to `asl $28d6` w $7CDE, a każde wywołanie
; najpierw je zapisuje). X, Y, flagi: nie czytane przez wołających (STA/CMP albo LDY #0 od razu po powrocie).
; Bank na wyjściu = 2 (jak w całym VBI; logika lotu $7310 nie przełącza okna).
 opt h-
 org $7f4b
mul2
 lda $28d6
 lsr
 lsr
 lsr
 lsr
 ora #$80
 sta op1+2
 lda $28d6
 and #$0f
 eor #$98
 sta op2+2
 ldx $6b
 lda #7
 sta $d500
op1 lda $8000,x
 clc
op2 adc $9000,x
 ldx #2
 stx $d500
 ldx #0
 stx $6b
 rts
 ert * > $7fa0
