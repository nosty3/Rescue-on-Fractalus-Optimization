# NTSC: pomiar główny — świeży proces dla każdej próby
Dane tego raportu: [results/ntsc_isolated_main](../../../results/ntsc_isolated_main/). Nazwy plików JSON bez ścieżki odnoszą się do tego katalogu.


**Uwaga o definicji wyniku:** po 47 ukończonych próbach napotkano naturalne zakończenie lotu przed minutą. Procedurę jawnie uzupełniono: próba trwa do limitu 60 s albo do końca lotu, a krótsze loty pozostają w średniej. Nie doliczamy animacji końca gry. Nie jest to średnia wyłącznie z pełnych minut. Regułę dopisano w toku badania; szczegóły w UZUPELNIENIE_PROTOKOLU_PL.md. Liczebność i harmonogram nie zmieniły się. Wynik nie jest testem w całości zarejestrowanym z góry dla tej uzupełnionej definicji.

155 natywnych startów oryginału i 155 natywnych startów v9. Żadnych zapisów stanu ani modyfikacji pamięci gry. Pomiary 15, 30 i 60 s są zagnieżdżone w tym samym locie; jednostką statystyczną jest cały lot.

## Warunki i populacja scenariuszy

Atari 800XL 64 KB NTSC, standardowa konfiguracja bez przyspieszaczy, domyślny poziom, joystick wycentrowany, bez dopalacza i strzelania. START po 3000–3599 klatkach wideo od BOOT. Czasy losowane jednostajnie bez powtórzeń osobno dla każdej wersji; nie gwarantuje to jednostajnego rozkładu wszystkich map gry. Każde 5 prób każdej wersji tworzy zrównoważony blok, kolejność wewnątrz bloku losowa. Harmonogram i liczba prób zapisane w plan.json przed rozpoczęciem.

Po pierwszym wejściu $A32E zwalniamy START i wykonujemy 170 klatek wideo rozgrzewki. Następnie mierzymy liczbę odstępów pomiędzy ukończonymi obrazami na $B516 i ich czas w taktach Atari (1 789 772,5 Hz). Domykamy pierwszy pełny odstęp po 15/30/60 s. Wszystkie zliczone ukończenia obrazów należą do trybu lotu 2. Zapisujemy pełne odstępy, hashe terenu, pamięć przy wejściu i konfigurację.

Wyniki opisują średnią z jawnie zdefiniowanego zbioru 600 możliwych momentów START dla każdej wersji w tym emulatorze i scenariuszu. Nie opisują automatycznie wszystkich poziomów, sprzętów i sposobów grania. Nie dobieramy map pod korzystny wynik ani nie usuwamy poprawnych skrajnych prób.

Porównujemy natywne uruchomienia obu wersji przy tym samym rozkładzie momentów START. Nie wymuszamy jednakowych map: audyt wykazał, że ten sam moment START może generować różny teren w oryginale i v9. Procentowy zysk dotyczy średniego wyniku tego scenariusza użytkowego; nie jest izolowanym pomiarem przyspieszenia renderera na identycznym terenie.

## Średnie i rozrzut

| Okno | Oryginał FPS | SD oryginału | v9 FPS | SD v9 | Zysk |
|---|---:|---:|---:|---:|---:|
| 15 s | 5,7407 | 0,2771 | 6,8404 | 0,3393 | +19,16% |
| 30 s | 5,7637 | 0,2204 | 6,8293 | 0,2895 | +18,49% |
| 60 s | 5,8043 | 0,1937 | 6,8977 | 0,2581 | +18,84% |

## Niepewność wyniku 60 s

- original: średnia 5,8043 FPS, orientacyjny przedział ufności 95% 5,7736–5,8350 FPS; różne tablice terenu 155/155.
- original: loty zakończone przed limitem 60 s: 1/155; zakres rzeczywistych czasów mierzonych odstępów: 52,584–60,194 s.
- v9: średnia 6,8977 FPS, orientacyjny przedział ufności 95% 6,8567–6,9386 FPS; różne tablice terenu 155/155.
- v9: loty zakończone przed limitem 60 s: 1/155; zakres rzeczywistych czasów mierzonych odstępów: 32,058–60,161 s.

Kontrola sposobu uśredniania: suma wszystkich ukończonych odstępów / suma ich czasów daje 5,8044 FPS dla oryginału i 6,8978 FPS dla v9, czyli +18,84%. To wynik ważony długością lotu; główny wynik powyżej nadaje każdemu wylosowanemu lotowi jednakową wagę.

- Zysk: +18,84%; przybliżony przedział 95% metodą propagacji wariancji 17,90%–19,78% (połowa szerokości 0,94 p.p.).
- Kontrola bootstrap: 18,03%–19,66%. Losowano całe loty wewnątrz każdej kombinacji blok/wariant, zachowując liczebność bloków. 50 000 replikacji; nie losowano pojedynczych klatek.

Przedziały są przybliżone i warunkowe dla tego planu próbkowania. W wariancie analitycznym nie zastosowano korekty na skończony zbiór 600 scenariuszy, co daje zachowawcze oszacowanie błędu losowania bez zwracania. Bootstrap utrzymuje zaobserwowane bloki, nie modeluje nieznanych wspólnych zmian między przyszłymi sesjami. Powtarzalność techniczną sprawdzono osobnym audytem; wynik audytu nie jest dowodem pełnej poprawności emulatora.

