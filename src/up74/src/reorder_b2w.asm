; Bank 2 $9FD5-$9FEE (old wait_beam, now unused): landings for the bank-3 prolog tables called from pre
; (reorder_b2.asm). $9FD5: lda #3 / sta $D500 -> bank 3 $9FDA jmp $9D80; return: bank 3 $9FDD lda #2 / sta $D500
; -> bank 2 $9FE2 rts. Bytes $9FDA-$9FE1 and $9FE3-$9FEE are never executed in bank 2 ($FF).
 opt h-
 org $9fd5
 lda #3
 sta $d500
 :8 dta $ff
 rts
 :12 dta $ff
 ert * <> $9fef
