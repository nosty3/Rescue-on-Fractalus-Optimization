; Flight loop reorder (s2-reorder, idea #8): work that does not touch the frame buffers runs BEFORE the beam wait.
; Bank 2 $87D7-$885D: the dead body of the old $87D3 prolog (unused since proj_loop; $87D3 stays sec / jmp $984F).
;
; $9214 (clear, X = $33/$03) -> jmp pre:
;   1. prolog tables with X = $30/$00: jsr $9FD5 (bank 2 lda #3 / sta $D500 -> bank 3 $9FDA jmp $9D80): bank 3
;      fills occ $263A-$26E1, bank 14 column table $3920-$39D7, $270E-$272D, $B3, $B5; back via bank 3 $9F83
;      jmp $9FDD (lda #2 / sta $D500) -> bank 2 $9FE2 rts.
;   2. the beam wait of wait_beam (same condition: $4A = 0, or $42 = 0, or VCOUNT 74..123), but while not ready
;      it walks the edge-pair list exactly like the edge loop ($85D4) and projects the points that loop would
;      project, in the same order (C = 0 / jsr $984F, bank 3). It stops for good at the first point whose map
;      cell $0A00[$2276,X] is non-zero (that projection would take the rare visibility path, which draws pixels
;      and reads occ: that point and all later ones stay lazy in the edge loop, at their original moment).
;   3. ready: registers and flags restored, jmp $982F (clear, unchanged).
; $87D3 (render, after the clear): bank 3 pdisp now jumps to tail3 ($9F86): stx $a7 + the scalar tail of the old
; prolog ($2907/$2908 from $28/$29 and $6A -> $28FC, which the VBI writes; $28E7.., $2912-$2915 (the VBI reads
; $2912/$2913 at $7C2E in demo mode), $28EA/$79, $28ED, $28FB), then the edge loop, which finds the pre-projected
; points flagged ($10 in $24B4,X) and skips their projection.
 opt h-
 org $87d7
pre
 php
 pha
 txa
 pha
 tya
 pha
 dex
 dex
 dex
 jsr $9fd5
 lda $4a
 beq ready
 ldy #0
wl
 lda $42
 beq ready
 lda $d40b
 cmp #74
 bcc work
 cmp #124
 bcc ready
work
 cpy #$90
 beq wl
 ldx $9b09,y
 iny
 lda $24b4,x
 and #$a0
 bne skp1
 ldx $9b09,y
 iny
 lda $24b4,x
 cmp #$40
 bcs wl
 and #$10
 bne p2ok
 jsr try
p2ok
 ldx $9b07,y
 lda $24b4,x
 and #$10
 bne wl
 jsr try
 jmp wl
skp1
 iny
 bne wl
try
 tya
 pha
 lda $2276,x
 tay
 lda $0a00,y
 bne rare
 clc
 jsr $984f
 pla
 tay
 rts
rare
 pla
 pla
 pla
 ldy #$90
 bne wl
ready
 pla
 tay
 pla
 tax
 pla
 plp
 jmp $982f
 ert * > $885e
