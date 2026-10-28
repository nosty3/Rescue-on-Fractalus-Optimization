; Bank 2, $9885-$988E (dziura FF nosty3 między skokami geometrii): ciągi dalsze wyjść z kodu VBI w banku 14
; (tam `sta $d500` przełącza okno na bank 2, więc następna instrukcja pobiera się stąd).
; $9885 (po bank 14 $9880): dźwięk. Y=0: wszystkie kanały bezczynne -> $B9B0, inaczej Y = pierwszy
;        aktywny kanał -> oryginalna pętla $B92B. A i flagi nadpisywane w obu celach.
; $988E (po bank 14 $9889): koniec wskaźnika $A83E -> rts do wołającego ($B69A).
 opt h-
 org $9885
 tya
 beq idle
 jmp $b92b
idle
 jmp $b9b0
 ert * <> $988e
 rts
