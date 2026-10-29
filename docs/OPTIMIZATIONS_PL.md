# Optymalizacje Rescue on Fractalus! — pełny opis aktualnego buildu

[English](OPTIMIZATIONS.md) · [Polski](OPTIMIZATIONS_PL.md)

Dokument opisuje łącznie zmiany obecne w **v11**, według obszarów kodu, a nie kolejnych wydań. Punktem wejścia do odtworzenia jest [rebuild_current.py](../scripts/rebuild_current.py); źródła MADS są w [src](../src/). Eksperymentalne źródła zachowano dla dalszych badań, lecz o składzie wydania rozstrzyga builder. Nie każdy plik w `src` jest aktywną poprawką.

## Aktualny renderer v11 i wkład autorów

v11 łączy wcześniejszą implementację nosty/Astry, pracę zespołu Opus Solo w up38 i pięć końcowych zmian Astry. Fable opracował projekcję i pętlę krawędzi w zespole Solo. Historyczne +18% i około +39% opisują etapy, a nie procenty, które można dodawać; końcowe wyniki pomiarów są w README.

### Solo/Opus: widoczność, kasowanie i przerwania

- **Kasowanie zależne od pozycji wiązki:** wejście `$9214` w banku 2 używa ścieżki wait-beam up38. Kasowanie może się rozpocząć, gdy nie czeka prezentacja obrazu albo VCOUNT jest w sprawdzonym zakresie 74–123, po obszarze terenu. Zastępuje to wcześniejsze bezwarunkowe oczekiwanie na potwierdzenie przełączenia bufora opisane niżej; nie pozwala dowolnie pisać po widocznym terenie. Czasy DMA/VBI i odtwarzanie banków pozostają warunkiem poprawności.
- **Odrzucanie zasłoniętych podziałów:** rasteryzator banku 5 pomija podział wyłącznie, gdy zachowawcze ograniczenie wysokości dowodzi zasłonięcia wyniku przez istniejące kolumny. Usuwa pracę rekurencyjną bez zmniejszenia szczegółowości geometrii. Pozostają ścieżki ogólne i zapasowe.
- **Granice kasowania kolumn:** `$0100+kolumna` przechowuje HD, granicę między pewnym czystym niebem a potencjalnie zabrudzonymi pikselami. Banki 6/8 wykonują kasowanie wstępne, 5/8 kasowanie na żądanie, a bank 9 wypełnia potrzebne pasma. Rysowanie obiektów aktualizuje ten sam cache; nie jest to bezwarunkowe pomijanie wszystkich zapisów nieba.
- **VBI:** bank 14 skraca ścieżki milczących kanałów i specjalizuje rysowanie wskaźnika, zachowując ochronę banków. Usuwa zbędną pracę przerwania, a nie zmienia zegara logiki gry.
- **Projekcja/pętla krawędzi (Fable):** bank 3 wykonuje projekcję z dzieleniem inline, bank 2 usprawnia iterację krawędzi i clipping, a bank 14 dostarcza prolog/tablice. Trzeba zachować wygenerowane wyrównanie powrotu i odtwarzanie znaczników banków. Stub banku 2 trafia na sprawdzony RTS w banku odbierającym.

Źródła i generatory: `arc/up38/src/`, `arc/up38/tools/`; oryginalne szczegółowe notatki: [opis techniczny up38](../arc/up38/TECHNICAL_NOTES.md). To składniki budowania, nie drugie aktualne wydanie.

### Astra: pięć końcowych zmian

1. **HD=152 oznacza pełne wyczyszczenie.** Rysowane wysokości kończą się na 151, więc dawny znacznik 151 powodował zbędne wywołania pomocnika dla maksymalnej wysokości. Nowy znacznik usuwa te wywołania; poprawiono inicjalizację i tablice wyboru. Obiekty mogą nadal wytworzyć HD=151, który pozostaje obsługiwany.
2. **Odtwarzanie Y na wspólnych wyjściach.** W specjalizacjach d0–d4 usunięto powtarzane LDY przy pikselach, a wspólne DEY zastąpiono LDY ze znaną wartością końcową. Ścieżka ogólnej rekurencji i inne liście zachowują wymagane zachowanie.
3. **Kasowanie na żądanie we współrzędnych wysokości.** Banki 5 i 8 używają bezpośrednio HD/h. Odwrócone tablice skoków i porównania usuwają konwersje do numerów wierszy, zachowując zaokrąglanie granic oraz przypadki 151/152.
4. **Próg zasłaniania w akumulatorze.** Skany o0–o4 zachowują Hmax−1 w A, zastępują pary LDA/CMP instrukcjami CMP z pamięcią, odwracają warunek skoku i przesuwają X czterema INX. Ograniczenie szerokości gwarantuje Hmax>0. Skrótu nie stosuje się do ogólnego przypadku zerowej granicy.
5. **Wypełnianie bezpośrednio z HD.** Bank 9 używa odwróconego indeksowania i porównań zamiast ponownie liczyć D=152−HD; obraz jest zgodny w sprawdzonych kontraktach.

