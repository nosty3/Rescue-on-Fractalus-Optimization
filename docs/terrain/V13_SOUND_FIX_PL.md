# Naprawa bankowania dźwięku i geometrii v13

Aktualizacja plików z 2026-10-29. Wersja pozostaje **v13**, a istniejące nazwy CAR/ROM/XEX do pobrania zostały zachowane. Odtworzono łatki IPS, manifesty i oczekiwane sumy kontrolne. Eksperyment geometrii nie jest częścią tej aktualizacji.

## Przyczyna i naprawa

Fallback gotowych drzew instalował `STA $D500` w banku 2 pod `$9E50`, nadpisując trzy bajty istniejącej procedury miksera:

```asm
; Poprawny kod miksera
$9E4E CMP $0716
$9E51 BCS $9E5E
```

Nadpisanie zmieniało porównanie na `CMP $8D16`, a skok na `BRK`. Uszkodzony fragment wykonuje się przy zajętym wirtualnym kanale 11 (`$0710 != 0`), zaburzając wybór kanałów dźwiękowych i sygnał pilota.

Pierwsza nieopublikowana poprawka przywróciła mikser, ale umieściła trampolinę pod `$9875`, nadpisując działający dyspozytor geometrii. Awarię podczas skrętu odtworzono w Altirrze na 130XE PAL z 1088 KB RAM. Rzeczywista historia CPU pokazała `$835E -> $9863 -> $9867 BEQ $9876 -> BRK`, a następnie wykonywanie pustego ROM-u i strony zerowej. Ten kandydat został odrzucony.

Poprawiony v13 zachowuje mikser i geometrię. Fallback przełącza teraz bank pod **`$9FEF` w banku 2** i wykonuje kontynuację pod **`$9FF2` w banku 5**. Generator sprawdza oba miejsca jako wolną przestrzeń i chroni obszary miksera oraz geometrii. XEX stosuje odpowiednią relokację i przełączanie PORTB. Każdy poprawiony ROM różni się od początkowego opublikowanego v13 o 14 bajtów; wygenerowane procedury rysowania terenu pozostają bez zmian.

## Walidacja

- Pełna odbudowa ze źródeł przez MADS: obie pary ROM/CAR, XEX i obie łatki IPS są zgodne bajt w bajt z poprawioną dystrybucją.
- `scripts/test_v13_sound_fix.py`, bez prywatnych stanów: wszystkie 256 wejść dyspozytora i 1024 losowe konfiguracje miksera na CAR, porównane z mikserem oryginalnej gry, oraz regresja zajętego kanału 11.
- Tryb `--native` przeszedł cztery zimne starty z niezmienioną mapą: oba rozmiary CAR, PAL/NTSC, 130XE z 1088 KB RAM, długie skręty oraz kontrola rzeczywistego zegara i kończenia renderowania.
- Wcześniejsza walidacja poprawionych obrazów obejmowała 16 dodatkowych zimnych startów tych dwóch CAR-ów: PAL/NTSC, 64/1088 KB, dwa opóźnienia menu, co najmniej 2738 klatek lotu na próbę, wielokrotne skręty po 400 klatek i pauzę/wznowienie.
- Dwa dodatkowe testy CAR używały S, B i PLUS przy przydzielonym kanale 11, a potem długich skrętów. Dwa wydłużone testy XEX obejmowały PAL/NTSC, sterowanie/strzelanie, wielokrotne skręty, kończenie renderowania i pauzę/wznowienie.
- Model CPU dodatkowo odtworzył 4096 wejść miksera, 320 zapisanych wejść VBI, osiem wejść kolejki dźwięku i 40 potoków renderowania na ROM. RAM, rejestry i cykle CPU renderera były zgodne przed/po naprawie; prywatne dane tych odtworzeń nie są wymagane przez publiczny test regresji ani odbudowę.
- Użytkownik potwierdził działanie poprawionego CAR-a 1 MB w swoim emulatorze.

Testy natywne sprawdzają rzeczywisty przyrost zegara, zmianę kierunku i ukończenie renderowania. Sama poprawna odpowiedź FRAME lub znacznik trybu lotu nie wystarczają: znacznik może pozostać ustawiony po awarii.

[Bieżące wyniki walidacji](../../results/v13/validation/sound-fix/) · [Odbudowa](../REBUILD_PL.md)

Nie wykonano nowego benchmarku FPS. Istniejące tabele, wykresy i surowe pomiary opisują obrazy sprzed tej naprawy bankowania. Nie przypisujemy zastąpionym binariom nowego liczbowego wyniku FPS. Nie przeprowadzono pełnego kontrolowanego porównania odstępów pikania z rzeczywistą odległością pilota; regresja miksera/POKEY i testy funkcjonalne potwierdzają opisany zakres, a nie każdy stan gry lub zgodność ze sprzętem fizycznym.
