# Rescue on Fractalus! — optymalizacja dla Atari XL/XE

Pierwszy etap optymalizacji przygotował **nosty** z **ChatGPT-6 Astra** (+18%). Następnie **Solo** z zespołem agentów **Opus** znalazł dalsze optymalizacje uzyskując wynik około 39%. Jego prace znów poprawiła **Astra** uzyskując obecny wynik. **v12** rozwija także pomysły **ilmenita**, zachowując szczegółowość gór i rozdzielczość obrazu. Wynik łączny: **+42,43% PAL i +45,75% NTSC**.

[English](README.md) · [Polski](README_PL.md)

Gałąź `v12`: cartridge 128 KB dla Atari XL/XE 64 KB RAM; XEX wymaga 320 KB Rambo, 576 KB lub 1088 KB, BASIC wyłączony. Uruchamiaj od zimnego startu.

[CAR](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20128KB.car) · [ROM](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20128KB.rom) · [XEX](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20320KB-1MB.xex)

| System | Oryginał FPS | v11 FPS | v12 FPS | Zysk względem oryginału |
|---|---:|---:|---:|---:|
| PAL | 6.2717 | 8.7829 | **8.9329** | **+42.43%** |
| NTSC | 5.5915 | 8.0031 | **8.1499** | **+45.75%** |

![FPS comparison](docs/benchmarks/charts/V12_COMPARISON.png)

Wynik 50/50 to średnia średnich obu scenariuszy. v12: 155 zimnych startów na system (78 prosto, 77 z nurkowaniem), nominalnie 60 s, cztery izolowane emulatory. Nurkowanie: 1 s joystick w górę, 3 s neutralnie. Oryginał i v11 zachowują pełne referencje po 155 lotów na scenariusz i system. Naturalne wcześniejsze końce pozostają w danych. FPS oznacza ukończone obrazy terenu. To wyniki CAR; XEX ma osobne testy poprawności.

[Method](docs/benchmarks/METHOD_PL.md) · [Report](docs/benchmarks/V12_REPORT_PL.md) · [Rebuild](docs/REBUILD_PL.md)

## Co zoptymalizowano

- Dokładne dzielenie, projekcję, interpolację i wykonywanie poleceń geometrii.
- Rasteryzację profilu gór, clipping i typowe głębokości podziału.
- Kasowanie i fill, w tym bezpieczną synchronizację buforów i cache kolumn.
- PMG, wskaźniki kokpitu, mikser dźwięku i pracę VBI.
- Solo/Opus: kasowanie za wiązką, odrzucanie zasłoniętych poddrzew i skrócenie pracy przerwań.
- Zespół Solo/Fable: dzielenie inline i krótszą pętlę krawędzi projekcji.
- Astra: HD=152, lazy clear/fill bez zbędnych konwersji oraz wspólne odtwarzanie Y.
- v12: dokładny skrót `$AA`, wcześniejszy test zasłaniania, tablicę liczby grup i skan z progiem w A.
- v12: dalsze usunięcie obsługi Y w d0–d4 oraz grupowanie klasyfikacji geometrii 33–44.
- Zachowano poprawki Esc i wskaźników muzyki, które blokowały kończenie poziomu w XEX.

[Details](docs/OPTIMIZATIONS_PL.md)

## Katalogi

- **optimized version/** — Bieżące CAR, ROM, XEX i informacja o wersji.
- **original/** — Oryginalny ROM do odbudowy i porównań.
- **dist/** — Bieżąca łatka IPS i sumy kontrolne.
- **src/** — Źródła MADS; najnowsze banki w src/v12.
- **scripts/** — Narzędzia budowania, testowania i obliczeń.
- **analysis/** — Analiza oryginalnego kodu gry.
- **results/** — Wybrane dane badań; ostatnia pełna seria w results/v12.
- **docs/** — Szczegóły optymalizacji, metodyka i badania.
- **arc/up38/** — Archiwum źródeł i binariów Solo/Opus.

Starsze wydania pozostają w historii Git. Archiwalny XEX up38 ma znany błąd końca poziomu; używaj bieżącego XEX. Dokumenty: angielski bez sufiksu, polski `_PL`.
