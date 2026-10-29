; Batch exact classifiers 33..43, then generate/classify point 44 inline.
; CMP preserves the exact height borrow; SBC $8C later replaces V.
; v7 candidate: full tail specialization, exact arithmetic, 9F saved/restored.
 opt h-
 org $8000
entry
 lda $9f
 pha
 sec
 lda #0
 sbc $8b
 lsr @
 lsr @
 lsr @
 sta $9f
 ldy #0
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_0
 INX
 CLC
 LDA $22a3
 ADC $a2
 STA $22a4
 LDA $22d1
 ADC $a3
 STA $22d2
 CLC
 LDA $22ff
 ADC $a0
 STA $2300
 LDA $232d
 ADC $a1
 STA $232e

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2276
 lda $0900,x
 sta $23b5
 sbc $8c
 tax
 bcs positive_0
 lda high_table,x
 ora #$f0
 bne high_done_0
positive_0
 lda high_table,x
high_done_0
 sta $2388
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $235b
 ldx $2276
p0_84a7
 LDA $232e
p0_84aa
 BMI p0_84f0
p0_84ac
 BNE p0_84b5
p0_84ae
 LDA $2300
p0_84b1
 CMP #$20
p0_84b3
 BCC p0_84f0
p0_84b5
 LDA $22d2
p0_84b8
 BPL p0_84d9
p0_84ba
 SEC
p0_84bb
 LDA #$00
p0_84bd
 SBC $22a4
p0_84c0
 STA $b5
p0_84c2
 LDA #$00
p0_84c4
 SBC $22d2
p0_84c7
 CMP $232e
p0_84ca
 BCC p0_84ec
p0_84cc
 BNE p0_84d5
p0_84ce
 LDA $b5
p0_84d0
 CMP $2300
p0_84d3
 BCC p0_84ec
p0_84d5
 LDA #$40
p0_84d7
 BNE p0_84f2
p0_84d9
 CMP $232e
p0_84dc
 BCC p0_84ec
p0_84de
 BNE p0_84e8
p0_84e0
 LDA $22a4
p0_84e3
 CMP $2300
p0_84e6
 BCC p0_84ec
p0_84e8
 LDA #$20
p0_84ea
 BNE p0_84f2
p0_84ec
 LDA #$00
p0_84ee
 BEQ p0_84f2
p0_84f0
 LDA #$80
p0_84f2
 STA $24b4
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_1
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22a4
 SBC $a0
 STA $22a5
 LDA $22d2
 SBC $a1
 STA $22d3
 CLC
 LDA $2300
 ADC $a2
 STA $2301
 LDA $232e
 ADC $a3
 STA $232f
 INX
 CLC
 LDA $22a5
 ADC $a2
 STA $22a5
 LDA $22d3
 ADC $a3
 STA $22d3
 CLC
 LDA $2301
 ADC $a0
 STA $2301
 LDA $232f
 ADC $a1
 STA $232f

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2277
 lda $0900,x
 sta $23b6
 sbc $8c
 tax
 bcs positive_1
 lda high_table,x
 ora #$f0
 bne high_done_1
positive_1
 lda high_table,x
high_done_1
 sta $2389
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $235c
 ldx $2277
p1_84a7
 LDA $232f
p1_84aa
 BMI p1_84f0
p1_84ac
 BNE p1_84b5
p1_84ae
 LDA $2301
p1_84b1
 CMP #$20
p1_84b3
 BCC p1_84f0
p1_84b5
 LDA $22d3
p1_84b8
 BPL p1_84d9
p1_84ba
 SEC
p1_84bb
 LDA #$00
p1_84bd
 SBC $22a5
p1_84c0
 STA $b5
p1_84c2
 LDA #$00
p1_84c4
 SBC $22d3
p1_84c7
 CMP $232f
p1_84ca
 BCC p1_84ec
p1_84cc
 BNE p1_84d5
p1_84ce
 LDA $b5
p1_84d0
 CMP $2301
p1_84d3
 BCC p1_84ec
p1_84d5
 LDA #$40
p1_84d7
 BNE p1_84f2
p1_84d9
 CMP $232f
p1_84dc
 BCC p1_84ec
p1_84de
 BNE p1_84e8
p1_84e0
 LDA $22a5
p1_84e3
 CMP $2301
p1_84e6
 BCC p1_84ec
p1_84e8
 LDA #$20
p1_84ea
 BNE p1_84f2
p1_84ec
 LDA #$00
p1_84ee
 BEQ p1_84f2
p1_84f0
 LDA #$80
p1_84f2
 STA $24b5
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_2
 DEX
 SEC
 LDA $22a5
 SBC $a2
 STA $22a6
 LDA $22d3
 SBC $a3
 STA $22d4
 SEC
 LDA $2301
 SBC $a0
 STA $2302
 LDA $232f
 SBC $a1
 STA $2330

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2278
 lda $0900,x
 sta $23b7
 sbc $8c
 tax
 bcs positive_2
 lda high_table,x
 ora #$f0
 bne high_done_2
positive_2
 lda high_table,x
high_done_2
 sta $238a
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $235d
 ldx $2278
p2_84a7
 LDA $2330
p2_84aa
 BMI p2_84f0
p2_84ac
 BNE p2_84b5
p2_84ae
 LDA $2302
p2_84b1
 CMP #$20
p2_84b3
 BCC p2_84f0
p2_84b5
 LDA $22d4
p2_84b8
 BPL p2_84d9
p2_84ba
 SEC
p2_84bb
 LDA #$00
p2_84bd
 SBC $22a6
p2_84c0
 STA $b5
p2_84c2
 LDA #$00
p2_84c4
 SBC $22d4
p2_84c7
 CMP $2330
p2_84ca
 BCC p2_84ec
p2_84cc
 BNE p2_84d5
p2_84ce
 LDA $b5
p2_84d0
 CMP $2302
p2_84d3
 BCC p2_84ec
p2_84d5
 LDA #$40
p2_84d7
 BNE p2_84f2
p2_84d9
 CMP $2330
p2_84dc
 BCC p2_84ec
p2_84de
 BNE p2_84e8
p2_84e0
 LDA $22a6
p2_84e3
 CMP $2302
p2_84e6
 BCC p2_84ec
p2_84e8
 LDA #$20
p2_84ea
 BNE p2_84f2
p2_84ec
 LDA #$00
p2_84ee
 BEQ p2_84f2
p2_84f0
 LDA #$80
p2_84f2
 STA $24b6
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_3
 DEX
 SEC
 LDA $22a6
 SBC $a2
 STA $22a7
 LDA $22d4
 SBC $a3
 STA $22d5
 SEC
 LDA $2302
 SBC $a0
 STA $2303
 LDA $2330
 SBC $a1
 STA $2331

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2279
 lda $0900,x
 sta $23b8
 sbc $8c
 tax
 bcs positive_3
 lda high_table,x
 ora #$f0
 bne high_done_3
positive_3
 lda high_table,x
high_done_3
 sta $238b
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $235e
 ldx $2279
p3_84a7
 LDA $2331
p3_84aa
 BMI p3_84f0
p3_84ac
 BNE p3_84b5
p3_84ae
 LDA $2303
p3_84b1
 CMP #$20
p3_84b3
 BCC p3_84f0
p3_84b5
 LDA $22d5
p3_84b8
 BPL p3_84d9
p3_84ba
 SEC
p3_84bb
 LDA #$00
p3_84bd
 SBC $22a7
p3_84c0
 STA $b5
p3_84c2
 LDA #$00
p3_84c4
 SBC $22d5
p3_84c7
 CMP $2331
p3_84ca
 BCC p3_84ec
p3_84cc
 BNE p3_84d5
p3_84ce
 LDA $b5
p3_84d0
 CMP $2303
p3_84d3
 BCC p3_84ec
p3_84d5
 LDA #$40
p3_84d7
 BNE p3_84f2
p3_84d9
 CMP $2331
p3_84dc
 BCC p3_84ec
p3_84de
 BNE p3_84e8
p3_84e0
 LDA $22a7
p3_84e3
 CMP $2303
p3_84e6
 BCC p3_84ec
p3_84e8
 LDA #$20
p3_84ea
 BNE p3_84f2
p3_84ec
 LDA #$00
p3_84ee
 BEQ p3_84f2
p3_84f0
 LDA #$80
p3_84f2
 STA $24b7
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_4
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22a7
 ADC $a0
 STA $22a8
 LDA $22d5
 ADC $a1
 STA $22d6
 SEC
 LDA $2303
 SBC $a2
 STA $2304
 LDA $2331
 SBC $a3
 STA $2332

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $227a
 lda $0900,x
 sta $23b9
 sbc $8c
 tax
 bcs positive_4
 lda high_table,x
 ora #$f0
 bne high_done_4
positive_4
 lda high_table,x
high_done_4
 sta $238c
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $235f
 ldx $227a
p4_84a7
 LDA $2332
p4_84aa
 BMI p4_84f0
p4_84ac
 BNE p4_84b5
p4_84ae
 LDA $2304
p4_84b1
 CMP #$20
p4_84b3
 BCC p4_84f0
p4_84b5
 LDA $22d6
p4_84b8
 BPL p4_84d9
p4_84ba
 SEC
p4_84bb
 LDA #$00
p4_84bd
 SBC $22a8
