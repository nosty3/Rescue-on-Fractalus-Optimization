Dokument badawczy zachowany historycznie. Dawne ścieżki i wyniki dotyczą opisanego eksperymentu; aktualną implementację opisuje docs/OPTIMIZATIONS_PL.md, a wyniki zbiorcze docs/benchmarks/METHOD_PL.md (ścieżki od katalogu głównego repozytorium).

[English](NTSC_REPORT.md) · [Polski](NTSC_REPORT_PL.md)

# NTSC: pilot — świeży proces dla każdej próby

20 natywnych startów oryginału i 20 natywnych startów v9. Żadnych zapisów stanu ani modyfikacji pamięci gry. Pomiary 15, 30 i 60 s są zagnieżdżone w tym samym locie; jednostką statystyczną jest cały lot.

## Warunki i populacja scenariuszy

Atari 800XL 64 KB NTSC, standardowa konfiguracja bez przyspieszaczy, domyślny poziom, joystick wycentrowany, bez dopalacza i strzelania. START po 3000–3599 klatkach wideo od BOOT. Czasy losowane jednostajnie bez powtórzeń osobno dla każdej wersji; nie gwarantuje to jednostajnego rozkładu wszystkich map gry. Każde 5 prób każdej wersji tworzy zrównoważony blok, kolejność wewnątrz bloku losowa. Harmonogram i liczba prób zapisane w plan.json przed rozpoczęciem.

Po pierwszym wejściu $A32E zwalniamy START i wykonujemy 170 klatek wideo rozgrzewki. Następnie mierzymy liczbę odstępów pomiędzy ukończonymi obrazami na $B516 i ich czas w taktach Atari (1 789 772,5 Hz). Domykamy pierwszy pełny odstęp po 15/30/60 s. Wszystkie zliczone ukończenia obrazów należą do trybu lotu 2. Zapisujemy pełne odstępy, hashe terenu, pamięć przy wejściu i konfigurację.

Wyniki opisują średnią z jawnie zdefiniowanego zbioru 600 możliwych momentów START dla każdej wersji w tym emulatorze i scenariuszu. Nie opisują automatycznie wszystkich poziomów, sprzętów i sposobów grania. Nie dobieramy map pod korzystny wynik ani nie usuwamy poprawnych skrajnych prób.

## Średnie i rozrzut

| Okno | Oryginał FPS | SD oryginału | v9 FPS | SD v9 | Zysk |
|---|---:|---:|---:|---:|---:|
| 15 s | 5,6056 | 0,2446 | 6,7503 | 0,3112 | +20,42% |
| 30 s | 5,6586 | 0,2116 | 6,7900 | 0,2443 | +19,99% |
| 60 s | 5,6922 | 0,1953 | 6,8369 | 0,2268 | +20,11% |

## Niepewność wyniku 60 s

- original: średnia 5,6922 FPS, orientacyjny przedział ufności 95% 5,6008–5,7836 FPS; różne tablice terenu 20/20.
- original: loty zakończone przed limitem 60 s: 0/20; zakres rzeczywistych czasów mierzonych odstępów: 60,011–60,161 s.
- v9: średnia 6,8369 FPS, orientacyjny przedział ufności 95% 6,7308–6,9430 FPS; różne tablice terenu 20/20.
- v9: loty zakończone przed limitem 60 s: 0/20; zakres rzeczywistych czasów mierzonych odstępów: 60,011–60,144 s.

Kontrola sposobu uśredniania: suma wszystkich ukończonych odstępów / suma ich czasów daje 5,6922 FPS dla oryginału i 6,8369 FPS dla v9, czyli +20,11%. To wynik ważony długością lotu; główny wynik powyżej nadaje każdemu wylosowanemu lotowi jednakową wagę.

- Zysk: +20,11%; przybliżony przedział 95% metodą propagacji wariancji 17,60%–22,62% (połowa szerokości 2,51 p.p.).
- Kontrola bootstrap: 17,93%–22,40%. Losowano całe loty wewnątrz każdej kombinacji blok/wariant, zachowując liczebność bloków. 50 000 replikacji; nie losowano pojedynczych klatek.

Przedziały są przybliżone i warunkowe dla tego planu próbkowania. W wariancie analitycznym nie zastosowano korekty na skończony zbiór 600 scenariuszy, co daje zachowawcze oszacowanie błędu losowania bez zwracania. Bootstrap utrzymuje zaobserwowane bloki, nie modeluje nieznanych wspólnych zmian między przyszłymi sesjami. Powtarzalność techniczną sprawdzono osobnym audytem; wynik audytu nie jest dowodem pełnej poprawności emulatora.

## Bloki 60 s

| Blok | Oryginał FPS | v9 FPS | Zysk |
|---|---:|---:|---:|
| 1 | 5,6309 | 6,7501 | +19,88% |
| 2 | 5,7242 | 7,0272 | +22,76% |
| 3 | 5,7624 | 6,7989 | +17,99% |
| 4 | 5,6514 | 6,7713 | +19,82% |

## Zależność od długości lotu i kolejności

Kolejność w poniższej diagnostyce oznacza pozycję w zamrożonym harmonogramie. Przy wykonaniu równoległym nie jest to ścisła kolejność rozpoczęcia ani zakończenia procesów.

- original: SD dla 60 s / SD dla 15 s = 0,798; korelacja kolejność–FPS rho=0,067, p=0,779; test Kruskala między blokami p=0,635.
- v9: SD dla 60 s / SD dla 15 s = 0,729; korelacja kolejność–FPS rho=-0,030, p=0,900; test Kruskala między blokami p=0,315.

Wyniki diagnostycznych testów nie są dowodem równoważności bloków. Zmiana średniej przy dłuższym locie może wynikać z innego obciążenia na dalszej części trasy; 60 s nie jest wyłącznie dokładniejszym oszacowaniem tego samego pierwszego odcinka 15 s.

## Planowanie oddzielnego pomiaru głównego

Dla celu ±1 p.p. zysku (95%) i zaobserwowanego rozrzutu 60 s: około 127 prób na wersję. Z 20% zapasem i zaokrągleniem do pełnych bloków: 155 prób na wersję.

To prognoza, nie gwarancja końcowej dokładności. Liczbę należy zamrozić przed pomiarem głównym; nie kończyć go na podstawie korzystnego chwilowego wyniku. Pilota nie dodawać do średniej potwierdzającego testu.

## Materiały

- `plan.json`: zapisany z góry harmonogram.
- `benchmark.json`: wszystkie wyniki i metadane.
- `summary.json`: statystyki.
- `scripts/benchmark_ntsc_isolated.py`: procedura pomiarowa.
- `scripts/summarize_ntsc_isolated.py`: obliczenia.
- `scripts/report_ntsc_isolated.py`: raport i wykres.

Pomocniczych zrzutów RAM, pełnych logów emulatora i list taktów nie należy publikować w repozytorium.
