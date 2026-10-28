# Rescue on Fractalus! — Atari XL/XE optimization

Pierwszy etap optymalizacji przygotował **nosty** z **ChatGPT-6 Astra** (+18%). Następnie **Solo** z zespołem agentów **Opus** znalazł dalsze optymalizacje uzyskując wynik około 39%. Jego prace znów poprawiła **Astra** uzyskując obecny wynik. Wydanie **v11** optymalizuje Rescue on Fractalus! na Atari XL/XE, zachowując szczegółowość terenu i rozdzielczość obrazu. Obecny wynik zbiorczy to **+40,04% PAL i +43,13% NTSC**.

[English](README.md) · [Polski](README_PL.md)

## Pobieranie

Katalog **[optimized version](optimized%20version/)** zawiera wyłącznie aktualne pliki gry i informację o wersji:

- **[CAR](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20128KB.car)** / **[ROM](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20128KB.rom)** — XEGS 128 KB (type 14), Atari XL/XE 64 KB RAM, PAL/NTSC.
- **[XEX](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20320KB-1MB.xex)** — 320 KB Rambo, 576 KB lub 1088 KB RAM; wyłącz BASIC. Zawiera poprawkę ukończenia poziomu.

Uruchom od zimnego startu; stary zapis emulatora może zawierać poprzedni kod.

## Zmierzone FPS

Poniższe wyniki dotyczą **kartridża**. XEX przeszedł testy działania, ale nie osobną pełną serię FPS. Procenty we wstępie opisują w przybliżeniu kolejne etapy; dokładne wyniki zależą od standardu i scenariusza.

### PAL

| Scenariusz | Oryginał — FPS | v11 — FPS | Przyrost FPS | Zysk |
|---|---:|---:|---:|---:|
| Lot prosto | 6.4421 | 9.0779 | +2.6358 | +40.91% |
| Okresowe nurkowanie | 6.1013 | 8.4879 | +2.3866 | +39.12% |
| **Wynik zbiorczy 50/50** | **6.2717** | **8.7829** | **+2.5112** | **+40.04%** |

![PAL FPS comparison](docs/benchmarks/charts/V11_COMPARISON_PAL.png)

![PAL FPS distribution](docs/benchmarks/charts/V11_DISTRIBUTION_PAL.png)

### NTSC

| Scenariusz | Oryginał — FPS | v11 — FPS | Przyrost FPS | Zysk |
|---|---:|---:|---:|---:|
| Lot prosto | 5.8043 | 8.3120 | +2.5077 | +43.20% |
| Okresowe nurkowanie | 5.3787 | 7.6942 | +2.3155 | +43.05% |
| **Wynik zbiorczy 50/50** | **5.5915** | **8.0031** | **+2.4116** | **+43.13%** |

![NTSC FPS comparison](docs/benchmarks/charts/V11_COMPARISON_NTSC.png)

![NTSC FPS distribution](docs/benchmarks/charts/V11_DISTRIBUTION_NTSC.png)

Każdy scenariusz: **155 prób do 60 sekund**, nowy proces emulatora i zimny start. Nurkowanie: 1 s joystick w górę, 3 s neutralnie, cyklicznie. Zachowano naturalnie krótsze loty i wszystkie wyniki. FPS oznacza gotowe obrazy terenu, nie odświeżanie ekranu. Wynik zbiorczy jest średnią 50/50 dwóch scenariuszy; zysk to iloraz średnich FPS, nie średnia procentów. Oryginał w locie prosto pochodzi z historycznej serii z osobno losowanymi startami; nurkowanie ma harmonogram wspólny z v11.

[Metodyka i dane](docs/benchmarks/METHOD_PL.md) · [Raport v11](docs/benchmarks/V11_REPORT_PL.md)

## Co zoptymalizowano

- Przebudowano rasteryzację terenu i wyspecjalizowano typowe głębokości oraz szerokości profilu gór.
- Przyspieszono dokładne dzielenie, interpolację i przetwarzanie geometrii, zachowując ścieżki zapasowe.
- Ograniczono odwołania plottera do pamięci i koszty przekraczania granic stron.
- Skrócono rysowanie/kasowanie PMG i aktualizowano tylko zmienione fragmenty wskaźników.
- Rozwinięto pętle miksera oraz zabezpieczono przełączanie banków i wznowienie po Esc.
- Solo/Opus: rozpoczęto kasowanie po przejściu wiązki obrazu przez teren, z zabezpieczeniem buforów.
- Solo/Opus: pominięto pewnie zasłonięte podziały terenu i kasowano tylko potrzebne fragmenty kolumn.
- Solo/Opus: skrócono obsługę przerwania dla milczących kanałów dźwięku i wskaźnika kokpitu.
- Zespół Solo, w tym Fable: włączono dzielenie bezpośrednio do projekcji i usprawniono pętlę krawędzi.
- Astra: zastosowano HD=152 dla wyczyszczonych kolumn i jednorazowe odtwarzanie Y na wspólnych wyjściach plottera.
- Astra: usunięto przeliczanie wysokości na wiersze z kasowania na żądanie i wypełniania.
- Astra: zachowano próg zasłaniania w A, ograniczając powtarzane odczyty.
- Dostosowano loader XEX Solo do v11 i poprawiono wskaźniki melodii blokujące ukończenie poziomu.

[Pełny opis techniczny](docs/OPTIMIZATIONS_PL.md) · [Odtwarzanie ze źródeł](docs/REBUILD_PL.md)

## Katalogi repozytorium

- **[optimized version/](optimized%20version/)** — Aktualny v11: CAR, ROM, XEX i informacja o wersji.
- **[original/](original/)** — Oryginalny ROM do rekonstrukcji i porównań.
- **[dist/](dist/)** — Aktualny IPS i manifest sum kontrolnych.
- **[src/](src/)** — Źródła MADS; najnowsze banki znajdują się w src/v11.
- **[scripts/](scripts/)** — Narzędzia budowania, pomiarów, analizy i wykresów.
- **[analysis/](analysis/)** — Materiały inżynierii wstecznej.
- **[results/](results/)** — Wybrane dane pomiarowe i walidacja; najnowsze w results/v11.
- **[docs/](docs/)** — Szczegółowy opis zmian, metodyka i badania.
- **[arc/up38/](arc/up38/)** — Archiwum pracy Solo/Opusa, źródła i historyczne pliki up38.

Starsze nasze wydania pozostają w historii Git. Archiwalny XEX up38 ma znany błąd ukończenia poziomu — używaj v11. Dokumentacja jest po polsku (_PL) i angielsku (bez sufiksu). Nie publikujemy zrzutów pamięci, zapisów stanu ani screenów testowych. Testy emulatora nie obejmują wszystkich sytuacji gry ani wszystkich fizycznych rozszerzeń pamięci.
