# Odtworzenie aktualnego ROM-u i dalsza praca

## Budowanie v9

Wymagane są Python 3 oraz [MADS](https://github.com/tebe6502/Mad-Assembler). Emulator ani zapisane stany nie są potrzebne do budowania. Narzędzia instaluj lokalnie w `tools/`; katalog nie jest wersjonowany. Informacje o użytym MADS i emulatorze są w [tools/TOOLS.json](tools/TOOLS.json) oraz [tools/ALTIRRA-BUILD-INFO.txt](tools/ALTIRRA-BUILD-INFO.txt).

Z katalogu głównego repozytorium wykonaj:

```powershell
python scripts/rebuild_current.py --mads .\tools\mads\bin\windows_x86_64\mads.exe
```

Builder czyta `original/Rescue on Fractalus!.rom`, kompiluje źródła MADS, nakłada poprawki i tworzy końcowe ROM/CAR w ignorowanym katalogu `build/`. Sprawdza ich zgodność z plikami w `optimized version/` oraz kontrolnie stosuje `dist/fractalus-optimized-128KB.ips` do oryginału. Raport zapisuje w `build/reconstruction.json`. Zestaw sum kontrolnych jest w [dist/build-manifest.json](../dist/build-manifest.json).

Nie są potrzebne binaria v1–v8. Etapy pośrednie istnieją w pamięci buildera, z kontrolą znanych hashy; nie są publikowane jako dodatkowe wydania. Dawne `rebuild_*.py` pozostają aliasami budowania aktualnej wersji. Aby badać historyczne wydanie z jego dawnymi skryptami, należy wybrać odpowiedni commit Gita.

## Układ pracy badawczej

Aktualną implementację opisuje [OPTYMALIZACJE_PL.md](OPTYMALIZACJE_PL.md). Pozostałe źródła i skrypty zachowują również eksperymenty oraz testy porównawcze. Nie każdy dawny `build_*`, `test_*` czy `benchmark_*` uruchomi się bez przygotowania: część oczekuje historycznych buildów lub lokalnych fixtures, które świadomie nie należą do repozytorium. Nazwy `v7` czy `opt14` w źródłach identyfikują implementację i nie oznaczają dodatkowego pliku gry do pobrania.

Nie usuwaj osłony VBI, czekania na przełączenie bufora ani ścieżek zapasowych na podstawie samego mikrotestu CPU. Nową zmianę porównuj najpierw na identycznych wejściach procedury, a następnie w pełnym emulatorze z DMA i przerwaniami. Dokumentuj, które bajty są żywymi wynikami, a które martwą pamięcią roboczą. Oceniaj cały lot osobno od zgodności pojedynczej procedury.

## Dane, wykresy i emulator

`python -m pip install -r requirements.txt` instaluje biblioteki analityczne. Wykresy angielskie można odtworzyć bez emulatora:

```powershell
python scripts/plot_ntsc_english.py --video ntsc
python scripts/plot_ntsc_english.py --video pal
```

Skrypt zapisuje PNG i SVG w `docs/benchmarks/charts/`, czytając zachowane `results/ntsc_isolated_main/benchmark.json` i `results/pal_isolated_main/benchmark.json`.

Do nowych lotów pobierz [Altirra headless bridge](https://github.com/ilmenit/AltirraSDL/releases/tag/nightly-bridge) i rozpakuj pakiet w `tools/bridge/<pakiet>/`, tak aby zawierał `AltirraBridgeServer.exe` oraz `sdk/python/altirra_bridge`. Wersja nightly może się zmienić: porównaj hash emulatora z zapisanym protokołem i ponów walidację, jeśli jest inny. Mechanizm izolacji ustawia TEMP/TMP w lokalnym `tools`, uruchamia serwery bez okien i nadaje osobne porty oraz tokeny.

Główne narzędzia to `benchmark_ntsc_isolated.py`, `validate_ntsc_parallel.py`, `benchmark_ntsc_parallel.py` oraz `benchmark_pal_parallel.py` (opcja `--validate`). Zachowane wyniki stanowią ukończoną serię: skrypty umieją ją wznawiać, a nie automatycznie zaczynać nową. Nowy eksperyment wykonuj w osobnej kopii roboczej, zachowując opublikowane dane; przygotuj tam puste katalogi wynikowe i skopiuj zamrożony plan, gdy potrzebne jest powtórzenie tego samego harmonogramu. Nie nadpisuj istniejącej serii pod pozorem nowego pomiaru.

Pełny [protokół](benchmarks/METODA_PL.md) oraz plany w JSON określają kolejność i warunki. PAL korzysta z planu NTSC. Walidację równoległości wykonuje się przed lotami pomiarowymi; dopiero jej zgodność uprawnia do czterech procesów. Zrzuty pamięci i zdarzeń mogą powstawać lokalnie na potrzeby walidacji, ale nie należy dodawać ich do repozytorium. Opublikowane hashe i agregaty dokumentują badanie; nie zastępują nieprzechowywanych zrzutów przy ponownej kontroli każdego bajtu.
