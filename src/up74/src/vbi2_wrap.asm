; Kod rezydentny $7EEB-$7EFC (18 bajtów): opakowanie wywołania interpolacji terenu w banku 14.
; Oryginał: lda #14 / sta $d500 / jsr $9000 / php / pha / lda #2 / sta $d500 / pla / plp / rts.
; Wołający ($7D56, $7E47, $7EA9, $7AC9) zaraz po powrocie robią `lda $62` / `lsr $62` / `lda $62; cmp`,
; więc A i flagi są martwe: bez php/pha/pla/plp (14 cykli). Cel: spec9000 (vbi2_interp14.asm).
 opt h-
 org $7eeb
 lda #14
 sta $d500
 jsr $9490
 lda #2
 sta $d500
 rts
 ert * > $7efd
