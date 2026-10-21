; Reset event flag only after consumption, preserve last-channel value.
 opt h-
 org $bb1c
 jsr $bca4
 cpy #1
 beq done
 lda #0
 sta $0718
done
 rts