Aktualne źródła pełnych banków MADS: `src/v11/raster5.asm`, `sky_b6.asm`, `sky_b8.asm`, `sky_b9.asm`. ROM nadal ma 128 KB, a kartridż potrzebuje tylko 64 KB RAM. Te pięć zmian nie wymaga nowego banku ani dodatkowego RAM-u.

### XEX z rozszerzoną pamięcią i poprawka ukończenia poziomu

Loader Solo przenosi kod rezydentny `$4000–$7FFF` do `$8000–$BFFF`, a kod okna kartridża i banku stałego mapuje do okna rozszerzonego RAM-u PORTB `$4000–$7FFF`. Mapowanie zachowuje młodsze bajty i granice stron. Wymaga 16 różnych banków rozszerzenia (320 KB Rambo, 576 KB albo 1088 KB), zachowuje ROM systemu i wyłącza BASIC. Cztery zmienione banki są asemblowane bezpośrednio pod ten układ; pozostałe korzystają z wcześniejszych decyzji relokacji.

Dostarczona relokacja pominęła wskaźniki melodii banku 0 `$57D3` i `$57D9`: `$57FB/$57DF` trzeba zmienić na `$97FB/$97DF`. Bez poprawki melodia końca poziomu czytała niewłaściwe dane bankowe, a pętla czekała w XEX pod `$867B` na wyzerowanie `$0655`. v11 poprawia oba słowa, zmieniając dokładnie dwa bajty wcześniejszego XEX kandydata. CAR/ROM nie zmieniają się. [Pełna diagnoza i regresja](research/XEX_LEVEL_TRANSITION_FIX_PL.txt).

### Dowody i ograniczenia

Pięć końcowych zmian przeszło 320 porównań renderera, 5000 losowych segmentów, 300 przypadków obiektów, 11880 przypadków pomocników kasowania oraz testy pauzy i rozrywania obrazu w emulatorze. Oszczędności 1,51–4,88% cykli scen nie są FPS całej gry. Pełne loty wykazały dodatkowe 1,58% PAL / 1,78% NTSC względem up38 przy locie prosto i 4,97% / 5,27% z nurkowaniem. Zysk zbiorczy oryginał–v11 wynosi 40,04% PAL / 43,13% NTSC.

Poprawiony XEX przeszedł 12 kontrolowanych scenariuszy zmiany poziomu (dwa standardy, trzy wielkości pamięci, komplet lub komplet+1) i sześć konfiguracji testów działania. Scenariusze przejścia ustawiają dane powrotu/pilotów, a następnie wykonują zwykły kod punktacji, melodii i zmiany poziomu; nie są to pełne misje rozegrane ręcznie. Użytkownik także potwierdził działanie poprawionego XEX. Nie deklarujemy osobnego pełnego benchmarku FPS XEX ani pełnej certyfikacji sprzętowej.


Poniższe sekcje opisują odziedziczoną podstawę; szczegóły kasowania/synchronizacji i układu banków zastąpione przez aktualny renderer wskazano powyżej.

## Poprawka Esc w v10.1

Wznowienie gry pod $AB1D usuwa teraz dziewięć zamiast ośmiu bajtów stosu. Dodatkowy bajt jest znacznikiem banku odkładanym przez ochronę VBI wprowadzoną w v2. Ścieżka wznowienia omijała normalne odtworzenie banku, co uszkadzało adres powrotu. Źródło MADS: `src/pause_resume_stack.asm`; builder nakłada poprawkę po plotterze. ROM różni się od v10 wyłącznie bajtem pod offsetem $1EB1E ($08 → $09).

Kandydat identyczny z wydaniem przeszedł 12 cykli pauza/wznowienie PAL i 12 NTSC; po każdym potwierdzono pięć kolejnych obrazów. Wyniki FPS poniżej dotyczą v10; dla v10.1 nie wykonywano nowych pomiarów. [Diagnoza](research/ESC_DIAGNOSIS_PL.md).

## Wynik i zakres

Gra działa na Atari XL/XE z 64 KB RAM, na cartridge'u XEGS 128 KB (CART 14), w PAL i NTSC. Nie zmieniono rozdzielczości ani szczegółowości terenu. Zwiększenie ROM zapewnia miejsce na wyspecjalizowany kod i tablice; samo przepakowanie do większego cartridge'a nie przyspiesza gry.

