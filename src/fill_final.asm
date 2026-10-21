; Final bitmap scan: original single-row test first, then four-row OR groups.
; Zero groups skip reads; nonzero groups use the original exact fallback.
 opt h-
 org $9C42
 txa
 tay
 lda #$2A
 sta $9F
 lda #0
 cmp $1010,y
 beq next_0
 lda #$55
 ldx #0
 jmp $95E4
next_0
 lda $1070,y
 ora $10D0,y
 ora $1130,y
 ora $1190,y
 beq empty_1
 lda #0
 jmp $931C
empty_1
 lda $11F0,y
 ora $1250,y
 ora $12B0,y
 ora $1310,y
 beq empty_5
 lda #0
 jmp $934C
empty_5
 lda $1370,y
 ora $13D0,y
 ora $1430,y
 ora $1490,y
 beq empty_9
 lda #0
 jmp $937C
empty_9
 lda $14F0,y
 ora $1550,y
 ora $15B0,y
 ora $1610,y
 beq empty_13
 lda #0
 jmp $93AC
empty_13
 lda $1670,y
 ora $16D0,y
 ora $1730,y
 ora $1790,y
 beq empty_17
 lda #0
 jmp $93DC
empty_17
 lda $17F0,y
 ora $1850,y
 ora $18B0,y
 ora $1910,y
 beq empty_21
 lda #0
 jmp $940C
empty_21
 lda $1970,y
 ora $19D0,y
 ora $1A30,y
 ora $1A90,y
 beq empty_25
 lda #0
 jmp $943C
empty_25
 lda $1AF0,y
 ora $1B50,y
 ora $1BB0,y
 ora $1C10,y
 beq empty_29
 lda #0
 jmp $946C
empty_29
 lda $1C70,y
 ora $1CD0,y
 ora $1D30,y
 ora $1D90,y
 beq empty_33
 lda #0
 jmp $949C
empty_33
 lda $1DF0,y
 ora $1E50,y
 ora $1EB0,y
 ora $1F10,y
 beq empty_37
 lda #0
 jmp $94CC
empty_37
 lda $1F70,y
 ora $1FD0,y
 ora $2030,y
 ora $2090,y
 beq empty_41
 lda #0
 jmp $94FC
empty_41
 lda $20F0,y
 ora $2150,y
 ora $21B0,y
 beq empty_45
 lda #0
 jmp $952C
empty_45
 sec
 jmp $9550