p4_84c0
 STA $b5
p4_84c2
 LDA #$00
p4_84c4
 SBC $22d6
p4_84c7
 CMP $2332
p4_84ca
 BCC p4_84ec
p4_84cc
 BNE p4_84d5
p4_84ce
 LDA $b5
p4_84d0
 CMP $2304
p4_84d3
 BCC p4_84ec
p4_84d5
 LDA #$40
p4_84d7
 BNE p4_84f2
p4_84d9
 CMP $2332
p4_84dc
 BCC p4_84ec
p4_84de
 BNE p4_84e8
p4_84e0
 LDA $22a8
p4_84e3
 CMP $2304
p4_84e6
 BCC p4_84ec
p4_84e8
 LDA #$20
p4_84ea
 BNE p4_84f2
p4_84ec
 LDA #$00
p4_84ee
 BEQ p4_84f2
p4_84f0
 LDA #$80
p4_84f2
 STA $24b8
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_5
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22a8
 ADC $a0
 STA $22a9
 LDA $22d6
 ADC $a1
 STA $22d7
 SEC
 LDA $2304
 SBC $a2
 STA $2305
 LDA $2332
 SBC $a3
 STA $2333

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $227b
 lda $0900,x
 sta $23ba
 sbc $8c
 tax
 bcs positive_5
 lda high_table,x
 ora #$f0
 bne high_done_5
positive_5
 lda high_table,x
high_done_5
 sta $238d
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2360
 ldx $227b
p5_84a7
 LDA $2333
p5_84aa
 BMI p5_84f0
p5_84ac
 BNE p5_84b5
p5_84ae
 LDA $2305
p5_84b1
 CMP #$20
p5_84b3
 BCC p5_84f0
p5_84b5
 LDA $22d7
p5_84b8
 BPL p5_84d9
p5_84ba
 SEC
p5_84bb
 LDA #$00
p5_84bd
 SBC $22a9
p5_84c0
 STA $b5
p5_84c2
 LDA #$00
p5_84c4
 SBC $22d7
p5_84c7
 CMP $2333
p5_84ca
 BCC p5_84ec
p5_84cc
 BNE p5_84d5
p5_84ce
 LDA $b5
p5_84d0
 CMP $2305
p5_84d3
 BCC p5_84ec
p5_84d5
 LDA #$40
p5_84d7
 BNE p5_84f2
p5_84d9
 CMP $2333
p5_84dc
 BCC p5_84ec
p5_84de
 BNE p5_84e8
p5_84e0
 LDA $22a9
p5_84e3
 CMP $2305
p5_84e6
 BCC p5_84ec
p5_84e8
 LDA #$20
p5_84ea
 BNE p5_84f2
p5_84ec
 LDA #$00
p5_84ee
 BEQ p5_84f2
p5_84f0
 LDA #$80
p5_84f2
 STA $24b9
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_6
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22a9
 ADC $a0
 STA $22aa
 LDA $22d7
 ADC $a1
 STA $22d8
 SEC
 LDA $2305
 SBC $a2
 STA $2306
 LDA $2333
 SBC $a3
 STA $2334
 DEX
 SEC
 LDA $22aa
 SBC $a2
 STA $22aa
 LDA $22d8
 SBC $a3
 STA $22d8
 SEC
 LDA $2306
 SBC $a0
 STA $2306
 LDA $2334
 SBC $a1
 STA $2334

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $227c
 lda $0900,x
 sta $23bb
 sbc $8c
 tax
 bcs positive_6
 lda high_table,x
 ora #$f0
 bne high_done_6
positive_6
 lda high_table,x
high_done_6
 sta $238e
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2361
 ldx $227c
p6_84a7
 LDA $2334
p6_84aa
 BMI p6_84f0
p6_84ac
 BNE p6_84b5
p6_84ae
 LDA $2306
p6_84b1
 CMP #$20
p6_84b3
 BCC p6_84f0
p6_84b5
 LDA $22d8
p6_84b8
 BPL p6_84d9
p6_84ba
 SEC
p6_84bb
 LDA #$00
p6_84bd
 SBC $22aa
p6_84c0
 STA $b5
p6_84c2
 LDA #$00
p6_84c4
 SBC $22d8
p6_84c7
 CMP $2334
p6_84ca
 BCC p6_84ec
p6_84cc
 BNE p6_84d5
p6_84ce
 LDA $b5
p6_84d0
 CMP $2306
p6_84d3
 BCC p6_84ec
p6_84d5
 LDA #$40
p6_84d7
 BNE p6_84f2
p6_84d9
 CMP $2334
p6_84dc
 BCC p6_84ec
p6_84de
 BNE p6_84e8
p6_84e0
 LDA $22aa
p6_84e3
 CMP $2306
p6_84e6
 BCC p6_84ec
p6_84e8
 LDA #$20
p6_84ea
 BNE p6_84f2
p6_84ec
 LDA #$00
p6_84ee
 BEQ p6_84f2
p6_84f0
 LDA #$80
p6_84f2
 STA $24ba
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_7
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22aa
 SBC $a0
 STA $22ab
 LDA $22d8
 SBC $a1
 STA $22d9
 CLC
 LDA $2306
 ADC $a2
 STA $2307
 LDA $2334
 ADC $a3
 STA $2335

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $227d
 lda $0900,x
 sta $23bc
 sbc $8c
 tax
 bcs positive_7
 lda high_table,x
 ora #$f0
 bne high_done_7
positive_7
 lda high_table,x
high_done_7
 sta $238f
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2362
 ldx $227d
p7_84a7
 LDA $2335
p7_84aa
 BMI p7_84f0
p7_84ac
 BNE p7_84b5
p7_84ae
 LDA $2307
p7_84b1
 CMP #$20
p7_84b3
 BCC p7_84f0
p7_84b5
 LDA $22d9
p7_84b8
 BPL p7_84d9
p7_84ba
 SEC
p7_84bb
 LDA #$00
p7_84bd
 SBC $22ab
p7_84c0
 STA $b5
p7_84c2
 LDA #$00
p7_84c4
 SBC $22d9
p7_84c7
 CMP $2335
p7_84ca
 BCC p7_84ec
p7_84cc
 BNE p7_84d5
p7_84ce
 LDA $b5
p7_84d0
 CMP $2307
p7_84d3
 BCC p7_84ec
p7_84d5
 LDA #$40
p7_84d7
 BNE p7_84f2
p7_84d9
 CMP $2335
p7_84dc
 BCC p7_84ec
p7_84de
 BNE p7_84e8
p7_84e0
 LDA $22ab
p7_84e3
 CMP $2307
p7_84e6
 BCC p7_84ec
p7_84e8
 LDA #$20
p7_84ea
 BNE p7_84f2
p7_84ec
 LDA #$00
p7_84ee
 BEQ p7_84f2
p7_84f0
 LDA #$80
p7_84f2
 STA $24bb
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_8
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22ab
 SBC $a0
 STA $22ac
 LDA $22d9
 SBC $a1
 STA $22da
 CLC
 LDA $2307
 ADC $a2
 STA $2308
 LDA $2335
 ADC $a3
 STA $2336

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $227e
 lda $0900,x
 sta $23bd
 sbc $8c
 tax
 bcs positive_8
 lda high_table,x
 ora #$f0
 bne high_done_8
positive_8
 lda high_table,x
high_done_8
 sta $2390
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2363
 ldx $227e
p8_84a7
 LDA $2336
p8_84aa
 BMI p8_84f0
p8_84ac
 BNE p8_84b5
p8_84ae
 LDA $2308
p8_84b1
 CMP #$20
p8_84b3
 BCC p8_84f0
p8_84b5
 LDA $22da
p8_84b8
 BPL p8_84d9
p8_84ba
 SEC
p8_84bb
 LDA #$00
p8_84bd
 SBC $22ac
p8_84c0
 STA $b5
p8_84c2
 LDA #$00
p8_84c4
 SBC $22da
p8_84c7
 CMP $2336
p8_84ca
 BCC p8_84ec
p8_84cc
 BNE p8_84d5
p8_84ce
 LDA $b5
p8_84d0
 CMP $2308
p8_84d3
 BCC p8_84ec
p8_84d5
 LDA #$40
p8_84d7
 BNE p8_84f2
p8_84d9
 CMP $2336
p8_84dc
 BCC p8_84ec
p8_84de
 BNE p8_84e8
p8_84e0
 LDA $22ac
p8_84e3
 CMP $2308
p8_84e6
 BCC p8_84ec
p8_84e8
 LDA #$20
p8_84ea
 BNE p8_84f2
p8_84ec
 LDA #$00
p8_84ee
 BEQ p8_84f2
p8_84f0
 LDA #$80
p8_84f2
 STA $24bc
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_9
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22ac
 SBC $a0
 STA $22ad
 LDA $22da
 SBC $a1
 STA $22db
 CLC
 LDA $2308
 ADC $a2
 STA $2309
 LDA $2336
 ADC $a3
 STA $2337

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $227f
 lda $0900,x
 sta $23be
 sbc $8c
 tax
 bcs positive_9
 lda high_table,x
 ora #$f0
 bne high_done_9
positive_9
 lda high_table,x
high_done_9
 sta $2391
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2364
 ldx $227f
p9_84a7
 LDA $2337
