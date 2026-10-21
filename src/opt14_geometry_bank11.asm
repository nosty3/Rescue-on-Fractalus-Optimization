; Generated constant command stream; only original command selection is removed.
 opt h-
 org $8000
entry
 ldy #0
point_0
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22a3
 SBC $a0
 STA $22a4
 LDA $22d1
 SBC $a1
 STA $22d2
 CLC
 LDA $22ff
 ADC $a2
 STA $2300
 LDA $232d
 ADC $a3
 STA $232e
 INX
 CLC
 LDA $22a4
 ADC $a2
 STA $22a4
 LDA $22d2
 ADC $a3
 STA $22d2
 CLC
 LDA $2300
 ADC $a0
 STA $2300
 LDA $232e
 ADC $a1
 STA $232e
 jsr point_tail
 iny
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
 DEX
 SEC
 LDA $22a5
 SBC $a2
 STA $22a5
 LDA $22d3
 SBC $a3
 STA $22d3
 SEC
 LDA $2301
 SBC $a0
 STA $2301
 LDA $232f
 SBC $a1
 STA $232f
 jsr point_tail
 iny
point_2
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22a5
 ADC $a0
 STA $22a6
 LDA $22d3
 ADC $a1
 STA $22d4
 SEC
 LDA $2301
 SBC $a2
 STA $2302
 LDA $232f
 SBC $a3
 STA $2330
 jsr point_tail
 iny
point_3
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22a6
 ADC $a0
 STA $22a7
 LDA $22d4
 ADC $a1
 STA $22d5
 SEC
 LDA $2302
 SBC $a2
 STA $2303
 LDA $2330
 SBC $a3
 STA $2331
 jsr point_tail
 iny
point_4
 INX
 CLC
 LDA $22a7
 ADC $a2
 STA $22a8
 LDA $22d5
 ADC $a3
 STA $22d6
 CLC
 LDA $2303
 ADC $a0
 STA $2304
 LDA $2331
 ADC $a1
 STA $2332
 jsr point_tail
 iny
point_5
 INX
 CLC
 LDA $22a8
 ADC $a2
 STA $22a9
 LDA $22d6
 ADC $a3
 STA $22d7
 CLC
 LDA $2304
 ADC $a0
 STA $2305
 LDA $2332
 ADC $a1
 STA $2333
 jsr point_tail
 iny
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
 INX
 CLC
 LDA $22aa
 ADC $a2
 STA $22aa
 LDA $22d8
 ADC $a3
 STA $22d8
 CLC
 LDA $2306
 ADC $a0
 STA $2306
 LDA $2334
 ADC $a1
 STA $2334
 jsr point_tail
 iny
point_7
 DEX
 SEC
 LDA $22aa
 SBC $a2
 STA $22ab
 LDA $22d8
 SBC $a3
 STA $22d9
 SEC
 LDA $2306
 SBC $a0
 STA $2307
 LDA $2334
 SBC $a1
 STA $2335
 jsr point_tail
 iny
point_8
 DEX
 SEC
 LDA $22ab
 SBC $a2
 STA $22ac
 LDA $22d9
 SBC $a3
 STA $22da
 SEC
 LDA $2307
 SBC $a0
 STA $2308
 LDA $2335
 SBC $a1
 STA $2336
 jsr point_tail
 iny
point_9
 DEX
 SEC
 LDA $22ac
 SBC $a2
 STA $22ad
 LDA $22da
 SBC $a3
 STA $22db
 SEC
 LDA $2308
 SBC $a0
 STA $2309
 LDA $2336
 SBC $a1
 STA $2337
 jsr point_tail
 iny
point_10
 DEX
 SEC
 LDA $22ad
 SBC $a2
 STA $22ae
 LDA $22db
 SBC $a3
 STA $22dc
 SEC
 LDA $2309
 SBC $a0
 STA $230a
 LDA $2337
 SBC $a1
 STA $2338
 jsr point_tail
 iny
point_11
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22ae
 SBC $a0
 STA $22af
 LDA $22dc
 SBC $a1
 STA $22dd
 CLC
 LDA $230a
 ADC $a2
 STA $230b
 LDA $2338
 ADC $a3
 STA $2339
 jsr point_tail
 iny
