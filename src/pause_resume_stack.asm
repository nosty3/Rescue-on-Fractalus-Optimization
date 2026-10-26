; Resume discards the nested VBI context, bypassing the normal bank restore.
; 2 JSR return bytes + 1 bank marker + 3 saved registers + 3 IRQ bytes = 9.
; The older 8-byte discard leaves a byte that corrupts the RTS return address.
 opt h-
 org $ab1d
 ldy #9
 ert * <> $ab1f