p9_84aa
 BMI p9_84f0
p9_84ac
 BNE p9_84b5
p9_84ae
 LDA $2309
p9_84b1
 CMP #$20
p9_84b3
 BCC p9_84f0
p9_84b5
 LDA $22db
p9_84b8
 BPL p9_84d9
p9_84ba
 SEC
p9_84bb
 LDA #$00
p9_84bd
 SBC $22ad
p9_84c0
 STA $b5
p9_84c2
 LDA #$00
p9_84c4
 SBC $22db
p9_84c7
 CMP $2337
p9_84ca
 BCC p9_84ec
p9_84cc
 BNE p9_84d5
p9_84ce
 LDA $b5
p9_84d0
 CMP $2309
p9_84d3
 BCC p9_84ec
p9_84d5
 LDA #$40
p9_84d7
 BNE p9_84f2
p9_84d9
 CMP $2337
p9_84dc
 BCC p9_84ec
p9_84de
 BNE p9_84e8
p9_84e0
 LDA $22ad
p9_84e3
 CMP $2309
p9_84e6
 BCC p9_84ec
p9_84e8
 LDA #$20
p9_84ea
 BNE p9_84f2
p9_84ec
 LDA #$00
p9_84ee
 BEQ p9_84f2
p9_84f0
 LDA #$80
p9_84f2
 STA $24bd
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_10
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22ad
 SBC $a0
 STA $22ae
 LDA $22db
 SBC $a1
 STA $22dc
 CLC
 LDA $2309
 ADC $a2
 STA $230a
 LDA $2337
 ADC $a3
 STA $2338

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2280
 lda $0900,x
 sta $23bf
 sbc $8c
 tax
 bcs positive_10
 lda high_table,x
 ora #$f0
 bne high_done_10
positive_10
 lda high_table,x
high_done_10
 sta $2392
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2365
 ldx $2280
p10_84a7
 LDA $2338
p10_84aa
 BMI p10_84f0
p10_84ac
 BNE p10_84b5
p10_84ae
 LDA $230a
p10_84b1
 CMP #$20
p10_84b3
 BCC p10_84f0
p10_84b5
 LDA $22dc
p10_84b8
 BPL p10_84d9
p10_84ba
 SEC
p10_84bb
 LDA #$00
p10_84bd
 SBC $22ae
p10_84c0
 STA $b5
p10_84c2
 LDA #$00
p10_84c4
 SBC $22dc
p10_84c7
 CMP $2338
p10_84ca
 BCC p10_84ec
p10_84cc
 BNE p10_84d5
p10_84ce
 LDA $b5
p10_84d0
 CMP $230a
p10_84d3
 BCC p10_84ec
p10_84d5
 LDA #$40
p10_84d7
 BNE p10_84f2
p10_84d9
 CMP $2338
p10_84dc
 BCC p10_84ec
p10_84de
 BNE p10_84e8
p10_84e0
 LDA $22ae
p10_84e3
 CMP $230a
p10_84e6
 BCC p10_84ec
p10_84e8
 LDA #$20
p10_84ea
 BNE p10_84f2
p10_84ec
 LDA #$00
p10_84ee
 BEQ p10_84f2
p10_84f0
 LDA #$80
p10_84f2
 STA $24be
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_11
 INX
 CLC
 LDA $22ae
 ADC $a2
 STA $22af
 LDA $22dc
 ADC $a3
 STA $22dd
 CLC
 LDA $230a
 ADC $a0
 STA $230b
 LDA $2338
 ADC $a1
 STA $2339

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2281
 lda $0900,x
 sta $23c0
 sbc $8c
 tax
 bcs positive_11
 lda high_table,x
 ora #$f0
 bne high_done_11
positive_11
 lda high_table,x
high_done_11
 sta $2393
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2366
 ldx $2281
p11_84a7
 LDA $2339
p11_84aa
 BMI p11_84f0
p11_84ac
 BNE p11_84b5
p11_84ae
 LDA $230b
p11_84b1
 CMP #$20
p11_84b3
 BCC p11_84f0
p11_84b5
 LDA $22dd
p11_84b8
 BPL p11_84d9
p11_84ba
 SEC
p11_84bb
 LDA #$00
p11_84bd
 SBC $22af
p11_84c0
 STA $b5
p11_84c2
 LDA #$00
p11_84c4
 SBC $22dd
p11_84c7
 CMP $2339
p11_84ca
 BCC p11_84ec
p11_84cc
 BNE p11_84d5
p11_84ce
 LDA $b5
p11_84d0
 CMP $230b
p11_84d3
 BCC p11_84ec
p11_84d5
 LDA #$40
p11_84d7
 BNE p11_84f2
p11_84d9
 CMP $2339
p11_84dc
 BCC p11_84ec
p11_84de
 BNE p11_84e8
p11_84e0
 LDA $22af
p11_84e3
 CMP $230b
p11_84e6
 BCC p11_84ec
p11_84e8
 LDA #$20
p11_84ea
 BNE p11_84f2
p11_84ec
 LDA #$00
p11_84ee
 BEQ p11_84f2
p11_84f0
 LDA #$80
p11_84f2
 STA $24bf
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_12
 INX
 CLC
 LDA $22af
 ADC $a2
 STA $22b0
 LDA $22dd
 ADC $a3
 STA $22de
 CLC
 LDA $230b
 ADC $a0
 STA $230c
 LDA $2339
 ADC $a1
 STA $233a

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2282
 lda $0900,x
 sta $23c1
 sbc $8c
 tax
 bcs positive_12
 lda high_table,x
 ora #$f0
 bne high_done_12
positive_12
 lda high_table,x
high_done_12
 sta $2394
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2367
 ldx $2282
p12_84a7
 LDA $233a
p12_84aa
 BMI p12_84f0
p12_84ac
 BNE p12_84b5
p12_84ae
 LDA $230c
p12_84b1
 CMP #$20
p12_84b3
 BCC p12_84f0
p12_84b5
 LDA $22de
p12_84b8
 BPL p12_84d9
p12_84ba
 SEC
p12_84bb
 LDA #$00
p12_84bd
 SBC $22b0
p12_84c0
 STA $b5
p12_84c2
 LDA #$00
p12_84c4
 SBC $22de
p12_84c7
 CMP $233a
p12_84ca
 BCC p12_84ec
p12_84cc
 BNE p12_84d5
p12_84ce
 LDA $b5
p12_84d0
 CMP $230c
p12_84d3
 BCC p12_84ec
p12_84d5
 LDA #$40
p12_84d7
 BNE p12_84f2
p12_84d9
 CMP $233a
p12_84dc
 BCC p12_84ec
p12_84de
 BNE p12_84e8
p12_84e0
 LDA $22b0
p12_84e3
 CMP $230c
p12_84e6
 BCC p12_84ec
p12_84e8
 LDA #$20
p12_84ea
 BNE p12_84f2
p12_84ec
 LDA #$00
p12_84ee
 BEQ p12_84f2
p12_84f0
 LDA #$80
p12_84f2
 STA $24c0
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_13
 INX
 CLC
 LDA $22b0
 ADC $a2
 STA $22b1
 LDA $22de
 ADC $a3
 STA $22df
 CLC
 LDA $230c
 ADC $a0
 STA $230d
 LDA $233a
 ADC $a1
 STA $233b

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2283
 lda $0900,x
 sta $23c2
 sbc $8c
 tax
 bcs positive_13
 lda high_table,x
 ora #$f0
 bne high_done_13
positive_13
 lda high_table,x
high_done_13
 sta $2395
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2368
 ldx $2283
p13_84a7
 LDA $233b
p13_84aa
 BMI p13_84f0
p13_84ac
 BNE p13_84b5
p13_84ae
 LDA $230d
p13_84b1
 CMP #$20
p13_84b3
 BCC p13_84f0
p13_84b5
 LDA $22df
p13_84b8
 BPL p13_84d9
p13_84ba
 SEC
p13_84bb
 LDA #$00
p13_84bd
 SBC $22b1
p13_84c0
 STA $b5
p13_84c2
 LDA #$00
p13_84c4
 SBC $22df
p13_84c7
 CMP $233b
p13_84ca
 BCC p13_84ec
p13_84cc
 BNE p13_84d5
p13_84ce
 LDA $b5
p13_84d0
 CMP $230d
p13_84d3
 BCC p13_84ec
p13_84d5
 LDA #$40
p13_84d7
 BNE p13_84f2
p13_84d9
 CMP $233b
p13_84dc
 BCC p13_84ec
p13_84de
 BNE p13_84e8
p13_84e0
 LDA $22b1
p13_84e3
 CMP $230d
p13_84e6
 BCC p13_84ec
p13_84e8
 LDA #$20
p13_84ea
 BNE p13_84f2
p13_84ec
 LDA #$00
p13_84ee
 BEQ p13_84f2
p13_84f0
 LDA #$80
p13_84f2
 STA $24c1
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_14
 INX
 CLC
 LDA $22b1
 ADC $a2
 STA $22b2
 LDA $22df
 ADC $a3
 STA $22e0
 CLC
 LDA $230d
 ADC $a0
 STA $230e
 LDA $233b
 ADC $a1
 STA $233c

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2284
 lda $0900,x
 sta $23c3
 sbc $8c
 tax
 bcs positive_14
 lda high_table,x
 ora #$f0
 bne high_done_14
