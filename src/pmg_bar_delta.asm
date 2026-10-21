 opt h-
 org $84b0
 tya
 cmp #56
 bcs fallback
 lda $2875
 beq fallback
 cmp #56
 bcs fallback
 txa
 pha
 ldx $2875
 tya
 cmp $2875
 sty $2875
 bcc decrease
 lda #0
increase
 inx
 sta $0c97,x
 cpx $2875
 bne increase
 beq done
decrease
 lda #$ff
fill
 sta $0c97,x
 dex
 cpx $2875
 bne fill
done
 pla
 tax
 ldy #56
 lda #$ff
 sec
 jmp $a57c
fallback
 sty $2875
 jmp $a567
 ert * > $84fd
