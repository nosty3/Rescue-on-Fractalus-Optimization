# Esc: uszkodzenie stosu przy wznowieniu gry

Odtworzono w AltirraBridge headless: oryginał poprawnie przechodzi pauza/wznowienie, v10 po drugim Esc przestaje wykonywać kod gry (w badanej próbie PC=$32B5, BRK). Regresję odtworzono także w v2 (PC=$C1A6, brak kolejnych obrazów).

## Przyczyna

Oryginalna pauza nie jest zwykłą flagą. Kod $AB0A–$AB13 konstruuje na stosie adres pętli $B73A i przechodzi tam przez RTI, pozostawiając kontekst poprzedniego VBI. Drugie Esc obsługuje następne VBI. Wznowienie w $AB1D usuwa osiem bajtów jego kontekstu i wraca do wcześniejszego wywołania.

Ochrona banków wprowadzona w v2 przekierowuje wejście VBI $B46C do $BFDA. Odczytuje znacznik banku spod $9FFF i odkłada go przez PHA. Zwykłe wyjścia przez $BFEA zdejmują ten dodatkowy bajt, ale specjalna ścieżka wznowienia omija to wyjście. Pozostawiono oryginalne LDY #8 pod $AB1D. Tymczasem do usunięcia jest dziewięć bajtów: adres powrotu JSR (2), znacznik banku (1), zachowane rejestry A/X/Y (3) i ramka przerwania P/PC (3). Pozostawiony bajt przesuwa adres odczytywany przez RTS i wykonanie trafia poza właściwy kod.

## Minimalna poprawka robocza

Zmienić operand pod $AB1E z $08 na $09: LDY #8 -> LDY #9. Dla ROM-u 128 KB jest to offset $1EB1E. Pętla kończy się Y=0, późniejsze INY nadal daje Y=1. Nie trzeba zmieniać plottera ani usuwać ochrony banków. Zmiana dotyczy wyłącznie ścieżki wznowienia, nie zwykłego lotu.

Poprawka została włączona do v10.1. Wynikowy CAR jest identyczny z przetestowanym kandydatem. Źródło: `src/pause_resume_stack.asm`; odtwarzanie: `scripts/rebuild_current.py`.

## Sprawdzenie

- `scripts/debug_escape.py`: zimny start oryginału i v10, fizyczne zdarzenia KEYRAW ESC down/up, rejestry i stos przed pauzą oraz po dwóch Esc.
- `scripts/test_escape_fix.py`: odtworzenie błędu w v2 oraz 12 cykli pauza/wznowienie PAL i 12 NTSC na kandydacie.
- Po każdym z 24 wznowień osiągnięto pięć kolejnych prezentacji obrazu pod $B516 z rosnącymi znacznikami czasu. Wszystkie sprawdzenia przeszły.
- Testy obejmują automatyczny lot i różne odstępy między pauzami; nie stanowią pełnej walidacji wszystkich trybów gry i wszystkich faz przerwań. Nie wykonywano nowych pomiarów FPS.

Poprzednia seria wydajności używała neutralnego joysticka i nie naciskała Esc, dlatego nie wykrywała tej regresji.