positive_14
 lda high_table,x
high_done_14
 sta $2396
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2369
 ldx $2284
p14_84a7
 LDA $233c
p14_84aa
 BMI p14_84f0
p14_84ac
 BNE p14_84b5
p14_84ae
 LDA $230e
p14_84b1
 CMP #$20
p14_84b3
 BCC p14_84f0
p14_84b5
 LDA $22e0
p14_84b8
 BPL p14_84d9
p14_84ba
 SEC
p14_84bb
 LDA #$00
p14_84bd
 SBC $22b2
p14_84c0
 STA $b5
p14_84c2
 LDA #$00
p14_84c4
 SBC $22e0
p14_84c7
 CMP $233c
p14_84ca
 BCC p14_84ec
p14_84cc
 BNE p14_84d5
p14_84ce
 LDA $b5
p14_84d0
 CMP $230e
p14_84d3
 BCC p14_84ec
p14_84d5
 LDA #$40
p14_84d7
 BNE p14_84f2
p14_84d9
 CMP $233c
p14_84dc
 BCC p14_84ec
p14_84de
 BNE p14_84e8
p14_84e0
 LDA $22b2
p14_84e3
 CMP $230e
p14_84e6
 BCC p14_84ec
p14_84e8
 LDA #$20
p14_84ea
 BNE p14_84f2
p14_84ec
 LDA #$00
p14_84ee
 BEQ p14_84f2
p14_84f0
 LDA #$80
p14_84f2
 STA $24c2
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_15
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22b2
 SBC $a0
 STA $22b3
 LDA $22e0
 SBC $a1
 STA $22e1
 CLC
 LDA $230e
 ADC $a2
 STA $230f
 LDA $233c
 ADC $a3
 STA $233d
 INX
 CLC
 LDA $22b3
 ADC $a2
 STA $22b3
 LDA $22e1
 ADC $a3
 STA $22e1
 CLC
 LDA $230f
 ADC $a0
 STA $230f
 LDA $233d
 ADC $a1
 STA $233d

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2285
 lda $0900,x
 sta $23c4
 sbc $8c
 tax
 bcs positive_15
 lda high_table,x
 ora #$f0
 bne high_done_15
positive_15
 lda high_table,x
high_done_15
 sta $2397
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $236a
 ldx $2285
p15_84a7
 LDA $233d
p15_84aa
 BMI p15_84f0
p15_84ac
 BNE p15_84b5
p15_84ae
 LDA $230f
p15_84b1
 CMP #$20
p15_84b3
 BCC p15_84f0
p15_84b5
 LDA $22e1
p15_84b8
 BPL p15_84d9
p15_84ba
 SEC
p15_84bb
 LDA #$00
p15_84bd
 SBC $22b3
p15_84c0
 STA $b5
p15_84c2
 LDA #$00
p15_84c4
 SBC $22e1
p15_84c7
 CMP $233d
p15_84ca
 BCC p15_84ec
p15_84cc
 BNE p15_84d5
p15_84ce
 LDA $b5
p15_84d0
 CMP $230f
p15_84d3
 BCC p15_84ec
p15_84d5
 LDA #$40
p15_84d7
 BNE p15_84f2
p15_84d9
 CMP $233d
p15_84dc
 BCC p15_84ec
p15_84de
 BNE p15_84e8
p15_84e0
 LDA $22b3
p15_84e3
 CMP $230f
p15_84e6
 BCC p15_84ec
p15_84e8
 LDA #$20
p15_84ea
 BNE p15_84f2
p15_84ec
 LDA #$00
p15_84ee
 BEQ p15_84f2
p15_84f0
 LDA #$80
p15_84f2
 STA $24c3
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_16
 DEX
 SEC
 LDA $22b3
 SBC $a2
 STA $22b4
 LDA $22e1
 SBC $a3
 STA $22e2
 SEC
 LDA $230f
 SBC $a0
 STA $2310
 LDA $233d
 SBC $a1
 STA $233e

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2286
 lda $0900,x
 sta $23c5
 sbc $8c
 tax
 bcs positive_16
 lda high_table,x
 ora #$f0
 bne high_done_16
positive_16
 lda high_table,x
high_done_16
 sta $2398
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $236b
 ldx $2286
p16_84a7
 LDA $233e
p16_84aa
 BMI p16_84f0
p16_84ac
 BNE p16_84b5
p16_84ae
 LDA $2310
p16_84b1
 CMP #$20
p16_84b3
 BCC p16_84f0
p16_84b5
 LDA $22e2
p16_84b8
 BPL p16_84d9
p16_84ba
 SEC
p16_84bb
 LDA #$00
p16_84bd
 SBC $22b4
p16_84c0
 STA $b5
p16_84c2
 LDA #$00
p16_84c4
 SBC $22e2
p16_84c7
 CMP $233e
p16_84ca
 BCC p16_84ec
p16_84cc
 BNE p16_84d5
p16_84ce
 LDA $b5
p16_84d0
 CMP $2310
p16_84d3
 BCC p16_84ec
p16_84d5
 LDA #$40
p16_84d7
 BNE p16_84f2
p16_84d9
 CMP $233e
p16_84dc
 BCC p16_84ec
p16_84de
 BNE p16_84e8
p16_84e0
 LDA $22b4
p16_84e3
 CMP $2310
p16_84e6
 BCC p16_84ec
p16_84e8
 LDA #$20
p16_84ea
 BNE p16_84f2
p16_84ec
 LDA #$00
p16_84ee
 BEQ p16_84f2
p16_84f0
 LDA #$80
p16_84f2
 STA $24c4
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_17
 DEX
 SEC
 LDA $22b4
 SBC $a2
 STA $22b5
 LDA $22e2
 SBC $a3
 STA $22e3
 SEC
 LDA $2310
 SBC $a0
 STA $2311
 LDA $233e
 SBC $a1
 STA $233f

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2287
 lda $0900,x
 sta $23c6
 sbc $8c
 tax
 bcs positive_17
 lda high_table,x
 ora #$f0
 bne high_done_17
positive_17
 lda high_table,x
high_done_17
 sta $2399
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $236c
 ldx $2287
p17_84a7
 LDA $233f
p17_84aa
 BMI p17_84f0
p17_84ac
 BNE p17_84b5
p17_84ae
 LDA $2311
p17_84b1
 CMP #$20
p17_84b3
 BCC p17_84f0
p17_84b5
 LDA $22e3
p17_84b8
 BPL p17_84d9
p17_84ba
 SEC
p17_84bb
 LDA #$00
p17_84bd
 SBC $22b5
p17_84c0
 STA $b5
p17_84c2
 LDA #$00
p17_84c4
 SBC $22e3
p17_84c7
 CMP $233f
p17_84ca
 BCC p17_84ec
p17_84cc
 BNE p17_84d5
p17_84ce
 LDA $b5
p17_84d0
 CMP $2311
p17_84d3
 BCC p17_84ec
p17_84d5
 LDA #$40
p17_84d7
 BNE p17_84f2
p17_84d9
 CMP $233f
p17_84dc
 BCC p17_84ec
p17_84de
 BNE p17_84e8
p17_84e0
 LDA $22b5
p17_84e3
 CMP $2311
p17_84e6
 BCC p17_84ec
p17_84e8
 LDA #$20
p17_84ea
 BNE p17_84f2
p17_84ec
 LDA #$00
p17_84ee
 BEQ p17_84f2
p17_84f0
 LDA #$80
p17_84f2
 STA $24c5
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_18
 DEX
 SEC
 LDA $22b5
 SBC $a2
 STA $22b6
 LDA $22e3
 SBC $a3
 STA $22e4
 SEC
 LDA $2311
 SBC $a0
 STA $2312
 LDA $233f
 SBC $a1
 STA $2340

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2288
 lda $0900,x
 sta $23c7
 sbc $8c
 tax
 bcs positive_18
 lda high_table,x
 ora #$f0
 bne high_done_18
positive_18
 lda high_table,x
high_done_18
 sta $239a
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $236d
 ldx $2288
p18_84a7
 LDA $2340
p18_84aa
 BMI p18_84f0
p18_84ac
 BNE p18_84b5
p18_84ae
 LDA $2312
p18_84b1
 CMP #$20
p18_84b3
 BCC p18_84f0
p18_84b5
 LDA $22e4
p18_84b8
 BPL p18_84d9
p18_84ba
 SEC
p18_84bb
 LDA #$00
p18_84bd
 SBC $22b6
p18_84c0
 STA $b5
p18_84c2
 LDA #$00
p18_84c4
 SBC $22e4
p18_84c7
 CMP $2340
p18_84ca
 BCC p18_84ec
p18_84cc
 BNE p18_84d5
p18_84ce
 LDA $b5
p18_84d0
 CMP $2312
p18_84d3
 BCC p18_84ec
p18_84d5
 LDA #$40
p18_84d7
 BNE p18_84f2
p18_84d9
 CMP $2340
p18_84dc
 BCC p18_84ec
p18_84de
 BNE p18_84e8
p18_84e0
 LDA $22b6
p18_84e3
 CMP $2312
p18_84e6
 BCC p18_84ec
p18_84e8
 LDA #$20
p18_84ea
 BNE p18_84f2
