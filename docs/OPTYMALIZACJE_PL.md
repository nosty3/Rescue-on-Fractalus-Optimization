# Optymalizacje Rescue on Fractalus! — pełny opis aktualnego buildu

Dokument opisuje łącznie zmiany obecne w **v9**, według obszarów kodu, a nie kolejnych wydań. Punktem wejścia do odtworzenia jest [rebuild_current.py](../scripts/rebuild_current.py); źródła MADS są w [src](../src/). Eksperymentalne źródła zachowano dla dalszych badań, lecz o składzie wydania rozstrzyga builder. Nie każdy plik w `src` jest aktywną poprawką.

## Wynik i zakres

Gra działa na Atari XL/XE z 64 KB RAM, na cartridge'u XEGS 128 KB (CART 14), w PAL i NTSC. Nie zmieniono rozdzielczości ani szczegółowości terenu. Zwiększenie ROM zapewnia miejsce na wyspecjalizowany kod i tablice; samo przepakowanie do większego cartridge'a nie przyspiesza gry.

| System | Oryginał | v9 | Zysk |
| --- | ---: | ---: | ---: |
| PAL | 6,4421 FPS | 7,5623 FPS | 17,39% |
| NTSC | 5,8043 FPS | 6,8977 FPS | 18,84% |

Są to średnie ze 155 niezależnych automatycznych lotów na wersję i system. [Metoda i ograniczenia](benchmarks/METODA_PL.md) są wspólne dla obu serii. Poniższe wyniki mikrotestów pochodzą z badań poszczególnych procedur: nie są dodatkowymi pomiarami końcowego FPS i nie wolno sumować ich procentowych zysków.

SHA256 oryginalnego ROM-u: `1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68`.

SHA256 zoptymalizowanego ROM-u: `0c8226e1f58ad26b2a103cbf59c4b8b23fdb87caac0e22f2586a83513a859880`.

## Rasteryzator i powroty z podziału terenu

W procedurze przy `$9937` przestawiono operacje STX/TXA, aby współdzielić potrzebną część wejścia. Skoki po podziale przy `$9A18`, `$9A36` i `$9A52` prowadzą do `$9939`: pomijają powtórne sprawdzenie granicy i zapis niezmienionej wartości `$82`. Oszczędność wynosi 7 cykli na taki powrót. Istotne jest zachowanie semantyki `$82`; bezwarunkowe przesunięcie zapisu byłoby niepoprawne. Źródło: `raster_order.asm` oraz poprawki adresów w builderze.

## Dzielenie całkowitoliczbowe

Procedura pod `$8224` utrzymuje starszą część reszty w akumulatorze, ograniczając dostęp do RAM i liczbę skoków. Implementacja zajmuje 224 bajty. Dalsza zmiana kieruje wejście do `$8235` zamiast `$8231`, omijając zbędną normalizację przy spełnionych warunkach wywołania. Zachowano dokładny iloraz, w tym obsługę dzielnika zero; analizowany zakres zwykły to `0 <= N < D < 32768`.

Pola robocze `$AE..$B1` nie muszą po powrocie zawierać identycznych, znormalizowanych danych, ponieważ nie są dalej używane jako wynik. To celowy wyjątek od porównania całej pamięci, a nie zgoda na dowolne różnice. Pierwsze 50 042 przypadki wykazały 13,57% oszczędności cykli procedury. Kolejna weryfikacja obejmowała 20 033 przypadki, 58 scen i 232 warianty z VBI; w badanym zestawie oszczędzono 176 642 cykle. Źródła: `division_fast.asm`, `opt14_division.asm`.

## Generowanie profilu gór

W banku 5 rozdzielono obsługę ośmiu głębokości podziału. Znane indeksy zastąpiono adresami strony zerowej, usunięto powtarzane obliczenia i wykorzystano stałe własności Y oraz przeniesienia. Dla szerokości 3, a następnie 4 i 5 przy głębokościach 1–4, zastosowano krótsze ścieżki. Pozostałe przypadki korzystają ze ścieżki ogólnej.

Specjalizacje zachowują zaokrąglenia, przeniesienia i flagę V przy prawej krawędzi; nie zastępują matematyki terenu przybliżeniem. Testy obejmowały 58 scen oraz serie 5000, 5000 i 6000 przypadków. Źródła: `mountain_cull.asm`, `opt14_width45.asm`; szczegółowe rozpoznanie procedury zachowano w [badaniu profilu gór](terrain/PROFIL_GOR_PL.txt).

### Pomijanie całkowicie zasłoniętych podziałów

Pomijanie oparto na zachowawczej granicy wysokości wszystkich przyszłych punktów, a nie tylko końców odcinka. Dla szerokości `w` użyto granicy:

