# PAL — powtórzenie automatycznego testu oryginału i v9

[English](PAL_REPORT.md) · [Polski](PAL_REPORT_PL.md)
Dane tego raportu: [results/pal_isolated_main](../../../results/pal_isolated_main). Nazwy plików JSON bez ścieżki odnoszą się do tego katalogu.


Wykonano 155 natywnych startów każdej wersji. Średni FPS: oryginał **6,4421**, v9 **7,5623**, zysk **17,39%**.

## Protokół ustalony przed pomiarem

- Atari 800XL, 64 KB, PAL, standardowe dodatki, bez przyspieszaczy. Te same obrazy oryginału i v9 oraz ten sam emulator co w badaniu NTSC.
- Nowy proces emulatora dla każdego startu. Bez wczytywania stanów i modyfikowania pamięci gry.
- Dokładnie ten sam harmonogram 155 prób na wersję co w NTSC: START po 3000–3599 ramkach wideo, losowanie bez zwracania osobno dla każdej wersji. Bloki po pięć lotów każdej wersji.
- Pierwsze wejście $A32E, zwolnienie START, 170 ramek rozgrzewki, joystick wycentrowany. Bez skrętów, nurkowania, strzelania i dopalacza.
- Licznik odstępów między obrazami na $B516, zegar PAL 1 773 447,5 Hz. Ramka PAL ma 35 568 taktów (312 × 114).
- Punkty 15/30/60 sekund są kolejnymi oknami tego samego lotu, a nie niezależnymi próbami. Domykany jest pierwszy pełny odstęp po limicie.
- Przy wcześniejszym wyjściu z trybu lotu próba pozostaje w zbiorze. Liczone są pełne odstępy do ostatniego ukończonego obrazu lotu; animacja końca nie wchodzi do czasu. Reguła obowiązywała przed rozpoczęciem PAL.
- Cztery odizolowane emulatory, osobne porty/tokeny/pliki. Agregat zapisuje jeden wątek w kolejności planu. Każdy blok kończy się przed rozpoczęciem następnego.
- Liczbę 155 przyjęto przed pomiarem, aby powtórzyć NTSC. Nie wykonywano nowego pilota do doboru liczebności PAL i nie dobierano dalszych prób po obejrzeniu wyniku.

170 ramek rozgrzewki trwa w PAL około 3,41 s, a w NTSC około 2,84 s. Również oczekiwanie w menu jest dłuższe w PAL. Zachowano liczbę ramek z protokołu, nie ich czas w sekundach. Właściwy limit pomiaru to 60 sekund czasu emulowanego Atari w obu standardach.

## Walidacja techniczna

Przed główną serią wykonano cztery 15-sekundowe scenariusze (dwa na wersję) sekwencyjnie i ponownie równolegle. Wszystkie odstępy między obrazami i pełne 32 KB RAM przy wejściu, po rozgrzewce i na końcu były identyczne. Te osiem lotów kontrolnych nie wchodzi do głównej średniej. Dane: ../../../results/pal_parallel_validation/validation.json.
Po zakończeniu sprawdzono zgodność 310 prób z planem, unikalność momentów START w każdej wersji, tryb PAL, hashe zdarzeń i RAM oraz ponownie przeliczono FPS z taktów. Wynik: integrity.json.

## Wyniki

| Limit | Oryginał FPS | SD | v9 FPS | SD | Zysk |
|---|---:|---:|---:|---:|---:|
| 15 s | 6,4231 | 0,3473 | 7,5984 | 0,3954 | 18,30% |
| 30 s | 6,4249 | 0,2769 | 7,5709 | 0,3251 | 17,84% |
| 60 s | 6,4421 | 0,2213 | 7,5623 | 0,2771 | 17,39% |

## Niepewność i krótsze loty

- original: przybliżony przedział ufności 95% średniej 6,4070–6,4772 FPS; mediana 6,4159; 155/155 różnych tablic terenu.
- original: 3/155 lotów krótszych niż limit 60 s; zakres zmierzonych czasów 44,223–60,168 s.
- v9: przybliżony przedział ufności 95% średniej 7,5183–7,6063 FPS; mediana 7,5340; 155/155 różnych tablic terenu.
- v9: 4/155 lotów krótszych niż limit 60 s; zakres zmierzonych czasów 47,131–60,188 s.
- Zysk 17,39%; przybliżony przedział ufności 95% 16,46–18,32%, połowa szerokości 0,93 p.p.
- Bootstrap warstwowy (50 000 replikacji całych lotów wewnątrz blok/wariant): 16,56–18,23%.
- Kontrola ważenia czasem: 6,4430 i 7,5634 FPS; zysk 17,39%. Główny wynik nadaje każdemu lotowi jednakową wagę.

Przedziały są przybliżone. Analityczny przedział nie stosuje korekty na losowanie bez zwracania z 600 możliwych momentów START, co jest zachowawcze. Bootstrap utrzymuje zaobserwowane bloki; nie modeluje nieznanych zmian między przyszłymi sesjami. Dokładność dotyczy określonej populacji scenariuszy, nie całej gry.

## Porównanie z NTSC

| Standard | Oryginał FPS | v9 FPS | Zysk |
|---|---:|---:|---:|
| PAL | 6,4421 | 7,5623 | 17,39% |
| NTSC | 5,8043 | 6,8977 | 18,84% |

Różnica punktowych oszacowań zysku PAL minus NTSC: -1,45 p.p. To porównanie opisowe; nie jest osobnym testem równoważności standardów.

Te same momenty START wyrażone w ramkach nie gwarantują tych samych map ani trajektorii w różnych wersjach lub standardach. Wynik opisuje natywne uruchomienia przy wycentrowanym joysticku; nie jest pomiarem samego renderera na identycznych danych. Nie obejmuje kontrolowanego lotu w dolinach, skrętów ani innych poziomów.

## Rozrzut i diagnostyka kolejności

- original: SD okna 60 s / SD okna 15 s = 0,637; korelacja z pozycją w harmonogramie rho=-0,035, p=0,662; Kruskal między blokami p=0,547.
- v9: SD okna 60 s / SD okna 15 s = 0,701; korelacja z pozycją w harmonogramie rho=-0,019, p=0,815; Kruskal między blokami p=0,810.

Diagnostyczne p nie są skorygowane na wielokrotne porównania ani dowodem równoważności małych bloków. Kolejność dotyczy zamrożonego harmonogramu, nie ścisłej kolejności ukończenia procesów.

## Materiały

- plan.json, benchmark.json, summary.json, integrity.json — harmonogram, wyniki, statystyki i kontrola integralności.
- FPS_DISTRIBUTION_PAL_EN.png / .svg — rozkład FPS i dystrybuanta po angielsku.
- FLIGHT_DURATION_PAL_EN.png / .svg — zależność średniej od długości pomiaru po angielsku.
- scripts/benchmark_pal_parallel.py i pal_repro_common.py — wykonanie badania.
- scripts/summarize_ntsc_isolated.py main --video pal — statystyki.
- scripts/verify_ntsc_main_data.py --video pal — kontrola danych.
- scripts/plot_ntsc_english.py --video pal — wykresy.
- scripts/report_pal_isolated.py — ten raport.

Zrzuty RAM i pełne logi są materiałami diagnostycznymi lokalnymi, nie przeznaczonymi do kopiowania do repozytorium.
