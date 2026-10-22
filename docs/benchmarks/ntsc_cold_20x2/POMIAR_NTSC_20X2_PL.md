Dokument badawczy zachowany historycznie. Dawne ścieżki i wyniki dotyczą opisanego eksperymentu; aktualną implementację opisuje docs/OPTYMALIZACJE_PL.md, a wyniki zbiorcze docs/benchmarks/METODA_PL.md (ścieżki od katalogu głównego repozytorium).

# NTSC: dwie serie po 20 zimnych startów oryginału i v9

Każda seria obejmuje 20 prób oryginału i 20 prób v9. Łącznie 80 osobnych uruchomień. Nie wczytywano zapisów stanu, nie przenoszono pamięci między wersjami i nie modyfikowano kodu ani danych gry.

## Procedura

- Altirra headless, Atari 800XL, 64 KB, NTSC, bez rozszerzeń przyspieszających.
- Każda próba ładuje i uruchamia obraz gry od początku komendą BOOT.
- Czas przed START: 3000–3599 klatek wideo, wybierany niezależnie dla każdej próby. Dwie serie mają różne zapisane ziarna generatora wyboru czasu oczekiwania. Nie narzucamy ziarna generatorowi terenu gry.
- Domyślny poziom początkowy, joystick wycentrowany, bez dopalacza i strzelania. Po wejściu do pierwszej pętli lotu ($A32E) zwalniamy START i wykonujemy 170 klatek wideo rozgrzewki.
- Mierzymy ukończone obrazy gry na $B516, a nie częstotliwość odświeżania NTSC. Początek pomiaru przypada na pierwsze osiągnięcie tego punktu po rozgrzewce. Koniec przypada na pierwsze jego osiągnięcie po upływie 15 sekund. Domknięcie ostatniego obrazu usuwa błąd liczenia niepełnej klatki; rzeczywisty czas każdej próby zapisano w JSON.
- FPS próby = liczba pełnych odstępów między obrazami / rzeczywisty czas tych odstępów. Czas pochodzi z zegara emulowanego Atari: 1 789 772,5 Hz.
- Raportowana średnia to średnia arytmetyczna z FPS poszczególnych prób. Oryginał i v9 uruchamiamy naprzemiennie, zmieniając kolejność w kolejnych parach.
- Sprawdzamy tryb lotu przez cały pomiar, konfigurację NTSC, bank ROM i kod v9. Skrót SHA-256 tablicy $0900–$09FF kontroluje różnorodność danych terenu.

## Wyniki

| Seria | Oryginał: średnia FPS | v9: średnia FPS | Wzrost FPS |
|---|---:|---:|---:|
| 1 | 5,7764 | 6,7344 | +16,58% |
| 2 | 5,7708 | 7,0054 | +21,39% |
| Łącznie (40 + 40 prób) | 5,7736 | 6,8699 | +18,99% |

## Rozrzut między próbami

| Seria | Wersja | Min–max FPS | Odchylenie standardowe FPS | Średnia ± połowa przedziału ufności 95% | Różne tablice terenu |
|---|---|---:|---:|---:|---:|
| 1 | original | 5,4295–6,4817 | 0,2776 | 5,7764 ± 0,1299 | 20/20 |
| 1 | v9 | 6,4227–7,0497 | 0,1935 | 6,7344 ± 0,0906 | 20/20 |
| 2 | original | 5,5018–6,3944 | 0,2324 | 5,7708 ± 0,1088 | 20/20 |
| 2 | v9 | 6,4674–7,6483 | 0,3153 | 7,0054 ± 0,1476 | 20/20 |
| Łącznie | original | 5,4295–6,4817 | 0,2527 | 5,7736 ± 0,0808 | 40/40 |
| Łącznie | v9 | 6,4227–7,6483 | 0,2924 | 6,8699 ± 0,0935 | 40/40 |

Przedziały ufności wykorzystują rozkład t-Studenta i traktują próby jako niezależne próbki. Opisują niepewność średniej tego scenariusza, nie zakres FPS całej gry.

## Powtarzalność

- original: seria 2 minus seria 1 = -0,0056 FPS (-0,10%).
- v9: seria 2 minus seria 1 = 0,2710 FPS (4,02%).
- Różnica oszacowanego wzrostu FPS między seriami: 4,81 punktu procentowego.

## Ocena tych dwóch serii

Oryginał dał niemal identyczną średnią w obu seriach. Dla v9 różnica wyniosła około 4,02%, a szacowany zysk wzrósł z 16,58% do 21,39%. Obie serie potwierdzają wyraźną przewagę v9 w tym scenariuszu, lecz nie potwierdzają jeszcze powtarzalności dokładnego procentu zysku. Przy podanych założeniach statystycznych 95-procentowe przedziały średniej v9 obu serii nie nakładają się. Nie można więc po prostu uznać rozbieżności za pomijalną.

Łączna średnia jest opisem wykonanych 40 prób każdej wersji; nie usuwa rozbieżności między seriami. Różne mapy są potwierdzone, ale te pomiary nie rozstrzygają, czy odpowiadają za całą różnicę średnich. W dalszej analizie należy sprawdzić warunki inicjalizacji i rozkład obciążeń dla wylosowanych map przed uznaniem procedury za stabilną na poziomie około 1%. Nie wykonano dodatkowych, wybieranych po wyniku serii ani nie odrzucano prób skrajnych.

Każda wersja otrzymuje własne, niezależnie wygenerowane mapy. To porównanie próbek normalnych uruchomień, a nie pomiar obu wersji na identycznych mapach. Zgodność dwóch serii oceniamy na podstawie różnicy średnich i rozrzutu, bez założenia z góry, że muszą się zgodzić.

Wyniki dotyczą początkowego prostego lotu, z pominięciem 170 klatek wideo rozgrzewki. Nie uogólniają automatycznie wydajności na późniejsze poziomy, walkę, lądowanie ani inne sposoby sterowania. Poprzednie wyniki 6,8109 i 6,9827 FPS obejmowały inny, dłuższy zestaw scenariuszy, więc nie są bezpośrednimi powtórzeniami tego testu.

## Pliki i odtwarzanie

- `benchmark.json`: wszystkie 80 wyników, czas, liczba obrazów, skróty terenu i parametry.
- `summary.json`: statystyki i różnice między seriami.
- `scripts/benchmark_ntsc_cold.py`: pełna procedura pomiarowa; wymaga uruchomionego emulatora przez `scripts/launch.ps1`.
- `scripts/report_ntsc_cold.py`: generowanie tego raportu bez emulatora.

W celu powtórzenia uruchom `python scripts/benchmark_ntsc_cold.py`, następnie `python scripts/report_ntsc_cold.py`. Skrypt nadpisuje wynik w swoim katalogu; wcześniejsze wyniki należy najpierw zachować.

Oryginał SHA-256: `1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68`.

v9 ROM SHA-256 (bez nagłówka CAR): `0c8226e1f58ad26b2a103cbf59c4b8b23fdb87caac0e22f2586a83513a859880`.
