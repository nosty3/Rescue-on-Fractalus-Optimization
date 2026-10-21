# Pierwsza próba optymalizacji PMG na bazie v8

21.10.2026. Eksperyment, nie nowe wydanie. ROM SHA256: `0c8226e1f58ad26b2a103cbf59c4b8b23fdb87caac0e22f2586a83513a859880`.

## Wynik

| Lot | v8 | Próba PMG |
|---|---:|---:|
| straight | 7.513947 | 7.592925 |
| right | 7.742457 | 7.776753 |
| left | 7.844759 | 7.922579 |
| fast_right | 7.781929 | 7.765336 |

Łączny wynik: v8 **7.720697 FPS**, próba **7.764418 FPS**.
Różnica **+0.043721 FPS**, **+0.566%**.
Próg +0,05 FPS: **nieosiągnięty**.
Nie promowano próby do nowego wydania. Zalecanym wydaniem pozostaje v8.

Metoda: suma prezentacji w $B516 podzielona przez sumę czasu PAL,
cztery standardowe scenariusze po co najmniej 3000 ramek, rozgrzewka 50.
Baza to zachowany pomiar v8 z tego samego protokołu i stanów wejściowych.
Nie jest to średnia arytmetyczna czterech FPS. Zmiana szybkości może
zmieniać przebieg lotu; pojedyncza seria nie daje przedziału ufności.

## Co zmieniono

- Pasek $A55C: aktualizacja różnicowa. Dla spójnego poprzedniego obrazu
  zapisuje |nowa-stara| bajtów zamiast 57. Przy starej wartości zero lub
  wartościach poza zakresem 0..55 używa oryginalnego pełnego odrysowania.
  Stara wartość zero obejmuje inicjalizację po zerowaniu stanu $2830..$28D5.
  Gdy obie wartości są równe, oryginalne pominięcie aktualizacji pozostaje.
- Kopia 21 wierszy: siedem iteracji po trzy wiersze; końcowy licznik $BD=0.
- Kasowanie i kopiowanie 5 wierszy: rozwinięte pętle, zachowane X/Y i $BB.
- Dwie pętle po 3 wiersze pocisku: rozwinięte, zachowane maski innych pocisków.

Kod zajmuje wolne miejsca banku 2: $83CA..$8470 oraz $84B0..$84F3.
Nie narusza clippingu $8380..$83C9, osłony buforów $84A0..$84AE ani
kontynuacji geometrii $84FD. Bez dodatkowego banku i bez nowej zmiennej RAM.
Kod jest wywoływany z VBI, którego istniejąca osłona udostępnia bank 2.
Nie stosowano SMC; te proste warianty go nie wymagają.

## Weryfikacja

- 5268 przypadków CPU: wszystkie 56x56 przejść paska
  ze spójnym poprzednim obrazem, 300 przypadków ścieżki pełnego odrysowania,
  po 600 przypadków trzech pozostałych procedur i 32 zachowane wejścia z gry.
  Zgodność całego RAM poza martwym stosem, GTIA oraz A/X/Y/P/SP.
- 320 wejść do obsługi paska w emulatorze: po 80 po zimnym starcie,
  w podstawowym locie oraz w stanach poziomów 10 i 26. Za każdym razem
  poprzedni niezerowy stan odpowiadał rzeczywistym bajtom paska.
- Zimny start, lot, próby poziomów 10/26, restart z banków rozszerzeń
  i ponowny start: testy przeszły. Niektóre próby kończą się trybem 0,
  więc nie oznaczają nieprzerwanego lotu przez cały test.

W modelu CPU zmieniona kopia 21 wierszy oszczędza 106 cykli na aktywne
wywołanie, obsługa 5 wierszy do 44, a 3 wierszy do 12. Pomijane aktualizacje
nie zyskują. Pasek może być wolniejszy przy dużym skoku: najgorsza różnica
w wyczerpującym teście przejść to 233 cykle więcej. Nie dobierano dalszego
progu przełączania na pełne odrysowanie w ramach tej pierwszej próby.

## Ograniczenia i odtworzenie

Aktualizacja różnicowa zakłada spójność starej wartości i pamięci obrazu.
Testy obejmują wymienione scenariusze, nie każdą możliwą sekwencję rozgrywki.
Stare zewnętrzne save-state'y z niespójnym stanem nie są objęte gwarancją.
Nie testowano fizycznego Atari ani wszystkich wariantów animacji PMG.

Źródła: src/pmg_short_loops.asm, src/pmg_bar_delta.asm.
Budowanie lokalne: python scripts/build_pmg_trial.py, wymaga build/buffer_sync.rom
i MADS w tools/mads/bin/windows_x86_64/mads.exe. Skrypt generuje te źródła.
Testy: scripts/test_pmg_trial.py, scripts/validate_pmg_trial.py,
scripts/stress_pmg_trial.py. Część testów wymaga zachowanych lokalnych stanów.
Binaria eksperymentu: build/pmg_trial.rom i build/pmg_trial.car.
Nie zastąpiono plików v8 w dist.
