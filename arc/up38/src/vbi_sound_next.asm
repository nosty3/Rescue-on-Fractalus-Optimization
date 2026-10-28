; Bank 2, $984C (dziura FF nosty3 za wrapperem kasowania): następny kanał dźwięku po oryginalnej obsłudze.
; Stały bank $B9AD (`jmp $b92b`, koniec iteracji pętli kanałów, Y już zmniejszone i <> 0) skacze tutaj.
; Oryginał dla bezczynnego kanału ($06DB,Y = $06A3,Y = 0) przy $0718 = 0 robi tylko `dey`; tu to samo
; w ciasnej pętli. Aktywny kanał albo $0718 <> 0 -> oryginał $B92B z tym samym Y; koniec (Y=0) -> $B9B0.
; Rozdzielenie Y<>0 / Y=0 robi vbi_sound_exit.asm ($9885).
 opt h-
 org $984c
 lda $0718
 bne done
fast
 lda $06db,y
 ora $06a3,y
 bne done
 dey
 bne fast
done
 jmp $9885
 ert * > $9860