p18_84ec
 LDA #$00
p18_84ee
 BEQ p18_84f2
p18_84f0
 LDA #$80
p18_84f2
 STA $24c6
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_19
 DEX
 SEC
 LDA $22b6
 SBC $a2
 STA $22b7
 LDA $22e4
 SBC $a3
 STA $22e5
 SEC
 LDA $2312
 SBC $a0
 STA $2313
 LDA $2340
 SBC $a1
 STA $2341

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2289
 lda $0900,x
 sta $23c8
 sbc $8c
 tax
 bcs positive_19
 lda high_table,x
 ora #$f0
 bne high_done_19
positive_19
 lda high_table,x
high_done_19
 sta $239b
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $236e
 ldx $2289
p19_84a7
 LDA $2341
p19_84aa
 BMI p19_84f0
p19_84ac
 BNE p19_84b5
p19_84ae
 LDA $2313
p19_84b1
 CMP #$20
p19_84b3
 BCC p19_84f0
p19_84b5
 LDA $22e5
p19_84b8
 BPL p19_84d9
p19_84ba
 SEC
p19_84bb
 LDA #$00
p19_84bd
 SBC $22b7
p19_84c0
 STA $b5
p19_84c2
 LDA #$00
p19_84c4
 SBC $22e5
p19_84c7
 CMP $2341
p19_84ca
 BCC p19_84ec
p19_84cc
 BNE p19_84d5
p19_84ce
 LDA $b5
p19_84d0
 CMP $2313
p19_84d3
 BCC p19_84ec
p19_84d5
 LDA #$40
p19_84d7
 BNE p19_84f2
p19_84d9
 CMP $2341
p19_84dc
 BCC p19_84ec
p19_84de
 BNE p19_84e8
p19_84e0
 LDA $22b7
p19_84e3
 CMP $2313
p19_84e6
 BCC p19_84ec
p19_84e8
 LDA #$20
p19_84ea
 BNE p19_84f2
p19_84ec
 LDA #$00
p19_84ee
 BEQ p19_84f2
p19_84f0
 LDA #$80
p19_84f2
 STA $24c7
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_20
 DEX
 SEC
 LDA $22b7
 SBC $a2
 STA $22b8
 LDA $22e5
 SBC $a3
 STA $22e6
 SEC
 LDA $2313
 SBC $a0
 STA $2314
 LDA $2341
 SBC $a1
 STA $2342

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $228a
 lda $0900,x
 sta $23c9
 sbc $8c
 tax
 bcs positive_20
 lda high_table,x
 ora #$f0
 bne high_done_20
positive_20
 lda high_table,x
high_done_20
 sta $239c
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $236f
 ldx $228a
p20_84a7
 LDA $2342
p20_84aa
 BMI p20_84f0
p20_84ac
 BNE p20_84b5
p20_84ae
 LDA $2314
p20_84b1
 CMP #$20
p20_84b3
 BCC p20_84f0
p20_84b5
 LDA $22e6
p20_84b8
 BPL p20_84d9
p20_84ba
 SEC
p20_84bb
 LDA #$00
p20_84bd
 SBC $22b8
p20_84c0
 STA $b5
p20_84c2
 LDA #$00
p20_84c4
 SBC $22e6
p20_84c7
 CMP $2342
p20_84ca
 BCC p20_84ec
p20_84cc
 BNE p20_84d5
p20_84ce
 LDA $b5
p20_84d0
 CMP $2314
p20_84d3
 BCC p20_84ec
p20_84d5
 LDA #$40
p20_84d7
 BNE p20_84f2
p20_84d9
 CMP $2342
p20_84dc
 BCC p20_84ec
p20_84de
 BNE p20_84e8
p20_84e0
 LDA $22b8
p20_84e3
 CMP $2314
p20_84e6
 BCC p20_84ec
p20_84e8
 LDA #$20
p20_84ea
 BNE p20_84f2
p20_84ec
 LDA #$00
p20_84ee
 BEQ p20_84f2
p20_84f0
 LDA #$80
p20_84f2
 STA $24c8
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_21
 DEX
 SEC
 LDA $22b8
 SBC $a2
 STA $22b9
 LDA $22e6
 SBC $a3
 STA $22e7
 SEC
 LDA $2314
 SBC $a0
 STA $2315
 LDA $2342
 SBC $a1
 STA $2343

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $228b
 lda $0900,x
 sta $23ca
 sbc $8c
 tax
 bcs positive_21
 lda high_table,x
 ora #$f0
 bne high_done_21
positive_21
 lda high_table,x
high_done_21
 sta $239d
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2370
 ldx $228b
p21_84a7
 LDA $2343
p21_84aa
 BMI p21_84f0
p21_84ac
 BNE p21_84b5
p21_84ae
 LDA $2315
p21_84b1
 CMP #$20
p21_84b3
 BCC p21_84f0
p21_84b5
 LDA $22e7
p21_84b8
 BPL p21_84d9
p21_84ba
 SEC
p21_84bb
 LDA #$00
p21_84bd
 SBC $22b9
p21_84c0
 STA $b5
p21_84c2
 LDA #$00
p21_84c4
 SBC $22e7
p21_84c7
 CMP $2343
p21_84ca
 BCC p21_84ec
p21_84cc
 BNE p21_84d5
p21_84ce
 LDA $b5
p21_84d0
 CMP $2315
p21_84d3
 BCC p21_84ec
p21_84d5
 LDA #$40
p21_84d7
 BNE p21_84f2
p21_84d9
 CMP $2343
p21_84dc
 BCC p21_84ec
p21_84de
 BNE p21_84e8
p21_84e0
 LDA $22b9
p21_84e3
 CMP $2315
p21_84e6
 BCC p21_84ec
p21_84e8
 LDA #$20
p21_84ea
 BNE p21_84f2
p21_84ec
 LDA #$00
p21_84ee
 BEQ p21_84f2
p21_84f0
 LDA #$80
p21_84f2
 STA $24c9
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_22
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22b9
 ADC $a0
 STA $22ba
 LDA $22e7
 ADC $a1
 STA $22e8
 SEC
 LDA $2315
 SBC $a2
 STA $2316
 LDA $2343
 SBC $a3
 STA $2344

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $228c
 lda $0900,x
 sta $23cb
 sbc $8c
 tax
 bcs positive_22
 lda high_table,x
 ora #$f0
 bne high_done_22
positive_22
 lda high_table,x
high_done_22
 sta $239e
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2371
 ldx $228c
p22_84a7
 LDA $2344
p22_84aa
 BMI p22_84f0
p22_84ac
 BNE p22_84b5
p22_84ae
 LDA $2316
p22_84b1
 CMP #$20
p22_84b3
 BCC p22_84f0
p22_84b5
 LDA $22e8
p22_84b8
 BPL p22_84d9
p22_84ba
 SEC
p22_84bb
 LDA #$00
p22_84bd
 SBC $22ba
p22_84c0
 STA $b5
p22_84c2
 LDA #$00
p22_84c4
 SBC $22e8
p22_84c7
 CMP $2344
p22_84ca
 BCC p22_84ec
p22_84cc
 BNE p22_84d5
p22_84ce
 LDA $b5
p22_84d0
 CMP $2316
p22_84d3
 BCC p22_84ec
p22_84d5
 LDA #$40
p22_84d7
 BNE p22_84f2
p22_84d9
 CMP $2344
p22_84dc
 BCC p22_84ec
p22_84de
 BNE p22_84e8
p22_84e0
 LDA $22ba
p22_84e3
 CMP $2316
p22_84e6
 BCC p22_84ec
p22_84e8
 LDA #$20
p22_84ea
 BNE p22_84f2
p22_84ec
 LDA #$00
p22_84ee
 BEQ p22_84f2
p22_84f0
 LDA #$80
p22_84f2
 STA $24ca
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_23
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22ba
 ADC $a0
 STA $22bb
 LDA $22e8
 ADC $a1
 STA $22e9
 SEC
 LDA $2316
 SBC $a2
 STA $2317
 LDA $2344
 SBC $a3
 STA $2345

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $228d
 lda $0900,x
 sta $23cc
 sbc $8c
 tax
 bcs positive_23
 lda high_table,x
 ora #$f0
 bne high_done_23
positive_23
 lda high_table,x
high_done_23
 sta $239f
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2372
 ldx $228d
p23_84a7
 LDA $2345
p23_84aa
 BMI p23_84f0
p23_84ac
 BNE p23_84b5
p23_84ae
 LDA $2317
p23_84b1
 CMP #$20
p23_84b3
 BCC p23_84f0
p23_84b5
 LDA $22e9
p23_84b8
 BPL p23_84d9
p23_84ba
 SEC
p23_84bb
 LDA #$00
p23_84bd
 SBC $22bb
p23_84c0
 STA $b5
p23_84c2
 LDA #$00
p23_84c4
 SBC $22e9
p23_84c7
 CMP $2345
p23_84ca
 BCC p23_84ec
p23_84cc
 BNE p23_84d5
p23_84ce
 LDA $b5
p23_84d0
 CMP $2317
p23_84d3
 BCC p23_84ec
p23_84d5
 LDA #$40
p23_84d7
 BNE p23_84f2
p23_84d9
 CMP $2345
p23_84dc
 BCC p23_84ec
