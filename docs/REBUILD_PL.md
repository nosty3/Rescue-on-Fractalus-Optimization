# Odtworzenie aktualnego ROM-u i dalsza praca

[English](REBUILD.md) · [Polski](REBUILD_PL.md)

## Budowanie v10.1

Wymagane są Python 3 oraz [MADS](https://github.com/tebe6502/Mad-Assembler). Emulator ani zapisane stany nie są potrzebne do budowania. Narzędzia instaluj lokalnie w `tools/`; katalog nie jest wersjonowany. Informacje o użytym MADS i emulatorze są w [tools/TOOLS.json](tools/TOOLS.json) oraz [tools/ALTIRRA-BUILD-INFO.txt](tools/ALTIRRA-BUILD-INFO.txt).

Z katalogu głównego repozytorium wykonaj:

```powershell
python scripts/rebuild_current.py --mads .\tools\mads\bin\windows_x86_64\mads.exe
```

Builder czyta `original/Rescue on Fractalus!.rom`, kompiluje źródła MADS, nakłada poprawki i tworzy końcowe ROM/CAR w ignorowanym katalogu `build/`. Sprawdza ich zgodność z plikami w `optimized version/` oraz kontrolnie stosuje `dist/fractalus-optimized-128KB.ips` do oryginału. Raport zapisuje w `build/reconstruction.json`. Zestaw sum kontrolnych jest w [dist/build-manifest.json](../dist/build-manifest.json).

Nie są potrzebne binaria v1–v9. Etapy pośrednie istnieją w pamięci buildera, z kontrolą znanych hashy; nie są publikowane jako dodatkowe wydania. Dawne `rebuild_*.py` pozostają aliasami budowania aktualnej wersji. Aby badać historyczne wydanie z jego dawnymi skryptami, należy wybrać odpowiedni commit Gita.

## Układ pracy badawczej

Dokumentacja ma teraz angielskie nazwy plików, z sufiksem `_PL` dla wersji polskich. Historyczne skrypty pakowania i niektóre komunikaty diagnostyczne nadal wymieniają dawne nazwy dokumentów (np. `ODTWORZENIE_PL.md` odpowiada teraz `REBUILD_PL.md`). Skrypty pozostawiono bez zmian; korzystaj z aktualnej instrukcji tutaj, a do odtworzenia dawnego procesu pakowania użyj historycznej rewizji Gita.

Aktualną implementację opisuje [OPTIMIZATIONS_PL.md](OPTIMIZATIONS_PL.md). Pozostałe źródła i skrypty zachowują również eksperymenty oraz testy porównawcze. Nie każdy dawny `build_*`, `test_*` czy `benchmark_*` uruchomi się bez przygotowania: część oczekuje historycznych buildów lub lokalnych fixtures, które świadomie nie należą do repozytorium. Nazwy `v7` czy `opt14` w źródłach identyfikują implementację i nie oznaczają dodatkowego pliku gry do pobrania.

Nie usuwaj osłony VBI, czekania na przełączenie bufora ani ścieżek zapasowych na podstawie samego mikrotestu CPU. Nową zmianę porównuj najpierw na identycznych wejściach procedury, a następnie w pełnym emulatorze z DMA i przerwaniami. Dokumentuj, które bajty są żywymi wynikami, a które martwą pamięcią roboczą. Oceniaj cały lot osobno od zgodności pojedynczej procedury.

## Dane, wykresy i emulator

`python -m pip install -r requirements.txt` instaluje biblioteki analityczne. Wykresy angielskie można odtworzyć bez emulatora:

```powershell
python scripts/report_v10.py --published-data
```

Skrypt analityczny czyta serie historyczne oraz `results/v10/`, zapisuje wykresy PNG/SVG w `results/v10/pal/` i `results/v10/ntsc/`. Publiczne kopie są w `docs/benchmarks/charts/`. Kontrola wszystkich lokalnych hashy zdarzeń wymaga niepublikowanych plików diagnostycznych; użyj `--published-data` do analizy zachowanych agregatów.

Do nowych lotów pobierz [Altirra headless bridge](https://github.com/ilmenit/AltirraSDL/releases/tag/nightly-bridge) i rozpakuj pakiet w `tools/bridge/<pakiet>/`, tak aby zawierał `AltirraBridgeServer.exe` oraz `sdk/python/altirra_bridge`. Wersja nightly może się zmienić: porównaj hash emulatora z zapisanym protokołem i ponów walidację, jeśli jest inny. Mechanizm izolacji ustawia TEMP/TMP w lokalnym `tools`, uruchamia serwery bez okien i nadaje osobne porty oraz tokeny.

Główne narzędzia to `benchmark_ntsc_isolated.py`, `validate_ntsc_parallel.py`, `benchmark_ntsc_parallel.py` oraz `benchmark_pal_parallel.py` (opcja `--validate`). Zachowane wyniki stanowią ukończoną serię: skrypty umieją ją wznawiać, a nie automatycznie zaczynać nową. Nowy eksperyment wykonuj w osobnej kopii roboczej, zachowując opublikowane dane; przygotuj tam puste katalogi wynikowe i skopiuj zamrożony plan, gdy potrzebne jest powtórzenie tego samego harmonogramu. Nie nadpisuj istniejącej serii pod pozorem nowego pomiaru.

Pełny [protokół](benchmarks/METHOD_PL.md) oraz plany w JSON określają kolejność i warunki. PAL korzysta z planu NTSC. Walidację równoległości wykonuje się przed lotami pomiarowymi; dopiero jej zgodność uprawnia do czterech procesów. Zrzuty pamięci i zdarzeń mogą powstawać lokalnie na potrzeby walidacji, ale nie należy dodawać ich do repozytorium. Opublikowane hashe i agregaty dokumentują badanie; nie zastępują nieprzechowywanych zrzutów przy ponownej kontroli każdego bajtu.

## Powtórzenie v10

Builder tworzy także `build/reference-v9.car` wyłącznie jako historyczną kontrolę w ignorowanym katalogu. Skrypty `pal_v9_common.py` i `ntsc_v9_common.py` wskazują ten plik, aby starsze narzędzia nie używały omyłkowo v10 jako v9. Nowa seria: `benchmark_v10.py --validate`, następnie `benchmark_v10.py`. Zachowane ukończone wyniki są wznawiane, nie nadpisywane. Aby wykonać niezależną replikację, przygotuj osobną kopię wyników i pusty katalog docelowy.

## Poprawka pauzy v10.1

`src/pause_resume_stack.asm` jest kompilowany i nakładany przez builder. Końcowy ROM ma jeden zmieniony bajt względem v10. Builder zachowuje `build/reference-v10.car` wyłącznie w ignorowanym katalogu, aby historyczny skrypt `benchmark_v10.py` nadal wskazywał dokładnie zmierzoną wersję. Nie wykonywano testów FPS v10.1.