```
E(w) = 0                                      dla w <= 2
E(w) = floor(w/4) + 1 + max(E(floor(w/2)), E(ceil(w/2)))
Hmax = min(255, max(wysokość_lewa, wysokość_prawa) + E(w))
```

Podział można pominąć wyłącznie wtedy, gdy profil zasłaniający w każdej objętej kolumnie ekranu jest co najmniej tak wysoki jak `Hmax`. Zachowano warunki dla granic ekranu. Różnice w martwej części stosu są dopuszczalne; testy z celowo zmienianą zawartością nieużywanej pamięci sprawdzały, czy nie staje się ona później wejściem obliczeń.

## Kasowanie bufora obrazu

Oryginalne wejście `$9214` wykonuje 44 zapisy na każdą z 42 kolumn. Dla dwóch typowych wartości X utworzono bezpośrednie zapisy 1848 bajtów oraz 32 bajtów krawędzi: bank 6 dla X=3 i bank 8 dla X=51. Nietypowe X nadal obsługuje oryginalna pętla. Zachowano A, X, Y, flagi i `$94` zgodnie z kontraktem procedury.

Koszt typowego wywołania spadł z 9792 do 7586 lub 7590 cykli, już z przełączaniem banków. Przetestowano 456 przypadków, w tym wszystkie wartości X. Źródła: `clear128_entry.asm`, `clear128_bank6.asm`, `clear128_bank8.asm`. Nazwy źródeł i dokładny montaż rozstrzyga builder.

## Wypełnianie terenu

Pierwszy wiersz zachowuje semantykę oryginału. W kolejnych wierszach sprawdzenie OR czterech bajtów pozwala ominąć grupy zerowe; dla pozostałych danych pozostaje ścieżka ogólna. Samo założenie, że wystarczy patrzeć na horyzont, okazało się niewystarczające i nie weszło do końcowego algorytmu.

Kod w banku 9 zastępuje wielokrotne wyliczanie adresu `$1010 + 96*r` wyspecjalizowanymi adresami i dostępem absolutnym indeksowanym Y. Odtwarza `$80/$81`, przeniesienia i warunki wyjścia. Zachowuje szczególne maski `$95=0`, `$96=$55` i tablice `$3A00/$3B00`. Początki 0–32 mają specjalizacje, 33–48 ścieżkę ogólną; długości 1–48 są rozwinięte, a 49 i więcej mają fallback zamiast obcięcia dołu obrazu. Bank przełączany jest raz na procedurę.

Weryfikacja objęła 58 scen, 256 losowych bitmap i 56 przypadków granicznych, w tym długości do 69. W zestawie porównawczym koszt spadł z 774 828 do 718 543 cykli. Aktywne źródła: `fill_final.asm`, `fill_rows.asm`. Wcześniejsze warianty `fill_zero` i `fill_first` są materiałem badawczym.

## Geometria: od interpreterów do wyspecjalizowanego kodu

Cztery tablice po 45 poleceń pod `$9A55`, `$9A82`, `$9AAF` i `$9ADC` zastąpiono programami w bankach 10–13. Klasyfikację punktów 0–32 rozwinięto z użyciem stałych adresów; punkty 33–44 współdzielą kod, aby zmieścić bank w 8 KB. Tablice pod `$9D00/$9E00` zastępują przesunięcia o cztery bity. Niezmienną wartość `$8B` oblicza się raz; `$9F` zachowuje się na stosie.

Wejście z banku 2 pod `$835E` prowadzi do `$9863`. Przełączenie banku przy `$9890` kontynuuje przy `$9893`, a wyjście prowadzi przez `$98E0`, bank 2 pod `$98E7` i `$84FD`. Weryfikacja obejmowała kontrolę aktywnego banku, przeniesienia, znaków i zaokrągleń. Oszczędności kolejnych etapów wyniosły w 58 scenach 82 736 i dalsze 70 336 cykli. Dodatkowo porównano 1000 losowych przypadków i rzeczywiste wywołania w emulatorze. Aktualne źródła końcowe: `opt14_geometry_entry.asm`, `v7_geometry_bank10.asm` do `v7_geometry_bank13.asm`.

## Przycinanie do ekranu

Wejście `$963D` przekierowano do `$8380` w banku 2. Szybka ścieżka rozpoznaje przypadki z X=0 i zerowymi starszymi bajtami współrzędnych, sprawdza porządek oraz lewą granicę i rozstrzyga rysowanie lub odrzucenie. Przypadki mieszane wracają do oryginalnego algorytmu: odtwarzają pominiętą pierwszą normalizację i kontynuują przy `$9648`.