point_12
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22af
 SBC $a0
 STA $22b0
 LDA $22dd
 SBC $a1
 STA $22de
 CLC
 LDA $230b
 ADC $a2
 STA $230c
 LDA $2339
 ADC $a3
 STA $233a
 jsr point_tail
 iny
point_13
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22b0
 SBC $a0
 STA $22b1
 LDA $22de
 SBC $a1
 STA $22df
 CLC
 LDA $230c
 ADC $a2
 STA $230d
 LDA $233a
 ADC $a3
 STA $233b
 jsr point_tail
 iny
point_14
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22b1
 SBC $a0
 STA $22b2
 LDA $22df
 SBC $a1
 STA $22e0
 CLC
 LDA $230d
 ADC $a2
 STA $230e
 LDA $233b
 ADC $a3
 STA $233c
 jsr point_tail
 iny
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
 DEX
 SEC
 LDA $22b3
 SBC $a2
 STA $22b3
 LDA $22e1
 SBC $a3
 STA $22e1
 SEC
 LDA $230f
 SBC $a0
 STA $230f
 LDA $233d
 SBC $a1
 STA $233d
 jsr point_tail
 iny
point_16
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22b3
 ADC $a0
 STA $22b4
 LDA $22e1
 ADC $a1
 STA $22e2
 SEC
 LDA $230f
 SBC $a2
 STA $2310
 LDA $233d
 SBC $a3
 STA $233e
 jsr point_tail
 iny
point_17
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22b4
 ADC $a0
 STA $22b5
 LDA $22e2
 ADC $a1
 STA $22e3
 SEC
 LDA $2310
 SBC $a2
 STA $2311
 LDA $233e
 SBC $a3
 STA $233f
 jsr point_tail
 iny
point_18
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22b5
 ADC $a0
 STA $22b6
 LDA $22e3
 ADC $a1
 STA $22e4
 SEC
 LDA $2311
 SBC $a2
 STA $2312
 LDA $233f
 SBC $a3
 STA $2340
 jsr point_tail
 iny
point_19
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22b6
 ADC $a0
 STA $22b7
 LDA $22e4
 ADC $a1
 STA $22e5
 SEC
 LDA $2312
 SBC $a2
 STA $2313
 LDA $2340
 SBC $a3
 STA $2341
 jsr point_tail
 iny
point_20
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22b7
 ADC $a0
 STA $22b8
 LDA $22e5
 ADC $a1
 STA $22e6
 SEC
 LDA $2313
 SBC $a2
 STA $2314
 LDA $2341
 SBC $a3
 STA $2342
 jsr point_tail
 iny
point_21
 LDA $b6
 CLC
 ADC #$f0
 STA $b6
 CLC
 LDA $22b8
 ADC $a0
 STA $22b9
 LDA $22e6
 ADC $a1
 STA $22e7
 SEC
 LDA $2314
 SBC $a2
 STA $2315
 LDA $2342
 SBC $a3
 STA $2343
 jsr point_tail
 iny
point_22
 INX
 CLC
 LDA $22b9
 ADC $a2
 STA $22ba
 LDA $22e7
 ADC $a3
 STA $22e8
 CLC
 LDA $2315
 ADC $a0
 STA $2316
 LDA $2343
 ADC $a1
 STA $2344
 jsr point_tail
 iny
point_23
 INX
 CLC
 LDA $22ba
 ADC $a2
 STA $22bb
 LDA $22e8
 ADC $a3
 STA $22e9
 CLC
 LDA $2316
 ADC $a0
 STA $2317
 LDA $2344
 ADC $a1
 STA $2345
 jsr point_tail
 iny
point_24
 INX
 CLC
 LDA $22bb
 ADC $a2
 STA $22bc
 LDA $22e9
 ADC $a3
 STA $22ea
 CLC
 LDA $2317
 ADC $a0
 STA $2318
 LDA $2345
 ADC $a1
 STA $2346
 jsr point_tail
 iny
point_25
 INX
 CLC
 LDA $22bc
 ADC $a2
 STA $22bd
 LDA $22ea
 ADC $a3
 STA $22eb
 CLC
 LDA $2318
 ADC $a0
 STA $2319
 LDA $2346
 ADC $a1
 STA $2347
 jsr point_tail
 iny
