; Bank 2 free raster space. Exact live RAM/register behavior.
 opt h-
 org $9863
 lda $073d,x
 sta $80
 lda $0793,x
 sta $81
 lda #0
 sta $95
 lda #$55
 sta $96
; First iteration: ($byte & 0) | $55 | table3B[$byte].
 lda ($80),y
 tax
 lda $3b00,x
 ora #$55
 sta ($80),y
 lda $3a00,x
 and #$55
 beq column_end
update_mask
 sta $96
 tax
 lda $3a00,x
 sta $95
 clc
 lda $80
 adc #$60
 sta $80
 bcc loop
 inc $81
; Carry path falls through, replacing the original BCS.
loop
 lda ($80),y
 tax
 and $95
 ora $96
 ora $3b00,x
 sta ($80),y
 lda $3a00,x
 and $96
 bne update_mask
column_end
 iny
 dec $9f
 beq done
 jmp $9c48
done
 rts
 ert * > $98f0
