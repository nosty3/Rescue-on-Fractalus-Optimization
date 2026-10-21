; Standalone audit prototype, NOT patched into distributed game.
 opt h-
 org $bb19
 lda #16
 sta $0716
 lda $0706
 beq next_1
 lda $066c
 and #15
 cmp $0716
 bcs next_1
 sta $0716
 sta $0714
 ldx #1
 stx $0715
next_1
 lda $0707
 beq next_2
 lda $066d
 and #15
 cmp $0716
 bcs next_2
 sta $0716
 sta $0714
 ldx #2
 stx $0715
next_2
 lda $0708
 beq next_3
 lda $066e
 and #15
 cmp $0716
 bcs next_3
 sta $0716
 sta $0714
 ldx #3
 stx $0715
next_3
 lda $0709
 beq next_4
 lda $066f
 and #15
 cmp $0716
 bcs next_4
 sta $0716
 sta $0714
 ldx #4
 stx $0715
next_4
 lda $070a
 beq next_5
 lda $0670
 and #15
 cmp $0716
 bcs next_5
 sta $0716
 sta $0714
 ldx #5
 stx $0715
next_5
 lda $070b
 beq next_6
 lda $0671
 and #15
 cmp $0716
 bcs next_6
 sta $0716
 sta $0714
 ldx #6
 stx $0715
next_6
 lda $070c
 beq next_7
 lda $0672
 and #15
 cmp $0716
 bcs next_7
 sta $0716
 sta $0714
 ldx #7
 stx $0715
next_7
 lda $070d
 beq next_8
 lda $0673
 and #15
 cmp $0716
 bcs next_8
 sta $0716
 sta $0714
 ldx #8
 stx $0715
next_8
 lda $070e
 beq next_9
 lda $0674
 and #15
 cmp $0716
 bcs next_9
 sta $0716
 sta $0714
 ldx #9
 stx $0715
next_9
 lda $070f
 beq next_10
 lda $0675
 and #15
 cmp $0716
 bcs next_10
 sta $0716
 sta $0714
 ldx #10
 stx $0715
next_10
 lda $0710
 beq next_11
 lda $0676
 and #15
 cmp $0716
 bcs next_11
 sta $0716
 sta $0714
 ldx #11
 stx $0715
next_11
 lda $0711
 beq next_12
 lda $0677
 and #15
 cmp $0716
 bcs next_12
 sta $0716
 sta $0714
 ldx #12
 stx $0715
next_12
 ldx #12
 cpx #12
 rts
