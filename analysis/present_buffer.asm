; Extracted from supplied 64 KiB ROM; addresses are original CPU addresses.
; Reassemble with MADS; output verified byte-for-byte against fixed ROM bank.
 opt h-
 org $B4F4
; VBI: skip presentation when flight mode ($4A) is zero.
 lda $4A                ; $B4F4
 beq $B51A              ; $B4F6
; Read ready buffer flag; zero means renderer has not published.
 lda $42                ; $B4F8
 beq $B51A              ; $B4FA
 cmp #$01               ; $B4FC
 bne $B50C              ; $B4FE
; Ready=1: display list $316B.
 lda #$6B               ; $B500
 sta $D402              ; $B502
 lda #$31               ; $B505
 sta $D403              ; $B507
 bne $B516              ; $B50A
; Ready=2: display list $3210.
 lda #$10               ; $B50C
 sta $D402              ; $B50E
 lda #$32               ; $B511
 sta $D403              ; $B513
; Measurement breakpoint: exactly one hit per buffer presentation.
 lda #$00               ; $B516
; Acknowledge presentation; clear ready flag.
 sta $42                ; $B518
