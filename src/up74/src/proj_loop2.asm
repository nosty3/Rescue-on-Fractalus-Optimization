; s2-proj: pętla krawędzi terenu (bank 2 $85D4-$87D2). Generuje tools/gen_proj.py - nie edytować ręcznie.
 opt h-
P1R = $8224
P2R = $826c
 org $85d4
 lda $272e
 pha
 lda #$ff
 sta $272e
 ldy #71
 jmp lp
 ert * > $8600
 :($8600-*) dta $ff
lp
 ldx P1R,y
 lda $24b4,x
 and #$a0
 bne next
 ldx P2R,y
 lda $24b4,x
 cmp #$40
 bcs next
 sty $272e
 and #$10
 bne p2ok
 jsr $984f
 ldy $272e
p2ok
 lda P1R,y
 tay
 lda $24b4,y
 and #$10
 beq p1proj
p1ok
 lda $242d,y
 ora $2487,y
 ora $242d,x
 ora $2487,x
 bne cgen
 lda $2400,y
 cmp $2400,x
 bcs nextr
 cmp #$d8
 bcs nextr
 lda $245a,y
 cmp #$6c
 bcc cy1lt
 lda $245a,x
 cmp #$6c
 bcc c974a
 sta $ea
 lda $2400,x
 sta $95
 lda $23b5,x
 sta $f4
 lda $2400,y
 sta $82
 lda $245a,y
 sta $84
 lda $23b5,y
 sta $86
 ldx #0
 jsr $982a
nextr
 ldy $272e
next
 dey
 bpl lp
 jmp fin
p1proj
 tya
 tax
 jsr $984f
 ldy $272e
 ldx P2R,y
 lda P1R,y
 tay
 jmp p1ok
cy1lt
 lda $245a,x
 cmp #$6c
 bcc nextr
 jsr cpy12
 jsr $972e
 jmp nextr
c974a
 jsr cpy12
 jsr $974a
 jmp nextr
cgen
 jsr cpy12
 lda $25d2
 eor #$80
 sta $b5
 lda $83
 eor #$80
 cmp $b5
 bne cg1
 lda $82
 cmp $25b4
cg1
 bcs nextr
 jsr $83bb
 jmp nextr
; p1 (Y) -> $82-$86, $9F = $14, p2 (X) -> $25B4.., X = 0 (wejście ścieżek ogólnych clipu)
cpy12
 lda $2400,y
 sta $82
 lda $242d,y
 sta $83
 lda $245a,y
 sta $84
 lda $2487,y
 sta $85
 lda $23b5,y
 sta $86
 lda #$14
 sta $9f
 lda $2400,x
 sta $25b4
 lda $242d,x
 sta $25d2
 lda $245a,x
 sta $25f0
 lda $2487,x
 sta $24e2
 lda $23b5,x
 sta $23e2
 ldx #0
 rts
; koniec: stan jak pętla Fable ($272E = 2k + 2 ostatniej pary po teście p1, X, Y, $82-$86, kopie p2)
fin
 pla
 sta $28db
 ldy $272e
 cpy #$ff
 bne fb1
 jmp $82b4
fb1
 ldx P2R,y
 lda P1R,y
 tay
 lda $242d,y
 ora $2487,y
 ora $242d,x
 ora $2487,x
 bne fcp
 lda $2400,y
 cmp $2400,x
 bcs frej
 cmp #$d8
 bcs frej
 lda $245a,y
 cmp #$6c
 bcs fy1h
 lda $245a,x
 cmp #$6c
 bcc frej
 bcs fcp
fy1h
 lda $245a,x
 cmp #$6c
 bcc fcp
 lda #0
 sta $83
 sta $85
 beq fcp
frej
 lda $2400,y
 sta $82
 lda $245a,y
 sta $84
 lda $23b5,y
 sta $86
 lda #0
 sta $83
 sta $85
fcp
 jsr copies
 txa
 pha
 ldy $272e
 tya
 pha
 sty $28db
fs
 dey
 bmi fsd
 ldx P1R,y
 lda $24b4,x
 and #$a0
 bne fs
 sty $28db
 beq fs
fsd
 lda $28db
 asl @
 eor #$ff
 sec
 adc #144
 sta $272e
 pla
 asl @
 eor #$ff
 sec
 adc #144
 tay
 pla
 tax
fdone
 lda #43
 sta $28db
 sec
 jmp $88e8
; kopie p2 (X) do $25B4/$25D2/$25F0/$24E2/$23E2 jak oryginał
copies
 lda $2400,x
 sta $25b4
 lda $242d,x
 sta $25d2
 lda $245a,x
 sta $25f0
 lda $2487,x
 sta $24e2
 lda $23b5,x
 sta $23e2
 rts
 ert * > $87d3
 :($87d3-*) dta $ff