p23_84de
 BNE p23_84e8
p23_84e0
 LDA $22bb
p23_84e3
 CMP $2317
p23_84e6
 BCC p23_84ec
p23_84e8
 LDA #$20
p23_84ea
 BNE p23_84f2
p23_84ec
 LDA #$00
p23_84ee
 BEQ p23_84f2
p23_84f0
 LDA #$80
p23_84f2
 STA $24cb
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_24
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22bb
 ADC $a0
 STA $22bc
 LDA $22e9
 ADC $a1
 STA $22ea
 SEC
 LDA $2317
 SBC $a2
 STA $2318
 LDA $2345
 SBC $a3
 STA $2346

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $228e
 lda $0900,x
 sta $23cd
 sbc $8c
 tax
 bcs positive_24
 lda high_table,x
 ora #$f0
 bne high_done_24
positive_24
 lda high_table,x
high_done_24
 sta $23a0
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2373
 ldx $228e
p24_84a7
 LDA $2346
p24_84aa
 BMI p24_84f0
p24_84ac
 BNE p24_84b5
p24_84ae
 LDA $2318
p24_84b1
 CMP #$20
p24_84b3
 BCC p24_84f0
p24_84b5
 LDA $22ea
p24_84b8
 BPL p24_84d9
p24_84ba
 SEC
p24_84bb
 LDA #$00
p24_84bd
 SBC $22bc
p24_84c0
 STA $b5
p24_84c2
 LDA #$00
p24_84c4
 SBC $22ea
p24_84c7
 CMP $2346
p24_84ca
 BCC p24_84ec
p24_84cc
 BNE p24_84d5
p24_84ce
 LDA $b5
p24_84d0
 CMP $2318
p24_84d3
 BCC p24_84ec
p24_84d5
 LDA #$40
p24_84d7
 BNE p24_84f2
p24_84d9
 CMP $2346
p24_84dc
 BCC p24_84ec
p24_84de
 BNE p24_84e8
p24_84e0
 LDA $22bc
p24_84e3
 CMP $2318
p24_84e6
 BCC p24_84ec
p24_84e8
 LDA #$20
p24_84ea
 BNE p24_84f2
p24_84ec
 LDA #$00
p24_84ee
 BEQ p24_84f2
p24_84f0
 LDA #$80
p24_84f2
 STA $24cc
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_25
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22bc
 ADC $a0
 STA $22bd
 LDA $22ea
 ADC $a1
 STA $22eb
 SEC
 LDA $2318
 SBC $a2
 STA $2319
 LDA $2346
 SBC $a3
 STA $2347

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $228f
 lda $0900,x
 sta $23ce
 sbc $8c
 tax
 bcs positive_25
 lda high_table,x
 ora #$f0
 bne high_done_25
positive_25
 lda high_table,x
high_done_25
 sta $23a1
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2374
 ldx $228f
p25_84a7
 LDA $2347
p25_84aa
 BMI p25_84f0
p25_84ac
 BNE p25_84b5
p25_84ae
 LDA $2319
p25_84b1
 CMP #$20
p25_84b3
 BCC p25_84f0
p25_84b5
 LDA $22eb
p25_84b8
 BPL p25_84d9
p25_84ba
 SEC
p25_84bb
 LDA #$00
p25_84bd
 SBC $22bd
p25_84c0
 STA $b5
p25_84c2
 LDA #$00
p25_84c4
 SBC $22eb
p25_84c7
 CMP $2347
p25_84ca
 BCC p25_84ec
p25_84cc
 BNE p25_84d5
p25_84ce
 LDA $b5
p25_84d0
 CMP $2319
p25_84d3
 BCC p25_84ec
p25_84d5
 LDA #$40
p25_84d7
 BNE p25_84f2
p25_84d9
 CMP $2347
p25_84dc
 BCC p25_84ec
p25_84de
 BNE p25_84e8
p25_84e0
 LDA $22bd
p25_84e3
 CMP $2319
p25_84e6
 BCC p25_84ec
p25_84e8
 LDA #$20
p25_84ea
 BNE p25_84f2
p25_84ec
 LDA #$00
p25_84ee
 BEQ p25_84f2
p25_84f0
 LDA #$80
p25_84f2
 STA $24cd
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_26
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22bd
 ADC $a0
 STA $22be
 LDA $22eb
 ADC $a1
 STA $22ec
 SEC
 LDA $2319
 SBC $a2
 STA $231a
 LDA $2347
 SBC $a3
 STA $2348

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2290
 lda $0900,x
 sta $23cf
 sbc $8c
 tax
 bcs positive_26
 lda high_table,x
 ora #$f0
 bne high_done_26
positive_26
 lda high_table,x
high_done_26
 sta $23a2
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2375
 ldx $2290
p26_84a7
 LDA $2348
p26_84aa
 BMI p26_84f0
p26_84ac
 BNE p26_84b5
p26_84ae
 LDA $231a
p26_84b1
 CMP #$20
p26_84b3
 BCC p26_84f0
p26_84b5
 LDA $22ec
p26_84b8
 BPL p26_84d9
p26_84ba
 SEC
p26_84bb
 LDA #$00
p26_84bd
 SBC $22be
p26_84c0
 STA $b5
p26_84c2
 LDA #$00
p26_84c4
 SBC $22ec
p26_84c7
 CMP $2348
p26_84ca
 BCC p26_84ec
p26_84cc
 BNE p26_84d5
p26_84ce
 LDA $b5
p26_84d0
 CMP $231a
p26_84d3
 BCC p26_84ec
p26_84d5
 LDA #$40
p26_84d7
 BNE p26_84f2
p26_84d9
 CMP $2348
p26_84dc
 BCC p26_84ec
p26_84de
 BNE p26_84e8
p26_84e0
 LDA $22be
p26_84e3
 CMP $231a
p26_84e6
 BCC p26_84ec
p26_84e8
 LDA #$20
p26_84ea
 BNE p26_84f2
p26_84ec
 LDA #$00
p26_84ee
 BEQ p26_84f2
p26_84f0
 LDA #$80
p26_84f2
 STA $24ce
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_27
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22be
 ADC $a0
 STA $22bf
 LDA $22ec
 ADC $a1
 STA $22ed
 SEC
 LDA $231a
 SBC $a2
 STA $231b
 LDA $2348
 SBC $a3
 STA $2349

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2291
 lda $0900,x
 sta $23d0
 sbc $8c
 tax
 bcs positive_27
 lda high_table,x
 ora #$f0
 bne high_done_27
positive_27
 lda high_table,x
high_done_27
 sta $23a3
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2376
 ldx $2291
p27_84a7
 LDA $2349
p27_84aa
 BMI p27_84f0
p27_84ac
 BNE p27_84b5
p27_84ae
 LDA $231b
p27_84b1
 CMP #$20
p27_84b3
 BCC p27_84f0
p27_84b5
 LDA $22ed
p27_84b8
 BPL p27_84d9
p27_84ba
 SEC
p27_84bb
 LDA #$00
p27_84bd
 SBC $22bf
p27_84c0
 STA $b5
p27_84c2
 LDA #$00
p27_84c4
 SBC $22ed
p27_84c7
 CMP $2349
p27_84ca
 BCC p27_84ec
p27_84cc
 BNE p27_84d5
p27_84ce
 LDA $b5
p27_84d0
 CMP $231b
p27_84d3
 BCC p27_84ec
p27_84d5
 LDA #$40
p27_84d7
 BNE p27_84f2
p27_84d9
 CMP $2349
p27_84dc
 BCC p27_84ec
p27_84de
 BNE p27_84e8
p27_84e0
 LDA $22bf
p27_84e3
 CMP $231b
p27_84e6
 BCC p27_84ec
p27_84e8
 LDA #$20
p27_84ea
 BNE p27_84f2
p27_84ec
 LDA #$00
p27_84ee
 BEQ p27_84f2
p27_84f0
 LDA #$80
p27_84f2
 STA $24cf
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_28
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22bf
 ADC $a0
 STA $22c0
 LDA $22ed
 ADC $a1
 STA $22ee
 SEC
 LDA $231b
 SBC $a2
 STA $231c
 LDA $2349
 SBC $a3
 STA $234a
 DEX
 SEC
 LDA $22c0
 SBC $a2
 STA $22c0
 LDA $22ee
 SBC $a3
 STA $22ee
 SEC
 LDA $231c
 SBC $a0
 STA $231c
 LDA $234a
 SBC $a1
 STA $234a

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2292
 lda $0900,x
 sta $23d1
 sbc $8c
 tax
 bcs positive_28
 lda high_table,x
 ora #$f0
 bne high_done_28
positive_28
 lda high_table,x
high_done_28
 sta $23a4
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2377
 ldx $2292
p28_84a7
 LDA $234a
p28_84aa
 BMI p28_84f0
p28_84ac
 BNE p28_84b5
p28_84ae
 LDA $231c
p28_84b1
 CMP #$20
p28_84b3
 BCC p28_84f0
p28_84b5
 LDA $22ee
p28_84b8
 BPL p28_84d9
p28_84ba
 SEC
p28_84bb
 LDA #$00
p28_84bd
 SBC $22c0
p28_84c0
 STA $b5
p28_84c2
 LDA #$00
p28_84c4
 SBC $22ee
p28_84c7
 CMP $234a