Zachowano wyjścia `$972E`, `$974A`, `$9788`, `$9797` oraz robocze `$9F/$B5`. Testy 3000 losowych przypadków i 58 scen wykazały zgodność; oszczędność badanego zestawu wyniosła 105 365 cykli. Źródło: `v7_clipping.asm`.

## Interpolacja i samomodyfikacja w RAM

Bank 14 zawiera 16 stron tablic wkładów arytmetycznych oraz tablicę przesunięcia o cztery bity. Wynik zachowuje dokładne zaokrąglenia oryginału. Kod RAM pod `$7EEB..$7FC1`, z procedurą przy `$7F20`, modyfikuje osiem operandów instrukcji, dzięki czemu następne odczyty mają gotowe adresy. Wszystkie te operandy ustawia się przed użyciem.

Kod ładowany jest z banku 1. Nie wymaga dodatkowego RAM ponad dostępny obszar gry. DLI nie korzysta z tej procedury, a VBI przywraca aktywny bank. Samo SEI nie zabezpieczałoby przed NMI — bezpieczeństwo wynika z kontraktu przerwań i bankowania. W 5000 losowych przypadkach, także z zatrutą pamięcią roboczą, uzyskano zgodność. Koszt wynosił 314–339 cykli, średnio 326,4432, z bankowaniem. Źródła: `opt14_interpolation_bank14.asm`, `opt14_interpolation_ram.asm`. Należy zaczynać zimnym startem, aby RAM zawierał właściwy kod.

## Dźwięk i drobne pętle logiki

Rozwinięto 12-iteracyjne pętle wyboru minimum/maksimum miksera przy `$BB19/$BB3E`. Pomocniki zajmują 322 i 344 bajty, wykorzystują bank 2 oraz skoki z banku stałego; nie dodają osobnego bankowania dla każdej operacji dźwięku. Zachowano kolejność rozstrzygania równych wartości i stan kanałów. Oszczędność wywołania wynosiła odpowiednio 65–76 i 53–54 cykle.

Flagę `$0718` zeruje się na początku, a potem po obsłużonym zdarzeniu, z wyjątkiem końcowego kanału. Usuwa to 13 zbędnych zapisów w przypadku bez zdarzeń; przy wielu zdarzeniach narzut może być większy. Zmiana nie jest gwarancją przyspieszenia każdej ścieżki.

Porównano 6000 przypadków miksera, 5800 flag, 400 scenariuszy syntetycznych i 1160 wywołań scen. W badaniu 271 zapisów POKEY zachowano ich wartości i kolejność; nie oznacza to identycznego czasu każdej próbki audio. Źródła: `lowlevel_sound_minimum.asm`, `lowlevel_sound_maximum.asm`, `lowlevel_sound_flag.asm`.

## PMG: rysowanie, kasowanie i pasek wskaźnika

Pętle trzech i pięciu wierszy rozwinięto, a kopiowanie 21 wierszy wykonuje po trzy wiersze na iterację. Pasek obsługiwany przy `$A55C` aktualizuje tylko zmieniony odcinek. Dla starej wartości zero oraz wartości spoza 0–55 pozostaje pełne odrysowanie; jest to istotne m.in. podczas inicjalizacji 0→29.

Pomocniki w banku 2 zajmują `$83CA..$8470` i `$84B0..$84F3`, bez kolizji z clippingiem `$8380..$83C9`, synchronizacją `$84A0..$84AE` i kontynuacją `$84FD`. Wywołania następują w VBI przy już aktywnym banku 2. Nie dodano nowych zmiennych ani samomodyfikacji do PMG.

Weryfikacja obejmowała 5268 przypadków CPU, 320 kontroli paska, pierwszych 40 rzeczywistych wywołań po starcie, poziomy 10/26 i restarty z banków rozszerzeń. Cały RAM poza martwym stosem oraz rejestry i flagi były zgodne. Historyczny test czterech lotów wykazał około +0,044 FPS względem poprzedniego buildu; nie jest to oddzielna statystyczna estymacja wkładu PMG w aktualnej serii 155 lotów. Źródła: `pmg_short_loops.asm`, `pmg_bar_delta.asm`. [Badania PMG](pmg/) opisują również niewdrożone pomysły.

## Bankowanie i przerwania

Okno `$8000..$9FFF` wybiera się przez `$D500`, a `$A000..$BFFF` pozostaje bankiem stałym. Po rozszerzeniu ROM kopia dawnego banku stałego znajduje się w banku 15; dawny bank 7 nie jest automatycznie wolnym miejscem. Znacznik `$9FFF` ma wartość `$FF` dla banku 2, a dla banków rozszerzeń ich numer. Osłona przy `$BFEA` rozpoznaje numery mniejsze niż 15 i odtwarza bank po VBI.