| System | Oryginał | v10 | Przyrost do oryginału |
| --- | ---: | ---: | ---: |
| PAL | 6,4421 FPS | 7,6359 FPS | **+18,53%** |
| NTSC | 5,8043 FPS | 6,9377 FPS | **+19,53%** |

Są to średnie ze 155 niezależnych automatycznych lotów na wersję i system. [Metoda i ograniczenia](benchmarks/METHOD_PL.md) są wspólne dla obu serii. Poniższe wyniki mikrotestów pochodzą z badań poszczególnych procedur: nie są dodatkowymi pomiarami końcowego FPS i nie wolno sumować ich procentowych zysków.

SHA256 oryginalnego ROM-u: `1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68`.

SHA256 zoptymalizowanego ROM-u: `afa04d6802a03333516936b4912f8f7abf23a1837362ac2b0ceaa83b6b6414da`.

## Rasteryzator i powroty z podziału terenu

W procedurze przy `$9937` przestawiono operacje STX/TXA, aby współdzielić potrzebną część wejścia. Skoki po podziale przy `$9A18`, `$9A36` i `$9A52` prowadzą do `$9939`: pomijają powtórne sprawdzenie granicy i zapis niezmienionej wartości `$82`. Oszczędność wynosi 7 cykli na taki powrót. Istotne jest zachowanie semantyki `$82`; bezwarunkowe przesunięcie zapisu byłoby niepoprawne. Źródło: `raster_order.asm` oraz poprawki adresów w builderze.

## Tablice adresów wierszy plottera i zapisy Y

Bank 5 korzysta z dwóch 48-bajtowych tablic ROM pod $9768 i $97A8. Dla wysokości Y=104..151 adres wiersza wynosi $1010+96*(151-Y). Efektywne podstawy odczytu $9700 i $9740 eliminują przekroczenia strony pamięci. Ogólne ścieżki, w tym nietypowe wysokości, zachowują oryginalne tablice RAM.

Usunięto 48 instrukcji STY $B5 w wyspecjalizowanych ścieżkach, w których Y i tak odtwarzane jest instrukcją LDY ze stałą głębokością. Nie zmieniono liczby przełączeń banków ani synchronizacji buforów. Źródło: `v10_plotter.asm`.

W zestawie 58 scen oszczędzono średnio 1248,09 cyklu na renderowanie i wypełnienie. Przeszło również 6000 losowych odcinków, 309 przypadków brzegowych i 232 kontrole VBI. B5 po rendererze, a B4/B5 po dalszej geometrii mogą różnić się jako dane pomocnicze nieużywane przez dalsze badane obliczenia; martwy stos pomijano. Rejestry i flagi na badanych wyjściach pozostają zgodne. Zakres i ograniczenia testów, wraz z pełnym pomiarem FPS, opisuje [raport v10](benchmarks/V10_REPORT_PL.md).

## Dzielenie całkowitoliczbowe

Procedura pod `$8224` utrzymuje starszą część reszty w akumulatorze, ograniczając dostęp do RAM i liczbę skoków. Implementacja zajmuje 224 bajty. Dalsza zmiana kieruje wejście do `$8235` zamiast `$8231`, omijając zbędną normalizację przy spełnionych warunkach wywołania. Zachowano dokładny iloraz, w tym obsługę dzielnika zero; analizowany zakres zwykły to `0 <= N < D < 32768`.

Pola robocze `$AE..$B1` nie muszą po powrocie zawierać identycznych, znormalizowanych danych, ponieważ nie są dalej używane jako wynik. To celowy wyjątek od porównania całej pamięci, a nie zgoda na dowolne różnice. Pierwsze 50 042 przypadki wykazały 13,57% oszczędności cykli procedury. Kolejna weryfikacja obejmowała 20 033 przypadki, 58 scen i 232 warianty z VBI; w badanym zestawie oszczędzono 176 642 cykle. Źródła: `division_fast.asm`, `opt14_division.asm`.

## Generowanie profilu gór

W banku 5 rozdzielono obsługę ośmiu głębokości podziału. Znane indeksy zastąpiono adresami strony zerowej, usunięto powtarzane obliczenia i wykorzystano stałe własności Y oraz przeniesienia. Dla szerokości 3, a następnie 4 i 5 przy głębokościach 1–4, zastosowano krótsze ścieżki. Pozostałe przypadki korzystają ze ścieżki ogólnej.

Specjalizacje zachowują zaokrąglenia, przeniesienia i flagę V przy prawej krawędzi; nie zastępują matematyki terenu przybliżeniem. Testy obejmowały 58 scen oraz serie 5000, 5000 i 6000 przypadków. Źródła: `mountain_cull.asm`, `opt14_width45.asm`; szczegółowe rozpoznanie procedury zachowano w [badaniu profilu gór](terrain/MOUNTAIN_PROFILE_PL.txt).

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

