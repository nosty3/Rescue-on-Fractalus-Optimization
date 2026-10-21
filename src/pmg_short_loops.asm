 opt h-
 org $83ca
copy21
 iny
 lda $afce,x
 sta $0e87,y
 inx
 iny
 lda $afce,x
 sta $0e87,y
 inx
 iny
 lda $afce,x
 sta $0e87,y
 inx
 dec $bd
 bne copy21
 jmp $a556
clear5
 sta $0f98,y
 iny
 sta $0f98,y
 iny
 sta $0f98,y
 iny
 sta $0f98,y
 iny
 sta $0f98,y
 iny
 ldx #0
 jmp $a8f1
draw5
 lda $a93e,x
 sta $0f98,y
 inx
 iny
 lda $a93e,x
 sta $0f98,y
 inx
 iny
 lda $a93e,x
 sta $0f98,y
 inx
 iny
 lda $a93e,x
 sta $0f98,y
 inx
 iny
 lda $a93e,x
 sta $0f98,y
 inx
 iny
 lda #0
 sta $bb
 jmp $a92a
clear3
 lda $0b91,y
 and #$cf
 sta $0b91,y
 iny
 lda $0b91,y
 and #$cf
 sta $0b91,y
 iny
 lda $0b91,y
 and #$cf
 sta $0b91,y
 iny
 ldx #0
 jmp $a971
draw3
 lda $0b91,y
 ora #$30
 sta $0b91,y
 iny
 lda $0b91,y
 ora #$30
 sta $0b91,y
 iny
 lda $0b91,y
 ora #$30
 sta $0b91,y
 iny
 ldx #0
 jmp $a981
 ert * > $84a0
