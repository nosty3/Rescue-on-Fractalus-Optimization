; Nowa pętla krawędzi terenu (oryginał bank 2 $885E-$88E7) w miejscu starego rzutowania $85D4-$87D2,
; szybki clipping bez kopiowania p2 do $25B4/$25D2/$25F0/$24E2/$23E2 (czyta wprost z tablic po X = p2),
; kopie tylko dla ścieżek ogólnych i na końcu dla ostatniej krawędzi, która przeszła oba testy (stan RAM jak
; w oryginale). Generuje tools/gen_fable.py.
 opt h-
 org $85d4
newloop
 ldy #0
 sty $28db
lp
 ldx $9b09,y
 iny
 lda $24b4,x
 and #$a0
 bne skip1
 ldx $9b09,y
 iny
 sty $272e
 lda $24b4,x
 cmp #$40
 bcs next
 sty $28db
 and #$10
 bne p2ok
 jsr $984f
 ldy $272e
p2ok
 ldx $9b07,y
 lda $24b4,x
 and #$10
 bne p1ok
 clc
 jsr $984f
 ldy $272e
p1ok
 lda $2400,x
 sta $82
 lda $242d,x
 sta $83
 lda $245a,x
 sta $84
 lda $2487,x
 sta $85
 lda $23b5,x
 sta $86
 ldx $9b08,y
 jsr clipfast
 ldy $272e
 cpy #$90
 bne lp
 beq fin
skip1
 iny
next
 cpy #$90
 bne lp
fin
; ostatnia para, która przeszła oba testy -> kopie p2 jak w oryginale ($28DB = indeks za jej p2, 0 = brak);
; potem $28DB = p1 ostatniej pary tablicy (oryginał pisze tam p1 każdej pary, więc na końcu zawsze 43)
 ldy $28db
 beq done
 ldx $9b08,y
 jsr copies
done
 lda #43
 sta $28db
 jmp $88e8
; clipping (oryginał jsr $9627 z X=0), wejście z pętli: X = p2, $82-$86 = p1; hi x1,y1,x2,y2 = 0 -> szybka
; ścieżka bez kopii p2 do $25B4..; inaczej kopie i oryginalny kod
clipfast
 lda $83
 ora $85
 ora $242d,x
 ora $2487,x
 bne cgen
 lda $82
 cmp $2400,x
 bcs crts
 ldy #$14
 sty $9f
 cmp #$d8
 bcs crts
 lda $84
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
 ldx #0
 jmp $982a
cy1lt
 lda $245a,x
 cmp #$6c
 bcc crts
 jsr copies
 ldx #0
 jmp $972e
c974a
 jsr copies
 ldx #0
 jmp $974a
cgen
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
 bcs crts
 ldx #0
 jmp $83bb
crts
 rts
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