point_26
 INX
 CLC
 LDA $22bd
 ADC $a2
 STA $22be
 LDA $22eb
 ADC $a3
 STA $22ec
 CLC
 LDA $2319
 ADC $a0
 STA $231a
 LDA $2347
 ADC $a1
 STA $2348
 jsr point_tail
 iny
point_27
 INX
 CLC
 LDA $22be
 ADC $a2
 STA $22bf
 LDA $22ec
 ADC $a3
 STA $22ed
 CLC
 LDA $231a
 ADC $a0
 STA $231b
 LDA $2348
 ADC $a1
 STA $2349
 jsr point_tail
 iny
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
 INX
 CLC
 LDA $22c0
 ADC $a2
 STA $22c0
 LDA $22ee
 ADC $a3
 STA $22ee
 CLC
 LDA $231c
 ADC $a0
 STA $231c
 LDA $234a
 ADC $a1
 STA $234a
 jsr point_tail
 iny
point_29
 DEX
 SEC
 LDA $22c0
 SBC $a2
 STA $22c1
 LDA $22ee
 SBC $a3
 STA $22ef
 SEC
 LDA $231c
 SBC $a0
 STA $231d
 LDA $234a
 SBC $a1
 STA $234b
 jsr point_tail
 iny
point_30
 DEX
 SEC
 LDA $22c1
 SBC $a2
 STA $22c2
 LDA $22ef
 SBC $a3
 STA $22f0
 SEC
 LDA $231d
 SBC $a0
 STA $231e
 LDA $234b
 SBC $a1
 STA $234c
 jsr point_tail
 iny
point_31
 DEX
 SEC
 LDA $22c2
 SBC $a2
 STA $22c3
 LDA $22f0
 SBC $a3
 STA $22f1
 SEC
 LDA $231e
 SBC $a0
 STA $231f
 LDA $234c
 SBC $a1
 STA $234d
 jsr point_tail
 iny
point_32
 DEX
 SEC
 LDA $22c3
 SBC $a2
 STA $22c4
 LDA $22f1
 SBC $a3
 STA $22f2
 SEC
 LDA $231f
 SBC $a0
 STA $2320
 LDA $234d
 SBC $a1
 STA $234e
 jsr point_tail
 iny
point_33
 DEX
 SEC
 LDA $22c4
 SBC $a2
 STA $22c5
 LDA $22f2
 SBC $a3
 STA $22f3
 SEC
 LDA $2320
 SBC $a0
 STA $2321
 LDA $234e
 SBC $a1
 STA $234f
 jsr point_tail
 iny
point_34
 DEX
 SEC
 LDA $22c5
 SBC $a2
 STA $22c6
 LDA $22f3
 SBC $a3
 STA $22f4
 SEC
 LDA $2321
 SBC $a0
 STA $2322
 LDA $234f
 SBC $a1
 STA $2350
 jsr point_tail
 iny
point_35
 DEX
 SEC
 LDA $22c6
 SBC $a2
 STA $22c7
 LDA $22f4
 SBC $a3
 STA $22f5
 SEC
 LDA $2322
 SBC $a0
 STA $2323
 LDA $2350
 SBC $a1
 STA $2351
 jsr point_tail
 iny
point_36
 DEX
 SEC
 LDA $22c7
 SBC $a2
 STA $22c8
 LDA $22f5
 SBC $a3
 STA $22f6
 SEC
 LDA $2323
 SBC $a0
 STA $2324
 LDA $2351
 SBC $a1
 STA $2352
 jsr point_tail
 iny
point_37
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22c8
 SBC $a0
 STA $22c9
 LDA $22f6
 SBC $a1
 STA $22f7
 CLC
 LDA $2324
 ADC $a2
 STA $2325
 LDA $2352
 ADC $a3
 STA $2353
 jsr point_tail
 iny
point_38
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22c9
 SBC $a0
 STA $22ca
 LDA $22f7
 SBC $a1
 STA $22f8
 CLC
 LDA $2325
 ADC $a2
 STA $2326
 LDA $2353
 ADC $a3
 STA $2354
 jsr point_tail
 iny
point_39
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22ca
 SBC $a0
 STA $22cb
 LDA $22f8
 SBC $a1
 STA $22f9
 CLC
 LDA $2326
 ADC $a2
 STA $2327
 LDA $2354
 ADC $a3
 STA $2355
 jsr point_tail
 iny
