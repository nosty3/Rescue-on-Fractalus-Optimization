; Bank 3 $9F83-$9FE1 (s2-reorder): end of the prolog tables + tail3 + landings.
; $9F83: end of the tables part of prolog3 (was the scalar tail): jmp $9FDD -> bank 2 $9FE2 rts (back to pre).
; $9F86 tail3: entered from pdisp ($984C jmp tail3) on the $87D3 path (after the clear): stx $a7 and the scalar tail
; of the old prolog, byte for byte as before, then jmp $984F -> bank 2 $9854 jmp $85D4 (edge loop).
; $9FDA: landing from bank 2 $9FD5 (lda #3 / sta $D500): jmp $9D80 (hop14, prolog tables without stx $a7).
; $9FDD: lda #2 / sta $D500 -> bank 2 $9FE2 rts.
 opt h-
 org $9f83
 jmp $9fdd
tail3
 stx $a7
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
 ert * > $9fda
 :($9fda-*) dta $ff
 jmp $9d80
 lda #2
 sta $d500
 ert * <> $9fe2
