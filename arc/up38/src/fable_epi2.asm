; Pętla $89A1 ($28B6,Y = ($271E - $270E,Y) / 2 z zaokrągleniem, Y = 31..0) rozwinięta 4x; $89A1: jmp $8861.
; Generuje tools/gen_fable.py. X wolny (po pętli nikt go nie czyta przed zapisem).
 opt h-
 org $8861
 ldx $271e
 ldy #$1f
elp
 sec
 txa
 sbc $270e,y
 cmp #$80
 ror @
 adc #0
 sta $28b6,y
 dey
 sec
 txa
 sbc $270e,y
 cmp #$80
 ror @
 adc #0
 sta $28b6,y
 dey
 sec
 txa
 sbc $270e,y
 cmp #$80
 ror @
 adc #0
 sta $28b6,y
 dey
 sec
 txa
 sbc $270e,y
 cmp #$80
 ror @
 adc #0
 sta $28b6,y
 dey
 bpl elp
 jmp $89b5
 ert * > $88e8
