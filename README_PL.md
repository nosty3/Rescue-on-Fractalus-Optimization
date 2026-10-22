# Rescue on Fractalus! — optymalizacja dla Atari XL/XE

[English](README.md) · [Polski](README_PL.md)

Inżynieria wsteczna i optymalizacja w asemblerze 6502 gry **Rescue on Fractalus!** dla Atari XL/XE. Najnowszy build, **v9**, wykorzystuje **cartridge XEGS 128 KB** i działa na komputerach PAL i NTSC z 64 KB RAM, zachowując szczegółowość terenu i rozdzielczość obrazu.

## Pobieranie

W katalogu **[optimized version](optimized%20version/)** znajdują się najnowsze pliki `.car`, surowy `.rom` i krótka informacja o wersji. W emulatorze użyj `.car`; dla surowego ROM-u wybierz **XEGS 128 KB / typ cartridge'a 14**. Uruchom grę od zimnego startu.

## Zmierzona wydajność

| System | Oryginał | Zoptymalizowana v9 | Przyrost |
| --- | ---: | ---: | ---: |
| PAL | 6,4421 FPS | 7,5623 FPS | **+17,39%** |
| NTSC | 5,8043 FPS | 6,8977 FPS | **+18,84%** |

Są to średnie ze **155 niezależnych lotów dla każdej wersji i systemu**, trwających do 60 sekund, uruchamianych w nowym procesie emulatora od zimnego startu. Cztery odizolowane procesy emulatora zweryfikowano pod kątem pomiaru równoległego. Nie przenoszono zapisanych stanów ani nie odrzucano wyników odstających. 95-procentowe przedziały ufności przyrostu wynoszą **16,46–18,32% (PAL)** i **17,90–19,78% (NTSC)**.

FPS oznacza liczbę ukończonych obrazów terenu, a nie częstotliwość odświeżania obrazu. Test obejmuje automatyczny lot z joystickiem w położeniu neutralnym; nie obejmuje skrętów ani nurkowania. Loty zakończone naturalnie przed upływem 60 sekund pozostają w próbie. Szczegóły zawierają [metoda pomiaru i raporty](docs/benchmarks/METODA_PL.md) (po polsku).

### PAL

![Rozkład FPS dla PAL](docs/benchmarks/charts/FPS_DISTRIBUTION_PAL_EN.png)
![Czas lotu dla PAL](docs/benchmarks/charts/FLIGHT_DURATION_PAL_EN.png)

### NTSC

![Rozkład FPS dla NTSC](docs/benchmarks/charts/FPS_DISTRIBUTION_NTSC_EN.png)
![Czas lotu dla NTSC](docs/benchmarks/charts/FLIGHT_DURATION_NTSC_EN.png)

## Co zoptymalizowano

- Zmieniono kolejność operacji rasteryzatora terenu i usunięto zbędną pracę po podziale odcinka.
- Przyspieszono dokładne dzielenie całkowitoliczbowe i usunięto zbędną normalizację.
- Wyspecjalizowano generowanie profilu gór dla typowych głębokości i szerokości.
- Pominięto podziały terenu tylko tam, gdzie zachowawcza granica widoczności dowodzi ich całkowitego zasłonięcia.
- Wykorzystano dodatkowe banki ROM do bezpośredniego kasowania ekranu i wyspecjalizowanego wypełniania terenu.
- Zastąpiono powtarzane interpretowanie poleceń geometrii wyspecjalizowanym kodem i tablicami.
- Dodano szybkie ścieżki przycinania z oryginalnym algorytmem jako ścieżką zapasową.
- Przyspieszono interpolację za pomocą dokładnych tablic i samomodyfikującego się kodu w RAM.
- Rozwinięto pętle miksowania dźwięku i usunięto zbędne zerowanie flag dźwięku.
- Ograniczono aktualizację pasków PMG do zmienionych odcinków i skrócono pętle rysowania oraz kasowania PMG.
- Zabezpieczono przełączanie banków podczas przerwań i naprawiono synchronizację buforów obrazu, aby zapobiegać chwilowym artefaktom terenu.

Zobacz [pełny opis techniczny](docs/OPTYMALIZACJE_PL.md) i [instrukcję odtworzenia](docs/ODTWORZENIE_PL.md) (po polsku).

## Zawartość repozytorium

- **[optimized version/](optimized%20version/)** — najnowsze pliki CAR i ROM do uruchomienia oraz informacje o wersji i wydajności.
- **[original/](original/)** — niezmieniony oryginalny ROM, używany do budowania i jako punkt odniesienia pomiarów.
- **[dist/](dist/)** — pomocnicze pliki dystrybucji: aktualna łatka IPS i manifest buildu.
- **[src/](src/)** — źródła asemblera MADS dla optymalizacji i eksperymentów.
- **[scripts/](scripts/)** — narzędzia odtwarzania, analizy, weryfikacji, pomiarów i tworzenia wykresów.
- **[analysis/](analysis/)** — deasemblacja i analiza kodu wspierające inżynierię wsteczną.
- **[results/](results/)** — wybrane pomiary i wyniki weryfikacji w formacie maszynowym, w tym badania historyczne.
- **[docs/](docs/)** — zbiorczy opis zmian oraz badania pogrupowane tematycznie, m.in. PMG, teren i pomiary.

Starsze pliki wydań i ich opisy pozostają w historii Gita. Dokumenty badawcze są po polsku i mają nazwy z `_PL`. Repozytorium nie zawiera emulatorów, zapisanych stanów, zrzutów pamięci ani screenów z testów.
