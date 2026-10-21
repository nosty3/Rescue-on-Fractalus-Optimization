; Bank 2 free old-raster area, after the v4 clear bank-switch instruction.
; Invariant: $96 != 0 and $95 = table3A[$96]. table3A[0]=FF, table3B[0]=0.
; Zero data writes $96, keeps both masks and must continue to the next row.
; X is dead until the next nonzero byte loads it, including the terminating row.
 opt h-
 org $9863
 lda ($80),y
 bne nonzero
 lda $96
 sta ($80),y
 jmp $9611
nonzero
 tax
 jmp $95f9
 ert * > $98f0
