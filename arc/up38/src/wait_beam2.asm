; Czekanie przed kasowaniem bufora dla nietypowych X (pętla oryginału $921A); X=3/51 kasują banki 6/8 z wyścigiem z promieniem.
; Stary bufor wolno pisać, gdy VBI już przełączył obraz ($42=0) ALBO gdy promień w tej ramce minął
; ostatni wiersz gór (linia 146, VCOUNT>=73) i jeszcze nie ma VBI (VCOUNT<124): ANTIC już nie czyta
; starego bufora, a najbliższe VBI na pewno przełączy obraz ($42<>0).
; Kontrakt jak w v10.1: zachowane A, X, Y, flagi i SP; dalej jmp $982F.
 opt h-
 org $9FD5
 php
 pha
 lda $4a
 beq ready
wait
 lda $42
 beq ready
 lda $d40b
 cmp #74
 bcc wait
 cmp #124
 bcs wait
ready
 pla
 plp
 jmp $921a
 ert * > $9ff7
