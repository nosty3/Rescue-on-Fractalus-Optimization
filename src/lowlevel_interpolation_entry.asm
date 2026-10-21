; Called from flight logic while bank 2 is selected.
 opt h-
 org $7eeb
 lda #6
 sta $d500
 jsr $8000
 php
 pha
 lda #2
 sta $d500
 pla
 plp
 rts
