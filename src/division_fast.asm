; Exact fractional divider for the original two callers ($863E/$8719).
; Input: unsigned B1:B0 < AF:AE, nonzero divisor, decimal flag clear.
; Output: B2=floor(256*input/divisor), normalized divisor and remainder as original.
; X preserved, C preserved as in final ROL B2; A/Y/N/Z/V are caller-clobbered.
; Keep the high remainder in A instead of read/modify/write B1 on every bit.
 opt h-
 org $8224
 txa
 pha
 jmp normalize_test
normalize_shift
 asl $B0
 rol $B1
 asl $AE
 rol $AF
normalize_test
 bit $AF
 bvc normalize_shift
 lda $B1
; GENERATED BITS
 asl $B0
 rol @
 cmp $AF
 bcc bit_0_done
 tax
 lda $B0
 sbc $AE
 tay
 txa
 sbc $AF
 bcs bit_0_commit
 txa
 bcc bit_0_done
bit_0_commit
 sty $B0
bit_0_done
 rol $B2
 asl $B0
 rol @
 cmp $AF
 bcc bit_1_done
 tax
 lda $B0
 sbc $AE
 tay
 txa
 sbc $AF
 bcs bit_1_commit
 txa
 bcc bit_1_done
bit_1_commit
 sty $B0
bit_1_done
 rol $B2
 asl $B0
 rol @
 cmp $AF
 bcc bit_2_done
 tax
 lda $B0
 sbc $AE
 tay
 txa
 sbc $AF
 bcs bit_2_commit
 txa
 bcc bit_2_done
bit_2_commit
 sty $B0
bit_2_done
 rol $B2
 asl $B0
 rol @
 cmp $AF
 bcc bit_3_done
 tax
 lda $B0
 sbc $AE
 tay
 txa
 sbc $AF
 bcs bit_3_commit
 txa
 bcc bit_3_done
bit_3_commit
 sty $B0
bit_3_done
 rol $B2
 asl $B0
 rol @
 cmp $AF
 bcc bit_4_done
 tax
 lda $B0
 sbc $AE
 tay
 txa
 sbc $AF
 bcs bit_4_commit
 txa
 bcc bit_4_done
bit_4_commit
 sty $B0
bit_4_done
 rol $B2
 asl $B0
 rol @
 cmp $AF
 bcc bit_5_done
 tax
 lda $B0
 sbc $AE
 tay
 txa
 sbc $AF
 bcs bit_5_commit
 txa
 bcc bit_5_done
bit_5_commit
 sty $B0
bit_5_done
 rol $B2
 asl $B0
 rol @
 cmp $AF
 bcc bit_6_done
 tax
 lda $B0
 sbc $AE
 tay
 txa
 sbc $AF
 bcs bit_6_commit
 txa
 bcc bit_6_done
bit_6_commit
 sty $B0
bit_6_done
 rol $B2
 asl $B0
 rol @
 cmp $AF
 bcc bit_7_done
 tax
 lda $B0
 sbc $AE
 tay
 txa
 sbc $AF
 bcs bit_7_commit
 txa
 bcc bit_7_done
bit_7_commit
 sty $B0
bit_7_done
 rol $B2
 sta $B1
 pla
 tax
 rts