## Bloki 60 s

| Blok | Oryginał FPS | v9 FPS | Zysk |
|---|---:|---:|---:|
| 1 | 5,7635 | 6,5797 | +14,16% |
| 2 | 5,7565 | 7,0618 | +22,67% |
| 3 | 5,9290 | 6,8616 | +15,73% |
| 4 | 5,7994 | 6,8895 | +18,80% |
| 5 | 5,7034 | 6,8953 | +20,90% |
| 6 | 5,8785 | 6,7978 | +15,64% |
| 7 | 5,7619 | 6,7439 | +17,04% |
| 8 | 5,8541 | 7,0029 | +19,62% |
| 9 | 5,8835 | 6,8543 | +16,50% |
| 10 | 5,7214 | 6,8718 | +20,11% |
| 11 | 5,6800 | 7,0532 | +24,18% |
| 12 | 5,7831 | 6,8257 | +18,03% |
| 13 | 5,7939 | 7,0811 | +22,22% |
| 14 | 5,8964 | 6,6699 | +13,12% |
| 15 | 5,8090 | 6,6889 | +15,15% |
| 16 | 5,7409 | 6,9208 | +20,55% |
| 17 | 5,7531 | 6,9892 | +21,49% |
| 18 | 5,8044 | 6,9080 | +19,01% |
| 19 | 5,8372 | 6,9278 | +18,68% |
| 20 | 5,9029 | 6,8579 | +16,18% |
| 21 | 5,8107 | 7,0653 | +21,59% |
| 22 | 5,7946 | 7,2790 | +25,62% |
| 23 | 6,0444 | 6,8892 | +13,98% |
| 24 | 5,7376 | 6,8669 | +19,68% |
| 25 | 5,9071 | 6,8861 | +16,57% |
| 26 | 5,8007 | 7,0614 | +21,73% |
| 27 | 5,7629 | 6,7765 | +17,59% |
| 28 | 5,8302 | 6,8940 | +18,25% |
| 29 | 5,8211 | 6,9440 | +19,29% |
| 30 | 5,6961 | 6,9544 | +22,09% |
| 31 | 5,6762 | 6,7305 | +18,57% |

## Zależność od długości lotu i kolejności

Kolejność w poniższej diagnostyce oznacza pozycję w zamrożonym harmonogramie. Przy wykonaniu równoległym nie jest to ścisła kolejność rozpoczęcia ani zakończenia procesów.

- original: SD dla 60 s / SD dla 15 s = 0,699; korelacja kolejność–FPS rho=-0,039, p=0,627; test Kruskala między blokami p=0,797.
- v9: SD dla 60 s / SD dla 15 s = 0,761; korelacja kolejność–FPS rho=0,087, p=0,281; test Kruskala między blokami p=0,040.

Wyniki diagnostycznych testów nie są dowodem równoważności bloków. Zmiana średniej przy dłuższym locie może wynikać z innego obciążenia na dalszej części trasy; 60 s nie jest wyłącznie dokładniejszym oszacowaniem tego samego pierwszego odcinka 15 s.

W v9 test różnic między blokami daje niekorygowane p≈0,040. Jest to sygnał diagnostyczny z kilku wykonywanych porównań, nie dowód dryfu emulatora ani identyczności małych serii. Bloki zawierają różne losowo przypisane scenariusze. Nie zaobserwowano istotnej monotonicznej zależności od pozycji w harmonogramie; nie wyklucza to innych różnic. Podany główny przedział opisuje losowanie z ustalonej populacji scenariuszy, a nie nieznane zmiany między emulatorami lub sesjami.

## Ocena zaplanowanej dokładności

Cel ±1 p.p. osiągnięty według zastosowanego przybliżonego przedziału: ±0,94 p.p. Nie dobierano dodatkowych prób po obejrzeniu wyniku i nie dołączono danych pilota.

## Materiały

- `plan.json`: zapisany z góry harmonogram.
- `benchmark.json`: wszystkie wyniki i metadane.
- `summary.json`: statystyki.
- `scripts/benchmark_ntsc_isolated.py`: procedura pomiarowa.
- `scripts/summarize_ntsc_isolated.py`: obliczenia.
- `scripts/report_ntsc_isolated.py`: raport i wykres.

Pomocniczych zrzutów RAM, pełnych logów emulatora i list taktów nie należy publikować w repozytorium.


## Zmiana sposobu wykonania

Pierwsze 86 prób wykonano sekwencyjnie. Po zgodzie użytkownika i dokładnej walidacji czterech lotów (minimum i maksimum FPS pilota dla każdej wersji) pozostałe próby wykonano w maksymalnie czterech oddzielnych emulatorach. Walidacja obejmowała wszystkie odstępy między obrazami, punkty 15/30/60 s i pełne 32 KB RAM w trzech punktach; uzyskano pełną zgodność. Nie zmieniono zaplanowanych scenariuszy. Szczegóły: ../ntsc_parallel_validation/WALIDACJA_PL.md.
