; Bank 2 $984C-$9853 (dziura FF): lądowanie rzadkiej ścieżki widoczności z banku 3 i wejście rzutowania.
; Generuje tools/gen_fable.py.
 opt h-
 org $984c
 jmp $8af8
 lda #3
 sta $d500
 jmp $85d4
 ert * <> $9857