Nowy builder odtwarza aktualny ROM bez starych plików wydań, SDK emulatora i zapisów stanu. Sprawdza SHA256 wyniku, zgodność CAR oraz zastosowanie IPS do oryginału. Builder sprawdza etap v9, a następnie końcowy ROM v11, CAR, XEX i IPS bajt w bajt. [Instrukcja](REBUILD_PL.md) opisuje wymagania i rozdziela budowanie od historycznych badań.

Mikrotesty CPU porównują określone kontrakty procedur; nie zastępują emulatora z DMA, VBI i DLI. Wczesne pozornie wysokie wyniki rzędu 8–10,7 FPS odrzucono z powodu błędnej trampoliny i nieobsługiwanych instrukcji modelu. W dalszych testach wymagano ścisłej obsługi opkodów i kontroli banku/PC. Profil z limitem 4096 próbek nie jest pełnym licznikiem wszystkich wywołań.

Testy wykonano w modelu CPU i Altirrze headless; nie są certyfikacją wszystkich misji ani testem na fizycznym Atari. Użytkownik potwierdził działanie wydania v9. Aktualne pomiary FPS obejmują lot prosto oraz okresowe nurkowanie, a nie wszystkie zachowania gry.

## Pomysły zachowane do dalszych badań

Nie wdrażano pozostałych drobnych opcji: wyrównywania stron, mnożenia przy `$7CD6`, dalszej przebudowy skanowania kanałów dźwięku i specjalizacji początków wypełnienia 33–48. Są zachowane w [zestawieniu opcji](research/V5_OPTIMIZATION_OPTIONS_PL.md), [dalszych kierunkach](research/FUTURE_DIRECTIONS_PL.txt) i [audycie PMG](pmg/PMG_AUDIT_PL.md). To hipotezy, nie składniki wydanego ROM-u. Przy dalszych pracach obowiązywał próg szacowanego zysku 0,05 FPS, z osobno zaakceptowanym wyjątkiem dla małej zmiany PMG. Zakończenie obecnych prac nie dowodzi, że osiągnięto absolutne optimum.

Dodatkowe badanie cache wyboru kanałów miksera odrzucono: po uwzględnieniu zapisów z RAM oszczędność wewnątrz miksera wynosiła średnio tylko 14,63 cyklu/VBI przed odjęciem narzutu poza nim. Eksperyment nie wchodzi do v10. Podobnie nie włączono nowych skrótów skalowania perspektywy.


## v12: dalsze dokładne optymalizacje 128 KB

Skrót fill `$AA`, wcześniejszy test zasłaniania, tablica liczby grup, próg skanu w A, dalsze usunięcie obsługi Y w d0–d4 z odtworzeniem Y=5 oraz grupowanie geometrii 33–44 rozwijają pomysły ilmenita i Astry. Obraz pozostaje dokładny. Pełny wynik 50/50: 8,9329 FPS PAL (+42,43% względem oryginału) i 8,1499 FPS NTSC (+45,75%). Składowych oszczędności nie przedstawiamy jako niezależnie zmierzonych przyrostów FPS. [Badanie](research/V12_RESEARCH_PL.md) i [pełny test](benchmarks/V12_REPORT_PL.md).


## v13: dokładne drzewa szerokości i rozszerzony XEX

Na bazie v12 gotowe drzewa usuwają obliczenia środkowego X i sterowanie przejściem dla wybranych szerokości i clippingu. 512 KB ma 46 specjalizacji w 47 bankach; 1 MB — 86 w 111. Pozostałe przypadki obsługuje dokładny fallback v12. Zapisy pikseli uwzględniają HD/lazy clear; konserwatywne testy i przejścia banków z zachowaniem A/P zachowują obraz. Powyższe opisy bazowe dokumentują rozwój kodu nadal używanego w fallbacku i innych procedurach; opis stałego banku 15 dotyczył etapu 128 KB. Aktualny fizyczny stały bank to 63/127.

XEX wariantu 512 KB używa 62 stron po 16 KB na rozszerzeniu 1 MB (1088 KB łącznie). Prawidłowe PORTB poniżej $80 wymagają strażnika VBI akceptującego niezerowe znaczniki; zero oznacza bank 2. Loader sprawdza 64 niezależne strony i zachowuje poprawki Esc oraz melodii końca poziomu. Cartridge 1 MB przekracza pojemność tego układu stron; nie dostarczamy jego XEX. Oba cartridge’e wymagają tylko 64 KB RAM.

[Implementacja i walidacja](terrain/COMPILED_TREES_PL.md), [pełne pomiary](benchmarks/V13_REPORT_PL.md), [pomysły ilmenita](ILMENIT_IDEAS_PL.md). Bieżące źródła banków to src/v12 i generatory src/v13; starsze etapy pozostają potrzebne do odbudowy.
