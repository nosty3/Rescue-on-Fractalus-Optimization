Dokument badawczy zachowany historycznie. Dawne ścieżki i wyniki dotyczą opisanego eksperymentu; aktualną implementację opisuje docs/OPTIMIZATIONS_PL.md, a wyniki zbiorcze docs/benchmarks/METHOD_PL.md (ścieżki od katalogu głównego repozytorium).

[English](NTSC_COMPARISON.md) · [Polski](NTSC_COMPARISON_PL.md)

# NTSC — porównanie oryginału i v9

22.10.2026. Atari 800XL, 64 KiB RAM, NTSC, bez przyspieszaczy.

**Oryginał: 5.811446 FPS. V9: 6.982743 FPS.**
**Wzrost: +1.171297 FPS, czyli +20.155%.**

| Scenariusz | Oryginał | v9 | Zmiana |
|---|---:|---:|---:|
| Prosto | 5.885863 | 6.931424 | +17.764% |
| Skręt w prawo | 5.807564 | 7.088889 | +22.063% |
| Skręt w lewo | 5.718009 | 6.826011 | +19.377% |
| Szybki lot w prawo | 5.834364 | 7.084954 | +21.435% |

Wynik łączny jest sumą odstępów między prezentacjami podzieloną przez
sumę czasu emulowanego dla danej wersji. Nie jest średnią arytmetyczną FPS.
Każdy z ośmiu pomiarów trwa co najmniej 3600 ramek NTSC, około minuty.
Liczone są nowe obrazy prezentowane przy $B516, a nie ramki odświeżania.
Wszystkie próby pozostawały w trybie lotu przy każdej prezentacji.

## Wspólne warunki początkowe

Oryginał uruchomiono od zimnego startu w NTSC i zatrzymano przy pierwszym
wejściu do głównej pętli lotu $A32E, w banku 2. Zapisano ten sam stan
emulatora dla obu wersji. Jest to granica przed obliczeniami geometrii,
bez aktywnej procedury optymalizowanego renderera na stosie.

Przed każdą próbą ładowano właściwy cartridge, wspólny stan, a następnie
sprawdzano konfigurację NTSC/64 KiB, PC i bank oraz cały widoczny bank 2
i stały bank ROM. Oryginał wykonywał swój oryginalny kod RAM. Wyłącznie
dla v9 podmieniono udokumentowane 215 bajtów kodu RAM $7EEB..$7FC1 na
kod v9, potrzebny do jej działania. Przed wykonaniem sprawdzano całe
32 KiB RAM: identyczne między wersjami poza tym celowym fragmentem kodu.

Następnie obie wersje wykonywały 120 ramek lotu bez wychylenia joysticka,
po czym ustawiano kierunek scenariusza i wykonywano 50 ramek rozgrzewki.
W szybkim locie przed rozgrzewką dodatkowo przytrzymywano OPTION przez
45 ramek. Zegar NTSC: 1789772,5 Hz, ramka: 29868 taktów (114*262).
Po każdym przebiegu sprawdzano sygnaturę właściwego kodu RAM.

Szybszy kod zmienia postęp gry w czasie, więc nie gwarantuje identycznej
geometrii w każdej kolejnej klatce obu przebiegów. To porównanie wspólnego
stanu wejściowego i protokołu sterowania, nie test samych cykli renderera
na zamrożonym zestawie scen. Jedna seria nie daje przedziału ufności.

## Relacja do wcześniejszego pomiaru v9

Wcześniejsze 6,810914 FPS pochodziło z osobnego zimnego startu v9.
Do tego porównania zmierzono v9 ponownie ze wspólnego stanu oryginału.
Procentowy zysk powyżej używa wyłącznie tej nowej pary pomiarów.
Nie należy łączyć licznika z jednej serii z mianownikiem z drugiej.
Historyczny raport NTSC_V9_MEASUREMENT_PL.md pozostaje zapisem poprzedniego testu.

Oryginał może wykazywać wcześniej zidentyfikowany wyścig buforów; licznik
prezentacji nie oznacza, że każda wyświetlona ramka była bez artefaktów.
V9 zawiera naprawę synchronizacji i optymalizację PMG.

## Pliki i odtworzenie

Oryginał SHA256: `1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68`.
V9 SHA256: `0c8226e1f58ad26b2a103cbf59c4b8b23fdb87caac0e22f2586a83513a859880`.
Nie zmieniono ROM-ów, nazw istniejących plików ani README.

Skrypty: `python scripts/compare_ntsc.py prepare`, następnie
`python scripts/compare_ntsc.py benchmark` i `python scripts/report_ntsc_comparison.py`.
Wymagają lokalnego mostka Altirry i SDK. Przygotowanie tworzy świeży stan
z oryginału, więc nie wymaga dawnych stanów PAL ani poprzednich dumpów.
Dokładne ponowienie tej samej sesji wymaga zachowanego lokalnego stanu;
nowy zimny start może dać inny przebieg losowy i trochę inne wyniki.
W kopii repozytorium oryginał jest w original/Rescue on Fractalus!.rom;
skrypt obsługuje również pierwotne lokalne położenie w katalogu projektu.

Zwarte wyniki i konfiguracja są w results/ntsc_comparison. Screeny, stany
i surowe znaczniki prezentacji pozostają lokalnie, poza repozytorium.