p28_84ca
 BCC p28_84ec
p28_84cc
 BNE p28_84d5
p28_84ce
 LDA $b5
p28_84d0
 CMP $231c
p28_84d3
 BCC p28_84ec
p28_84d5
 LDA #$40
p28_84d7
 BNE p28_84f2
p28_84d9
 CMP $234a
p28_84dc
 BCC p28_84ec
p28_84de
 BNE p28_84e8
p28_84e0
 LDA $22c0
p28_84e3
 CMP $231c
p28_84e6
 BCC p28_84ec
p28_84e8
 LDA #$20
p28_84ea
 BNE p28_84f2
p28_84ec
 LDA #$00
p28_84ee
 BEQ p28_84f2
p28_84f0
 LDA #$80
p28_84f2
 STA $24d0
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_29
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22c0
 SBC $a0
 STA $22c1
 LDA $22ee
 SBC $a1
 STA $22ef
 CLC
 LDA $231c
 ADC $a2
 STA $231d
 LDA $234a
 ADC $a3
 STA $234b

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2293
 lda $0900,x
 sta $23d2
 sbc $8c
 tax
 bcs positive_29
 lda high_table,x
 ora #$f0
 bne high_done_29
positive_29
 lda high_table,x
high_done_29
 sta $23a5
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2378
 ldx $2293
p29_84a7
 LDA $234b
p29_84aa
 BMI p29_84f0
p29_84ac
 BNE p29_84b5
p29_84ae
 LDA $231d
p29_84b1
 CMP #$20
p29_84b3
 BCC p29_84f0
p29_84b5
 LDA $22ef
p29_84b8
 BPL p29_84d9
p29_84ba
 SEC
p29_84bb
 LDA #$00
p29_84bd
 SBC $22c1
p29_84c0
 STA $b5
p29_84c2
 LDA #$00
p29_84c4
 SBC $22ef
p29_84c7
 CMP $234b
p29_84ca
 BCC p29_84ec
p29_84cc
 BNE p29_84d5
p29_84ce
 LDA $b5
p29_84d0
 CMP $231d
p29_84d3
 BCC p29_84ec
p29_84d5
 LDA #$40
p29_84d7
 BNE p29_84f2
p29_84d9
 CMP $234b
p29_84dc
 BCC p29_84ec
p29_84de
 BNE p29_84e8
p29_84e0
 LDA $22c1
p29_84e3
 CMP $231d
p29_84e6
 BCC p29_84ec
p29_84e8
 LDA #$20
p29_84ea
 BNE p29_84f2
p29_84ec
 LDA #$00
p29_84ee
 BEQ p29_84f2
p29_84f0
 LDA #$80
p29_84f2
 STA $24d1
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_30
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22c1
 SBC $a0
 STA $22c2
 LDA $22ef
 SBC $a1
 STA $22f0
 CLC
 LDA $231d
 ADC $a2
 STA $231e
 LDA $234b
 ADC $a3
 STA $234c

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2294
 lda $0900,x
 sta $23d3
 sbc $8c
 tax
 bcs positive_30
 lda high_table,x
 ora #$f0
 bne high_done_30
positive_30
 lda high_table,x
high_done_30
 sta $23a6
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2379
 ldx $2294
p30_84a7
 LDA $234c
p30_84aa
 BMI p30_84f0
p30_84ac
 BNE p30_84b5
p30_84ae
 LDA $231e
p30_84b1
 CMP #$20
p30_84b3
 BCC p30_84f0
p30_84b5
 LDA $22f0
p30_84b8
 BPL p30_84d9
p30_84ba
 SEC
p30_84bb
 LDA #$00
p30_84bd
 SBC $22c2
p30_84c0
 STA $b5
p30_84c2
 LDA #$00
p30_84c4
 SBC $22f0
p30_84c7
 CMP $234c
p30_84ca
 BCC p30_84ec
p30_84cc
 BNE p30_84d5
p30_84ce
 LDA $b5
p30_84d0
 CMP $231e
p30_84d3
 BCC p30_84ec
p30_84d5
 LDA #$40
p30_84d7
 BNE p30_84f2
p30_84d9
 CMP $234c
p30_84dc
 BCC p30_84ec
p30_84de
 BNE p30_84e8
p30_84e0
 LDA $22c2
p30_84e3
 CMP $231e
p30_84e6
 BCC p30_84ec
p30_84e8
 LDA #$20
p30_84ea
 BNE p30_84f2
p30_84ec
 LDA #$00
p30_84ee
 BEQ p30_84f2
p30_84f0
 LDA #$80
p30_84f2
 STA $24d2
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_31
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22c2
 SBC $a0
 STA $22c3
 LDA $22f0
 SBC $a1
 STA $22f1
 CLC
 LDA $231e
 ADC $a2
 STA $231f
 LDA $234c
 ADC $a3
 STA $234d

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2295
 lda $0900,x
 sta $23d4
 sbc $8c
 tax
 bcs positive_31
 lda high_table,x
 ora #$f0
 bne high_done_31
positive_31
 lda high_table,x
high_done_31
 sta $23a7
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $237a
 ldx $2295
p31_84a7
 LDA $234d
p31_84aa
 BMI p31_84f0
p31_84ac
 BNE p31_84b5
p31_84ae
 LDA $231f
p31_84b1
 CMP #$20
p31_84b3
 BCC p31_84f0
p31_84b5
 LDA $22f1
p31_84b8
 BPL p31_84d9
p31_84ba
 SEC
p31_84bb
 LDA #$00
p31_84bd
 SBC $22c3
p31_84c0
 STA $b5
p31_84c2
 LDA #$00
p31_84c4
 SBC $22f1
p31_84c7
 CMP $234d
p31_84ca
 BCC p31_84ec
p31_84cc
 BNE p31_84d5
p31_84ce
 LDA $b5
p31_84d0
 CMP $231f
p31_84d3
 BCC p31_84ec
p31_84d5
 LDA #$40
p31_84d7
 BNE p31_84f2
p31_84d9
 CMP $234d
p31_84dc
 BCC p31_84ec
p31_84de
 BNE p31_84e8
p31_84e0
 LDA $22c3
p31_84e3
 CMP $231f
p31_84e6
 BCC p31_84ec
p31_84e8
 LDA #$20
p31_84ea
 BNE p31_84f2
p31_84ec
 LDA #$00
p31_84ee
 BEQ p31_84f2
p31_84f0
 LDA #$80
p31_84f2
 STA $24d3
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_32
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22c3
 SBC $a0
 STA $22c4
 LDA $22f1
 SBC $a1
 STA $22f2
 CLC
 LDA $231f
 ADC $a2
 STA $2320
 LDA $234d
 ADC $a3
 STA $234e

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2296
 lda $0900,x
 sta $23d5
 sbc $8c
 tax
 bcs positive_32
 lda high_table,x
 ora #$f0
 bne high_done_32
positive_32
 lda high_table,x
high_done_32
 sta $23a8
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $237b
 ldx $2296
p32_84a7
 LDA $234e
p32_84aa
 BMI p32_84f0
p32_84ac
 BNE p32_84b5
p32_84ae
 LDA $2320
p32_84b1
 CMP #$20
p32_84b3
 BCC p32_84f0
p32_84b5
 LDA $22f2
p32_84b8
 BPL p32_84d9
p32_84ba
 SEC
p32_84bb
 LDA #$00
p32_84bd
 SBC $22c4
p32_84c0
 STA $b5
p32_84c2
 LDA #$00
p32_84c4
 SBC $22f2
p32_84c7
 CMP $234e
p32_84ca
 BCC p32_84ec
p32_84cc
 BNE p32_84d5
p32_84ce
 LDA $b5
p32_84d0
 CMP $2320
p32_84d3
 BCC p32_84ec
p32_84d5
 LDA #$40
p32_84d7
 BNE p32_84f2
p32_84d9
 CMP $234e
p32_84dc
 BCC p32_84ec
p32_84de
 BNE p32_84e8
p32_84e0
 LDA $22c4
p32_84e3
 CMP $2320
p32_84e6
 BCC p32_84ec
p32_84e8
 LDA #$20
p32_84ea
 BNE p32_84f2
p32_84ec
 LDA #$00
p32_84ee
 BEQ p32_84f2
p32_84f0
 LDA #$80
p32_84f2
 STA $24d4
 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_33
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22c4
 SBC $a0
 STA $22c5
 LDA $22f2
 SBC $a1
 STA $22f3
 CLC
 LDA $2320
 ADC $a2
 STA $2321
 LDA $234e
 ADC $a3
 STA $234f

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2297
 lda $0900,x
 sta $23d6
 sbc $8c
 tax
 bcs positive_33
 lda high_table,x
 ora #$f0
 bne high_done_33
positive_33
 lda high_table,x
high_done_33
 sta $23a9
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $237c
 ldx $2297

 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_34
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22c5
 SBC $a0
 STA $22c6
 LDA $22f3
 SBC $a1
 STA $22f4
 CLC
 LDA $2321
 ADC $a2
 STA $2322
 LDA $234f
 ADC $a3
 STA $2350

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2298
 lda $0900,x
 sta $23d7
 sbc $8c
 tax
 bcs positive_34
 lda high_table,x
 ora #$f0
 bne high_done_34
positive_34
 lda high_table,x
