; Do not clear the previously displayed buffer until VBI acknowledges.
; Geometry can still run ahead. Preserve the complete caller register state.
 opt h-
 org $84a0
 php
 pha
 lda $4a
 beq ready
wait_present
 lda $42
 bne wait_present
ready
 pla
 plp
 jmp $982f
 ert * > $84fd
