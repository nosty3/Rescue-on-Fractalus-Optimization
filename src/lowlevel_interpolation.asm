; Bank 6 exact interpolation.
 opt h-
 org $8000
 LDA $2800
 ASL @
 ASL @
 ASL @
 ASL @
 STA $61
 LDA $27fe
 AND #$0f
 ORA $61
 TAY
 LDA $0900,Y
 STA $27f0
 INY
 TYA
 AND #$0f
 ORA $61
 TAY
 LDA $0900,Y
 STA $27f1
 CLC
 LDA $61
 ADC #$10
 STA $61
 LDA $27fe
 AND #$0f
 ORA $61
 TAY
 LDA $0900,Y
 STA $27f2
 INY
 TYA
 AND #$0f
 ORA $61
 TAY
 LDA $0900,Y
 STA $27f3
 LDX $27fd
 STX $27fa
 lda #0
 asl $27fa
 bcs b0_0_one
 lsr $27f1
 lsr $27f0
 adc $27f0
 jmp b0_0_done
b0_0_one
 lsr $27f0
 lsr $27f1
 adc $27f1
b0_0_done
 asl $27fa
 bcs b0_1_one
 lsr $27f1
 lsr $27f0
 adc $27f0
 jmp b0_1_done
b0_1_one
 lsr $27f0
 lsr $27f1
 adc $27f1
b0_1_done
 asl $27fa
 bcs b0_2_one
 lsr $27f1
 lsr $27f0
 adc $27f0
 jmp b0_2_done
b0_2_one
 lsr $27f0
 lsr $27f1
 adc $27f1
b0_2_done
 asl $27fa
 bcs b0_3_one
 lsr $27f1
 lsr $27f0
 adc $27f0
 jmp b0_3_done
b0_3_one
 lsr $27f0
 lsr $27f1
 adc $27f1
b0_3_done
 asl $27fa
 bcs b0_4_one
 lsr $27f1
 lsr $27f0
 adc $27f0
 jmp b0_4_done
b0_4_one
 lsr $27f0
 lsr $27f1
 adc $27f1
b0_4_done
 asl $27fa
 bcs b0_5_one
 lsr $27f1
 lsr $27f0
 adc $27f0
 jmp b0_5_done
b0_5_one
 lsr $27f0
 lsr $27f1
 adc $27f1
b0_5_done
 asl $27fa
 bcs b0_6_one
 lsr $27f1
 lsr $27f0
 adc $27f0
 jmp b0_6_done
b0_6_one
 lsr $27f0
 lsr $27f1
 adc $27f1
b0_6_done
 asl $27fa
 bcs b0_7_one
 lsr $27f1
 lsr $27f0
 adc $27f0
 jmp b0_7_done
b0_7_one
 lsr $27f0
 lsr $27f1
 adc $27f1
b0_7_done
 sta $27f4
 stx $27fa
 lda #0
 asl $27fa
 bcs b1_0_one
 lsr $27f3
 lsr $27f2
 adc $27f2
 jmp b1_0_done
b1_0_one
 lsr $27f2
 lsr $27f3
 adc $27f3
b1_0_done
 asl $27fa
 bcs b1_1_one
 lsr $27f3
 lsr $27f2
 adc $27f2
 jmp b1_1_done
b1_1_one
 lsr $27f2
 lsr $27f3
 adc $27f3
b1_1_done
 asl $27fa
 bcs b1_2_one
 lsr $27f3
 lsr $27f2
 adc $27f2
 jmp b1_2_done
b1_2_one
 lsr $27f2
 lsr $27f3
 adc $27f3
b1_2_done
 asl $27fa
 bcs b1_3_one
 lsr $27f3
 lsr $27f2
 adc $27f2
 jmp b1_3_done
b1_3_one
 lsr $27f2
 lsr $27f3
 adc $27f3
b1_3_done
 asl $27fa
 bcs b1_4_one
 lsr $27f3
 lsr $27f2
 adc $27f2
 jmp b1_4_done
b1_4_one
 lsr $27f2
 lsr $27f3
 adc $27f3
b1_4_done
 asl $27fa
 bcs b1_5_one
 lsr $27f3
 lsr $27f2
 adc $27f2
 jmp b1_5_done
b1_5_one
 lsr $27f2
 lsr $27f3
 adc $27f3
b1_5_done
 asl $27fa
 bcs b1_6_one
 lsr $27f3
 lsr $27f2
 adc $27f2
 jmp b1_6_done
b1_6_one
 lsr $27f2
 lsr $27f3
 adc $27f3
b1_6_done
 asl $27fa
 bcs b1_7_one
 lsr $27f3
 lsr $27f2
 adc $27f2
 jmp b1_7_done
b1_7_one
 lsr $27f2
 lsr $27f3
 adc $27f3
b1_7_done
 sta $27f5
 lda $27ff
 sta $27fb
 lda #0
 asl $27fb
 bcs b2_0_one
 lsr $27f5
 lsr $27f4
 adc $27f4
 jmp b2_0_done
b2_0_one
 lsr $27f4
 lsr $27f5
 adc $27f5
b2_0_done
 asl $27fb
 bcs b2_1_one
 lsr $27f5
 lsr $27f4
 adc $27f4
 jmp b2_1_done
b2_1_one
 lsr $27f4
 lsr $27f5
 adc $27f5
b2_1_done
 asl $27fb
 bcs b2_2_one
 lsr $27f5
 lsr $27f4
 adc $27f4
 jmp b2_2_done
b2_2_one
 lsr $27f4
 lsr $27f5
 adc $27f5
b2_2_done
 asl $27fb
 bcs b2_3_one
 lsr $27f5
 lsr $27f4
 adc $27f4
 jmp b2_3_done
b2_3_one
 lsr $27f4
 lsr $27f5
 adc $27f5
b2_3_done
 asl $27fb
 bcs b2_4_one
 lsr $27f5
 lsr $27f4
 adc $27f4
 jmp b2_4_done
b2_4_one
 lsr $27f4
 lsr $27f5
 adc $27f5
b2_4_done
 asl $27fb
 bcs b2_5_one
 lsr $27f5
 lsr $27f4
 adc $27f4
 jmp b2_5_done
b2_5_one
 lsr $27f4
 lsr $27f5
 adc $27f5
b2_5_done
 asl $27fb
 bcs b2_6_one
 lsr $27f5
 lsr $27f4
 adc $27f4
 jmp b2_6_done
b2_6_one
 lsr $27f4
 lsr $27f5
 adc $27f5
b2_6_done
 asl $27fb
 bcs b2_7_one
 lsr $27f5
 lsr $27f4
 adc $27f4
 jmp b2_7_done
b2_7_one
 lsr $27f4
 lsr $27f5
 adc $27f5
b2_7_done
 STA $62
 LSR @
 LSR @
 LSR @
 LSR @
 TAY
 CLC
 ADC $62
 STA $62
 TYA
 LSR @
 ADC $62
 STA $62
 RTS