Trampolina RAM przy `$7FFE` ma operand przekraczający granicę `$8000`, więc jej poprawność zależy od bankowania i osłony przerwania. VBI ekranu tytułowego i START mogą porzucić bieżący kontekst. Sprawdzono restarty z banków 2, 5, 6 i 8–14. Nie usunięto NOP przy `$AE88` ani zapisów WSYNC `$D40A`: są częścią zależności czasowych obrazu.

| Bank | Zastosowanie w zmianach |
| --- | --- |
| 1 | Obraz kodu kopiowanego do RAM |
| 2 | Wejścia, clipping, PMG, dźwięk i synchronizacja |
| 5 | Profil gór i pomijanie zasłoniętych podziałów |
| 6, 8 | Specjalizowane kasowanie bufora |
| 9 | Wypełnianie terenu |
| 10–13 | Wyspecjalizowana geometria |
| 14 | Tablice interpolacji |
| 15 | Bank stały |

## Synchronizacja buforów i artefakt po lewej stronie

Gra zgłasza gotowy bufor flagą `$42` przy `$A34A/$A3AF`. VBI przełącza obraz ANTIC, a następnie kasuje flagę przy `$B518` (wejście `$B516`). Jeżeli główna pętla zacznie kasować bufor przed tym potwierdzeniem, może pisać do nadal wyświetlanej pamięci. Ponieważ kasowanie zaczyna się z lewej strony, objawem jest chwilowy fragment terenu po lewej.

W diagnostyce także oryginał miał wejścia w kasowanie przy oczekującym przełączeniu: 51 ze 120 obserwacji; w jednym z szybszych buildów 18 z 45. Nie są to odsetki widocznych artefaktów ani pomiar ich częstości w całej grze, lecz dowód istnienia ryzykownej kolejności operacji.

Wejście kasowania `$9214` kieruje teraz do `$84A0..$84AE`, które czeka na `$42=0`. Obliczenia geometrii przed tym punktem mogą nadal trwać. Zachowano A/X/Y, flagi i SP; pomocnik chwilowo używa dwóch bajtów stosu. Dla zerowego trybu `$4A` istnieje obejście, aby nie czekać na nieaktywne przełączanie. Źródło: `buffer_sync.asm`.

Przetestowano 256×4 warianty oczekiwania, 240 kasowań przy `$42=0`, zimny start, START i poziomy 10/26. W teście 3000 ciągłych klatek odtworzono stary artefakt; w sprawdzonych kandydatach po poprawce go nie znaleziono. To nie dowód braku każdego możliwego błędu obrazu. Nie należy usuwać oczekiwania tylko po to, aby poprawić wynik FPS: przywróciłoby wyścig buforów.

## Weryfikacja i odtwarzalność

Nowy builder odtwarza aktualny ROM bez starych plików wydań, SDK emulatora i zapisów stanu. Sprawdza SHA256 wyniku, zgodność CAR oraz zastosowanie IPS do oryginału. Wynik odtworzenia po reorganizacji był identyczny bajt w bajt z wydanym v9. [Instrukcja](ODTWORZENIE_PL.md) opisuje wymagania i rozdziela budowanie od historycznych badań.

Mikrotesty CPU porównują określone kontrakty procedur; nie zastępują emulatora z DMA, VBI i DLI. Wczesne pozornie wysokie wyniki rzędu 8–10,7 FPS odrzucono z powodu błędnej trampoliny i nieobsługiwanych instrukcji modelu. W dalszych testach wymagano ścisłej obsługi opkodów i kontroli banku/PC. Profil z limitem 4096 próbek nie jest pełnym licznikiem wszystkich wywołań.

Testy wykonano w modelu CPU i Altirrze headless; nie są certyfikacją wszystkich misji ani testem na fizycznym Atari. Użytkownik potwierdził działanie wydania v9. Aktualne pomiary FPS obejmują automatyczny lot bez sterowania, a nie wszystkie zachowania gry.

## Pomysły zachowane do dalszych badań

Nie wdrażano pozostałych drobnych opcji: wyrównywania stron, mnożenia przy `$7CD6`, dalszej przebudowy skanowania kanałów dźwięku i specjalizacji początków wypełnienia 33–48. Są zachowane w [zestawieniu opcji](research/OPCJE_OPTYMALIZACJI_V5_PL.md), [dalszych kierunkach](research/DALSZE_KIERUNKI_PL.txt) i [audycie PMG](pmg/AUDYT_PMG_PL.md). To hipotezy, nie składniki wydanego ROM-u. Przy dalszych pracach obowiązywał próg szacowanego zysku 0,05 FPS, z osobno zaakceptowanym wyjątkiem dla małej zmiany PMG. Zakończenie obecnych prac nie dowodzi, że osiągnięto absolutne optimum.