point_40
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22cb
 SBC $a0
 STA $22cc
 LDA $22f9
 SBC $a1
 STA $22fa
 CLC
 LDA $2327
 ADC $a2
 STA $2328
 LDA $2355
 ADC $a3
 STA $2356
 jsr point_tail
 iny
point_41
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22cc
 SBC $a0
 STA $22cd
 LDA $22fa
 SBC $a1
 STA $22fb
 CLC
 LDA $2328
 ADC $a2
 STA $2329
 LDA $2356
 ADC $a3
 STA $2357
 jsr point_tail
 iny
point_42
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22cd
 SBC $a0
 STA $22ce
 LDA $22fb
 SBC $a1
 STA $22fc
 CLC
 LDA $2329
 ADC $a2
 STA $232a
 LDA $2357
 ADC $a3
 STA $2358
 jsr point_tail
 iny
point_43
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22ce
 SBC $a0
 STA $22cf
 LDA $22fc
 SBC $a1
 STA $22fd
 CLC
 LDA $232a
 ADC $a2
 STA $232b
 LDA $2358
 ADC $a3
 STA $2359
 jsr point_tail
 iny
point_44
 LDA $b6
 CLC
 ADC #$10
 STA $b6
 SEC
 LDA $22cf
 SBC $a0
 STA $22d0
 LDA $22fd
 SBC $a1
 STA $22fe
 CLC
 LDA $232b
 ADC $a2
 STA $232c
 LDA $2359
 ADC $a3
 STA $235a
 jsr point_tail
 iny
 cpy #45
 jmp $98e0
 ert * > $9300
 :($9300-*) dta $ff
point_tail
t_8467
 SEC
t_8468
 LDA #$00
t_846a
 SBC $8b
t_846c
 STA $b5
t_846e
 TXA
t_846f
 AND #$0f
t_8471
 ORA $b6
t_8473
 TAX
t_8474
 LDA $0900,X
t_8477
 STA $23b5,Y
t_847a
 SBC $8c
t_847c
 BCC t_848d
t_847e
 LSR @
t_847f
 ROR $b5
t_8481
 LSR @
t_8482
 ROR $b5
t_8484
 LSR @
t_8485
 ROR $b5
t_8487
 LSR @
t_8488
 ROR $b5
t_848a
 JMP t_849b
t_848d
 LSR @
t_848e
 ROR $b5
t_8490
 LSR @
t_8491
 ROR $b5
t_8493
 LSR @
t_8494
 ROR $b5
t_8496
 LSR @
t_8497
 ROR $b5
t_8499
 EOR #$f0
t_849b
 STA $2388,Y
t_849e
 LDA $b5
t_84a0
 STA $235b,Y
t_84a3
 TXA
t_84a4
 STA $2276,Y
t_84a7
 LDA $232e,Y
t_84aa
 BMI t_84f0
t_84ac
 BNE t_84b5
t_84ae
 LDA $2300,Y
t_84b1
 CMP #$20
t_84b3
 BCC t_84f0
t_84b5
 LDA $22d2,Y
t_84b8
 BPL t_84d9
t_84ba
 SEC
t_84bb
 LDA #$00
t_84bd
 SBC $22a4,Y
t_84c0
 STA $b5
t_84c2
 LDA #$00
t_84c4
 SBC $22d2,Y
t_84c7
 CMP $232e,Y
t_84ca
 BCC t_84ec
t_84cc
 BNE t_84d5
t_84ce
 LDA $b5
t_84d0
 CMP $2300,Y
t_84d3
 BCC t_84ec
t_84d5
 LDA #$40
t_84d7
 BNE t_84f2
t_84d9
 CMP $232e,Y
t_84dc
 BCC t_84ec
t_84de
 BNE t_84e8
t_84e0
 LDA $22a4,Y
t_84e3
 CMP $2300,Y
t_84e6
 BCC t_84ec
t_84e8
 LDA #$20
t_84ea
 BNE t_84f2
t_84ec
 LDA #$00
t_84ee
 BEQ t_84f2
t_84f0
 LDA #$80
t_84f2
 STA $24b4,Y
 rts
 ert * > $9893
 :($9893-*) dta $ff
 jmp entry
 :($98e0-*) dta $ff
 php
 pha
 lda #2
 sta $d500
 ert * <> $98e7
 :($9fff-*) dta $ff
 dta 11
