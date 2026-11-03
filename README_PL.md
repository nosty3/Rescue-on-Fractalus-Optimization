# Rescue on Fractalus! — Atari XL/XE optimization

Zoptymalizowana wersja **Rescue on Fractalus!** na Atari XL/XE. Działa płynniej, zachowując grafikę i zasady oryginału. **Wersja v14 mieści się w cartridgu 128 KB i wymaga standardowych 64 KB RAM.** Nowe optymalizacje tego wydania przygotował **Solo** ze swoim zespołem agentów **Opus/Fable**.

[English](README.md) · [Polski](README_PL.md)

[CAR](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20128KB.car) · [ROM](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20128KB.rom)

Pobierz **CAR**, aby uruchomić grę w emulatorze jako cartridge, lub **ROM**, jeśli Twój sprzęt wymaga surowego obrazu. Uruchom grę od zimnego startu zamiast wczytywać zapis stanu ze starszej wersji.

| System | Oryginał FPS | v11 FPS | v14 FPS | Zysk / oryginał | Zysk / v11 |
|---|---:|---:|---:|---:|---:|
| PAL | 6.2717 | 8.7829 | **10.9172** | **+74.07%** | **+24.30%** |
| NTSC | 5.5915 | 8.0031 | **9.8961** | **+76.98%** | **+23.65%** |

Wynik 50/50: połowa średniej lotu prosto i połowa średniej lotu z nurkowaniem. Solo dostarczył 620 lotów (155 na scenariusz i system), do 60 s, zimny start, 170 ramek rozgrzewki. Niezależny audyt odtworzył dokładnie 50 wybranych lotów. Referencje oryginału i v11 są historyczne. Nie przenoszono stanów między wersjami; szybsze VBI może zmieniać losowaną planetę. Naturalne końce lotu pozostają w danych.

![PAL FPS](docs/benchmarks/charts/V14_PAL.png)

![NTSC FPS](docs/benchmarks/charts/V14_NTSC.png)

## Nowe optymalizacje Solo

- Ściślejsze odrzucanie niewidocznych poddrzew i nowa rasteryzacja gór.
- Szybsze wypełnianie kolumn bez zmiany obrazu.
- Tablicowe mnożenie, interpolacja i kolejka dźwięku w VBI.
- Szybsza geometria siatki, jej przygotowanie i etap końcowy.
- Szybsze rzutowanie i pętla krawędzi.
- Bezpieczna część rzutowania wykonywana podczas oczekiwania na poprzedni obraz.

[Details / Szczegóły](docs/OPTIMIZATIONS_PL.md) · [Method / Metodyka](docs/benchmarks/METHOD_PL.md) · [Audit / Audyt](docs/benchmarks/UP74_INTEGRATION_AUDIT_PL.md) · [Build](docs/REBUILD_PL.md)

## Katalogi

- optimized version/ — aktualne CAR, ROM i informacja o wydaniu.
- original/ — oryginalny ROM.
- dist/ — łatka IPS od oryginału oraz sumy kontrolne.
- src/ — źródła; nowe prace Solo w src/up74.
- scripts/ — budowanie, pomiary i wykresy.
- results/ — wyniki; bieżące w results/v14.
- docs/ — opis zmian, metodyka i badania.
- analysis/ — inżynieria wsteczna oryginału.
- arc/ — historyczne materiały up38.

## Autorzy

Pierwszy etap optymalizacji przygotował **nosty** z **ChatGPT-6 Astra** (+18%). Następnie **Solo** z zespołem **Opus** osiągnął około 39%, a **Astra** rozwinęła te prace w v11. Kolejny duży przyrost wydajności w v14 jest dziełem **Solo** i jego zespołu **Opus/Fable**. Te historyczne procenty nie sumują się.
