; Fixed-bank wrapper: preserve the foreground cartridge bank on the VBI stack.
; $9FFF is $FF in bank 2, $05 in bank 5. No new RAM allocation is needed.
; Only the flight VBI at $B46C and its exits $B4EF/$B737 are intercepted.
; The separate title VBI at $B75E/$B7EB is untouched.
 opt h-
 org $bfda
 lda $9fff
 pha
 lda #2
 sta $d500
 lda #0
 sta $c7
 jmp $b470
; $BFEA
 pla
 cmp #5
 beq restore
 lda #2
restore
 sta $d500
 jmp $e462
 ert * > $bffa
