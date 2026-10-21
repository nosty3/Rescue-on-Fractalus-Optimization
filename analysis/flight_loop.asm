; Extracted from supplied 64 KiB ROM; addresses are original CPU addresses.
; Reassemble with MADS; output verified byte-for-byte against fixed ROM bank.
 opt h-
 org $A32E
; First half: update flight/scene, build image for display list $3210.
 jsr $8309              ; $A32E
 ldx #$33               ; $A331
; Renderer preparation, buffer selector X=$33.
 jsr $9214              ; $A333
 ldx #$30               ; $A336
; Terrain pipeline stage, buffer selector X=$30.
 jsr $87D3              ; $A338
 ldx #$33               ; $A33B
; Raster/output stage, buffer selector X=$33.
 jsr $9308              ; $A33D
 lda $41                ; $A340
 sta $288F              ; $A342
 jsr $8E51              ; $A345
 lda #$02               ; $A348
; Publish ready buffer 2 via zero-page $42.
 sta $42                ; $A34A
 sta $284B              ; $A34C
 jsr $A444              ; $A34F
 lda $062C              ; $A352
 cmp #$0E               ; $A355
 bcs $A36C              ; $A357
 lda $04                ; $A359
 beq $A363              ; $A35B
 jsr $6009              ; $A35D
 jmp $A36C              ; $A360
 lda $3A                ; $A363
 cmp #$01               ; $A365
 bne $A36C              ; $A367
 sta $2849              ; $A369
; Second half: same pipeline for display list $316B.
 jsr $8309              ; $A36C
 ldx #$03               ; $A36F
; Same renderer, selector X=$03.
 jsr $9214              ; $A371
 ldx #$00               ; $A374
; Same terrain stage, selector X=$00.
 jsr $87D3              ; $A376
 ldx #$03               ; $A379
; Same output stage, selector X=$03.
 jsr $9308              ; $A37B
 lda $41                ; $A37E
 beq $A385              ; $A380
 sta $288F              ; $A382
 jsr $8E51              ; $A385
 jsr $A444              ; $A388
 lda $288E              ; $A38B
 beq $A398              ; $A38E
 lda $288D              ; $A390
 beq $A398              ; $A393
 jsr $5D09              ; $A395
 lda $288D              ; $A398
 sta $288E              ; $A39B
 lda $288F              ; $A39E
 bne $A3A8              ; $A3A1
 lda $3E                ; $A3A3
 jmp $A3AA              ; $A3A5
 lda #$00               ; $A3A8
 sta $288D              ; $A3AA
 lda #$01               ; $A3AD
; Publish ready buffer 1 via zero-page $42.
 sta $42                ; $A3AF
 cmp $3E                ; $A3B1
 beq $A3C7              ; $A3B3
 ldx $72                ; $A3B5
 cpx #$02               ; $A3B7
 beq $A3C7              ; $A3B9
 lda $3D                ; $A3BB
 beq $A3C7              ; $A3BD
 lda #$02               ; $A3BF
 sta $3D                ; $A3C1
 ldy #$0E               ; $A3C3
 sty $44                ; $A3C5
 ldx $72                ; $A3C7
 cpx #$02               ; $A3C9
 beq $A3D0              ; $A3CB
; Repeat both halves.
 jmp $A32E              ; $A3CD
