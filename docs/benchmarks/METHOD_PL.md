# Metodyka pomiaru FPS — v11

[English](METHOD.md) · [Polski](METHOD_PL.md)

## Scenariusze i liczebność

Dwa standardy: PAL i NTSC. Dwa scenariusze: lot prosto z wycentrowanym joystickiem oraz powtarzane 1 s joysticka w górę (nurkowanie) / 3 s neutralnie. Sterowanie zaczyna się w chwili rozpoczęcia pomiaru; rozgrzewka pozostaje neutralna. Bez strzelania i skrętów. Każda kombinacja wersji, standardu i scenariusza zawiera 155 prób. Cztery konfiguracje up38/v11 × prosto/nurkowanie dały 1240 lotów; dodatkowy oryginał z nurkowaniem to 310 lotów. Historyczny oryginał w locie prosto dostarcza pozostałe 310 obserwacji do porównania oryginał–v11.

## Uruchamianie i licznik

Każda próba uruchamia świeży, izolowany proces AltirraBridge, Atari 800XL/64 KB, bez akceleratora, z natywnym zimnym startem właściwego kartridża. Nie przenosi się stanów ani nie modyfikuje pamięci gry. Cztery procesy mają osobne porty, tokeny i pliki; szybkość komputera gospodarza nie wyznacza czasu testu.

Harmonogram startów wybrano wcześniej (ziarno 2026102303, menu_frames 3000–3599, 31 bloków po 5 prób). up38 i v11 w obu scenariuszach oraz nowe nurkowania oryginału używają 155 startów gałęzi v9 z historycznego planu NTSC. Historyczne loty prosto oryginału mają własne niezależnie losowane starty; nie należy traktować ich jako sparowanych z v11. Wspólny start nie gwarantuje identycznej geometrii i zdarzeń później, ponieważ czas wykonania kodu może wpływać na rozwój gry.

Po pierwszym wejściu do $A32E zwalnia się START i wykonuje 170 klatek obrazu rozgrzewki. Pierwsze trafienie $B516 jest początkiem pomiaru. Liczone są pełne odstępy między kolejnymi prezentacjami gotowego obrazu. FPS = liczba odstępów / czas tych odstępów, nie częstość VBI ani odświeżania monitora. Zegar Atari: PAL 1773447,5 Hz; NTSC 1789772,5 Hz. Pomiar obejmuje DMA, VBI/DLI i oczekiwania synchronizacyjne.

Pierwszy pełny odstęp przekraczający 60 s zamyka okno. Punkty 15/30/60 s są zagnieżdżone i nie stanowią osobnych prób. Zapis $4A wykrywa naturalny koniec lotu: zachowuje się wszystkie pełne obrazy sprzed wyjścia z lotu, bez animacji zakończenia. Krótsze loty i skrajne wyniki pozostają w próbie. W nowych nurkowaniach oryginału dotyczyło to 4/155 PAL i 4/155 NTSC.

Wychylenia joysticka planuje się według taktów Atari, a nie FPS ani czasu komputera: 0, 4, 8… s początek nurkowania, 1, 5, 9… s powrót do neutralnego. Największe odchylenie zapisanego momentu wejścia wyniosło 0,5 taktu.

## Przyspieszenie pomiaru i kontrola

Użyto zatwierdzonego grupowania komend FRAME/CYCLES, odczytu PC/trybu oraz CLOCK w jednym zapisie TCP. Nadal obowiązują breakpointy i kolejność wykonania. Nie użyto niepełnego profilu ograniczonego do 4096 wpisów jako licznika klatek. Walidacja transportu i sekwencyjne/równoległe kontrole dały zgodne zdarzenia oraz pamięć. Wszystkie 310 lotów prosto up38 odtworzyło historyczne liczniki i FPS.

Podczas części wcześniejszej serii 1240 lotów omyłkowo nakładały się dwa uruchomienia runnera (do ośmiu emulatorów). Zatrzymano duplikat; uwzględniono po jednym kompletnym rekordzie na próbę, bez wyboru po FPS. Cztery powtórzenia z tego okresu odtworzyły wszystkie znaczniki czasu i pamięć. Szczegóły zachowuje results/v11/runtime_notes.json. Nowe 310 lotów oryginału wykonano jednym runnerem i czterema emulatorami, w 1455,2 s czasu komputera.

Osiem grup początkowych stanów PAL w porównaniu up38/v11 różniło się jedynie bajtami $0270–$0277. Kontrole normalizacji i watchpointy wykazały zgodność reszty pamięci i brak odczytów tych bajtów w sprawdzonych scenariuszach. Nie modyfikowano ich w trakcie benchmarków.

## Obliczenia

Podstawą jest średnia arytmetyczna FPS pojedynczych lotów, każdy z równą wagą. Wynik zbiorczy = (średnia prosto + średnia nurkowanie) / 2. Zysk = 100 × (średnia v11 / średnia oryginału − 1), także w wierszu zbiorczym. Nie uśredniamy procentów scenariuszy. Waga 50/50 definiuje benchmark, a nie empiryczny udział tych zachowań w typowej grze.

W porównaniu up38/v11 przedziały wyznaczono przez 50000 sparowanych powtórzeń bootstrap, losując całe loty w 31 blokach, z ziarnem 2026103001. Nie przenosimy tych przedziałów do tabel oryginał–v11; historyczny oryginał prosto nie jest sparowany. Główne tabele podają estymaty punktowe. Wykresy rozkładu pokazują wszystkie loty.

## Dane i ograniczenia

- results/v11/flights.jsonl: 1550 nowych obserwacji z czasami prezentacji i sterowaniem.
- results/pal_isolated_main/benchmark.json i results/ntsc_isolated_main/benchmark.json: historyczne loty prosto oryginału.
- results/v11/summary.json: tabele oryginał–v11; up38_comparison_summary.json: dodatkowy zysk względem up38.
- scripts/report_v11.py odtwarza wykresy i sprawdza liczby z zapisanych obserwacji.
- scripts/benchmark_v11.py uruchamia nowe serie w osobnym katalogu wskazanym przez --output; nie uruchamiaj go tylko po to, by odtworzyć wykresy.

Są to wyniki kartridża. Nie wykonano osobnej pełnej serii FPS XEX. Test nie pokrywa całej różnorodności skrętów, poziomów, ratowania pilotów ani sprzętowych akceleratorów. Testy przejścia poziomu XEX celowo ustawiają dane diagnostyczne; nie wchodzą do pomiarów FPS.