high_done_34
 sta $23aa
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $237d
 ldx $2298

 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_35
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22c6
 SBC $a0
 STA $22c7
 LDA $22f4
 SBC $a1
 STA $22f5
 CLC
 LDA $2322
 ADC $a2
 STA $2323
 LDA $2350
 ADC $a3
 STA $2351

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $2299
 lda $0900,x
 sta $23d8
 sbc $8c
 tax
 bcs positive_35
 lda high_table,x
 ora #$f0
 bne high_done_35
positive_35
 lda high_table,x
high_done_35
 sta $23ab
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $237e
 ldx $2299

 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_36
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22c7
 SBC $a0
 STA $22c8
 LDA $22f5
 SBC $a1
 STA $22f6
 CLC
 LDA $2323
 ADC $a2
 STA $2324
 LDA $2351
 ADC $a3
 STA $2352

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $229a
 lda $0900,x
 sta $23d9
 sbc $8c
 tax
 bcs positive_36
 lda high_table,x
 ora #$f0
 bne high_done_36
positive_36
 lda high_table,x
high_done_36
 sta $23ac
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $237f
 ldx $229a

 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_37
 INX
 CLC
 LDA $22c8
 ADC $a2
 STA $22c9
 LDA $22f6
 ADC $a3
 STA $22f7
 CLC
 LDA $2324
 ADC $a0
 STA $2325
 LDA $2352
 ADC $a1
 STA $2353

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $229b
 lda $0900,x
 sta $23da
 sbc $8c
 tax
 bcs positive_37
 lda high_table,x
 ora #$f0
 bne high_done_37
positive_37
 lda high_table,x
high_done_37
 sta $23ad
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2380
 ldx $229b

 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_38
 INX
 CLC
 LDA $22c9
 ADC $a2
 STA $22ca
 LDA $22f7
 ADC $a3
 STA $22f8
 CLC
 LDA $2325
 ADC $a0
 STA $2326
 LDA $2353
 ADC $a1
 STA $2354

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $229c
 lda $0900,x
 sta $23db
 sbc $8c
 tax
 bcs positive_38
 lda high_table,x
 ora #$f0
 bne high_done_38
positive_38
 lda high_table,x
high_done_38
 sta $23ae
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2381
 ldx $229c

 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_39
 INX
 CLC
 LDA $22ca
 ADC $a2
 STA $22cb
 LDA $22f8
 ADC $a3
 STA $22f9
 CLC
 LDA $2326
 ADC $a0
 STA $2327
 LDA $2354
 ADC $a1
 STA $2355

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $229d
 lda $0900,x
 sta $23dc
 sbc $8c
 tax
 bcs positive_39
 lda high_table,x
 ora #$f0
 bne high_done_39
positive_39
 lda high_table,x
high_done_39
 sta $23af
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2382
 ldx $229d

 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_40
 INX
 CLC
 LDA $22cb
 ADC $a2
 STA $22cc
 LDA $22f9
 ADC $a3
 STA $22fa
 CLC
 LDA $2327
 ADC $a0
 STA $2328
 LDA $2355
 ADC $a1
 STA $2356

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $229e
 lda $0900,x
 sta $23dd
 sbc $8c
 tax
 bcs positive_40
 lda high_table,x
 ora #$f0
 bne high_done_40
positive_40
 lda high_table,x
high_done_40
 sta $23b0
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2383
 ldx $229e

 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_41
 INX
 CLC
 LDA $22cc
 ADC $a2
 STA $22cd
 LDA $22fa
 ADC $a3
 STA $22fb
 CLC
 LDA $2328
 ADC $a0
 STA $2329
 LDA $2356
 ADC $a1
 STA $2357

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $229f
 lda $0900,x
 sta $23de
 sbc $8c
 tax
 bcs positive_41
 lda high_table,x
 ora #$f0
 bne high_done_41
positive_41
 lda high_table,x
high_done_41
 sta $23b1
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2384
 ldx $229f

 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_42
 INX
 CLC
 LDA $22cd
 ADC $a2
 STA $22ce
 LDA $22fb
 ADC $a3
 STA $22fc
 CLC
 LDA $2329
 ADC $a0
 STA $232a
 LDA $2357
 ADC $a1
 STA $2358

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $22a0
 lda $0900,x
 sta $23df
 sbc $8c
 tax
 bcs positive_42
 lda high_table,x
 ora #$f0
 bne high_done_42
positive_42
 lda high_table,x
high_done_42
 sta $23b2
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2385
 ldx $22a0

 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
point_43
 INX
 CLC
 LDA $22ce
 ADC $a2
 STA $22cf
 LDA $22fc
 ADC $a3
 STA $22fd
 CLC
 LDA $232a
 ADC $a0
 STA $232b
 LDA $2358
 ADC $a1
 STA $2359

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $22a1
 lda $0900,x
 sta $23e0
 sbc $8c
 tax
 bcs positive_43
 lda high_table,x
 ora #$f0
 bne high_done_43
positive_43
 lda high_table,x
high_done_43
 sta $23b3
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2386
 ldx $22a1

 ift * > $97b0 .and * < $9900
 jmp $9900
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 :($9900-*) dta $ff
 eif
 ldy #33
classify_batch
c_84a7
 LDA $232e,Y
c_84aa
 BMI c_84f0
c_84ac
 BNE c_84b5
c_84ae
 LDA $2300,Y
c_84b1
 CMP #$20
c_84b3
 BCC c_84f0
c_84b5
 LDA $22d2,Y
c_84b8
 BPL c_84d9
c_84ba
 SEC
c_84bb
 LDA #$00
c_84bd
 SBC $22a4,Y
c_84c0
 STA $b5
c_84c2
 LDA #$00
c_84c4
 SBC $22d2,Y
c_84c7
 CMP $232e,Y
c_84ca
 BCC c_84ec
c_84cc
 BNE c_84d5
c_84ce
 LDA $b5
c_84d0
 CMP $2300,Y
c_84d3
 BCC c_84ec
c_84d5
 LDA #$40
c_84d7
 BNE c_84f2
c_84d9
 CMP $232e,Y
c_84dc
 BCC c_84ec
c_84de
 BNE c_84e8
c_84e0
 LDA $22a4,Y
c_84e3
 CMP $2300,Y
c_84e6
 BCC c_84ec
c_84e8
 LDA #$20
c_84ea
 BNE c_84f2
c_84ec
 LDA #$00
c_84ee
 BEQ c_84f2
c_84f0
 LDA #$80
c_84f2
 STA $24b4,Y
 iny
 cpy #44
 bne classify_batch
point_44
 INX
 CLC
 LDA $22cf
 ADC $a2
 STA $22d0
 LDA $22fd
 ADC $a3
 STA $22fe
 CLC
 LDA $232b
 ADC $a0
 STA $232c
 LDA $2359
 ADC $a1
 STA $235a

 lda #0
 cmp $8b
 txa
 and #15
 ora $b6
 tax
 stx $22a2
 lda $0900,x
 sta $23e1
 sbc $8c
 tax
 bcs positive_44
 lda high_table,x
 ora #$f0
 bne high_done_44
positive_44
 lda high_table,x
high_done_44
 sta $23b4
 lda $9f
 lsr @
 ora low_table,x
 sta $b5
 sta $2387
 ldx $22a2

p44_84a7
 LDA $235a
p44_84aa
 BMI p44_84f0
p44_84ac
 BNE p44_84b5
p44_84ae
 LDA $232c
p44_84b1
 CMP #$20
p44_84b3
 BCC p44_84f0
p44_84b5
 LDA $22fe
p44_84b8
 BPL p44_84d9
p44_84ba
 SEC
p44_84bb
 LDA #$00
p44_84bd
 SBC $22d0
p44_84c0
 STA $b5
p44_84c2
 LDA #$00
p44_84c4
 SBC $22fe
p44_84c7
 CMP $235a
p44_84ca
 BCC p44_84ec
p44_84cc
 BNE p44_84d5
p44_84ce
 LDA $b5
p44_84d0
 CMP $232c
p44_84d3
 BCC p44_84ec
p44_84d5
 LDA #$40
p44_84d7
 BNE p44_84f2
p44_84d9
 CMP $235a
p44_84dc
 BCC p44_84ec
p44_84de
 BNE p44_84e8
p44_84e0
 LDA $22d0
p44_84e3
 CMP $232c
p44_84e6
 BCC p44_84ec
p44_84e8
 LDA #$20
p44_84ea
 BNE p44_84f2
p44_84ec
 LDA #$00
p44_84ee
 BEQ p44_84f2
p44_84f0
 LDA #$80
p44_84f2
 STA $24e0
 tay
 pla
 sta $9f
 tya
 ldy #45
 cpy #45
 jmp $98e0
code_end
 ert * > $9d00
 :($9d00-*) dta $ff
high_table
 dta 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
 dta 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
 dta 2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2
 dta 3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3
 dta 4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4
 dta 5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5
 dta 6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6
 dta 7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7
 dta 8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8
 dta 9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9
 dta 10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10
 dta 11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11
 dta 12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12
 dta 13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13
 dta 14,14,14,14,14,14,14,14,14,14,14,14,14,14,14,14
 dta 15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15
low_table
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 dta 0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240
 :($9fff-*) dta $ff
 dta 10
