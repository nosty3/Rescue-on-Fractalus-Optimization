; Quotient-only contract, N < D < 32768, D=0 processor mode.
; AE/AF and B0/B1 are scratch and are not normalized on return.
 opt h-
 org $8224
 txa
 pha
 jmp $8235
