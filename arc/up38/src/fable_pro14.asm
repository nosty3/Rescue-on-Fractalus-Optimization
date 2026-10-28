; Bank 14: rozwinięty prolog rysowania terenu (tabela kolumn $3920-$39D7, tabela $270E-$272D). Generuje
; tools/gen_fable.py. Wejście z banku 3 (hop14) przez jmp $9950, X = $30 albo 0; powrót: jmp hop14 w banku 14 =
; lda #3 / sta $D500, dalej bank 3 pod hop14+5.
 opt h-
 org $9950
 txa
 sta $3920
 sta $3921
 sta $3922
 sta $3923
 inx
 txa
 sta $3924
 sta $3925
 sta $3926
 sta $3927
 inx
 txa
 sta $3928
 sta $3929
 sta $392a
 sta $392b
 inx
 txa
 sta $392c
 sta $392d
 sta $392e
 sta $392f
 inx
 txa
 sta $3930
 sta $3931
 sta $3932
 sta $3933
 inx
 txa
 sta $3934
 sta $3935
 sta $3936
 sta $3937
 inx
 txa
 sta $3938
 sta $3939
 sta $393a
 sta $393b
 inx
 txa
 sta $393c
 sta $393d
 sta $393e
 sta $393f
 inx
 txa
 sta $3940
 sta $3941
 sta $3942
 sta $3943
 inx
 txa
 sta $3944
 sta $3945
 sta $3946
 sta $3947
 inx
 txa
 sta $3948
 sta $3949
 sta $394a
 sta $394b
 inx
 txa
 sta $394c
 sta $394d
 sta $394e
 sta $394f
 inx
 txa
 sta $3950
 sta $3951
 sta $3952
 sta $3953
 inx
 txa
 sta $3954
 sta $3955
 sta $3956
 sta $3957
 inx
 txa
 sta $3958
 sta $3959
 sta $395a
 sta $395b
 inx
 txa
 sta $395c
 sta $395d
 sta $395e
 sta $395f
 inx
 txa
 sta $3960
 sta $3961
 sta $3962
 sta $3963
 inx
 txa
 sta $3964
 sta $3965
 sta $3966
 sta $3967
 inx
 txa
 sta $3968
 sta $3969
 sta $396a
 sta $396b
 inx
 txa
 sta $396c
 sta $396d
 sta $396e
 sta $396f
 inx
 txa
 sta $3970
 sta $3971
 sta $3972
 sta $3973
 inx
 txa
 sta $3974
 sta $3975
 sta $3976
 sta $3977
 inx
 txa
 sta $3978
 sta $3979
 sta $397a
 sta $397b
 inx
 txa
 sta $397c
 sta $397d
 sta $397e
 sta $397f
 inx
 txa
 sta $3980
 sta $3981
 sta $3982
 sta $3983
 inx
 txa
 sta $3984
 sta $3985
 sta $3986
 sta $3987
 inx
 txa
 sta $3988
 sta $3989
 sta $398a
 sta $398b
 inx
 txa
 sta $398c
 sta $398d
 sta $398e
 sta $398f
 inx
 txa
 sta $3990
 sta $3991
 sta $3992
 sta $3993
 inx
 txa
 sta $3994
 sta $3995
 sta $3996
 sta $3997
 inx
 txa
 sta $3998
 sta $3999
 sta $399a
 sta $399b
 inx
 txa
 sta $399c
 sta $399d
 sta $399e
 sta $399f
 inx
 txa
 sta $39a0
 sta $39a1
 sta $39a2
 sta $39a3
 inx
 txa
 sta $39a4
 sta $39a5
 sta $39a6
 sta $39a7
 inx
 txa
 sta $39a8
 sta $39a9
 sta $39aa
 sta $39ab
 inx
 txa
 sta $39ac
 sta $39ad
 sta $39ae
 sta $39af
 inx
 txa
 sta $39b0
 sta $39b1
 sta $39b2
 sta $39b3
 inx
 txa
 sta $39b4
 sta $39b5
 sta $39b6
 sta $39b7
 inx
 txa
 sta $39b8
 sta $39b9
 sta $39ba
 sta $39bb
 inx
 txa
 sta $39bc
 sta $39bd
 sta $39be
 sta $39bf
 inx
 txa
 sta $39c0
 sta $39c1
 sta $39c2
 sta $39c3
 inx
 txa
 sta $39c4
 sta $39c5
 sta $39c6
 sta $39c7
 inx
 txa
 sta $39c8
 sta $39c9
 sta $39ca
 sta $39cb
 inx
 txa
 sta $39cc
 sta $39cd
 sta $39ce
 sta $39cf
 inx
 txa
 sta $39d0
 sta $39d1
 sta $39d2
 sta $39d3
 inx
 txa
 sta $39d4
 sta $39d5
 sta $39d6
 sta $39d7
 inx
 txa
 clc
 adc #$2e
 sta $b3
 lda $a6
 sta $271e
 ldx #0
 txa
 clc
 adc $a5
 tax
 lda $271e
 adc $a4
 sta $271f
 txa
 clc
 adc $a5
 tax
 lda $271f
 adc $a4
 sta $2720
 txa
 clc
 adc $a5
 tax
 lda $2720
 adc $a4
 sta $2721
 txa
 clc
 adc $a5
 tax
 lda $2721
 adc $a4
 sta $2722
 txa
 clc
 adc $a5
 tax
 lda $2722
 adc $a4
 sta $2723
 txa
 clc
 adc $a5
 tax
 lda $2723
 adc $a4
 sta $2724
 txa
 clc
 adc $a5
 tax
 lda $2724
 adc $a4
 sta $2725
 txa
 clc
 adc $a5
 tax
 lda $2725
 adc $a4
 sta $2726
 txa
 clc
 adc $a5
 tax
 lda $2726
 adc $a4
 sta $2727
 txa
 clc
 adc $a5
 tax
 lda $2727
 adc $a4
 sta $2728
 txa
 clc
 adc $a5
 tax
 lda $2728
 adc $a4
 sta $2729
 txa
 clc
 adc $a5
 tax
 lda $2729
 adc $a4
 sta $272a
 txa
 clc
 adc $a5
 tax
 lda $272a
 adc $a4
 sta $272b
 txa
 clc
 adc $a5
 tax
 lda $272b
 adc $a4
 sta $272c
 txa
 clc
 adc $a5
 tax
 lda $272c
 adc $a4
 sta $272d
 ldx #0
 txa
 sec
 sbc $a5
 tax
 lda $271e
 sbc $a4
 sta $271d
 txa
 sec
 sbc $a5
 tax
 lda $271d
 sbc $a4
 sta $271c
 txa
 sec
 sbc $a5
 tax
 lda $271c
 sbc $a4
 sta $271b
 txa
 sec
 sbc $a5
 tax
 lda $271b
 sbc $a4
 sta $271a
 txa
 sec
 sbc $a5
 tax
 lda $271a
 sbc $a4
 sta $2719
 txa
 sec
 sbc $a5
 tax
 lda $2719
 sbc $a4
 sta $2718
 txa
 sec
 sbc $a5
 tax
 lda $2718
 sbc $a4
 sta $2717
 txa
 sec
 sbc $a5
 tax
 lda $2717
 sbc $a4
 sta $2716
 txa
 sec
 sbc $a5
 tax
 lda $2716
 sbc $a4
 sta $2715
 txa
 sec
 sbc $a5
 tax
 lda $2715
 sbc $a4
 sta $2714
 txa
 sec
 sbc $a5
 tax
 lda $2714
 sbc $a4
 sta $2713
 txa
 sec
 sbc $a5
 tax
 lda $2713
 sbc $a4
 sta $2712
 txa
 sec
 sbc $a5
 tax
 lda $2712
 sbc $a4
 sta $2711
 txa
 sec
 sbc $a5
 tax
 lda $2711
 sbc $a4
 sta $2710
 txa
 sec
 sbc $a5
 tax
 lda $2710
 sbc $a4
 sta $270f
 txa
 sec
 sbc $a5
 tax
 lda $270f
 sbc $a4
 sta $270e
 stx $b5
 jmp $9d80
 ert * > $9d80
 :($9d80-*) dta $ff
 lda #3
 sta $d500
 jmp $9950
 ert * > $9dff
