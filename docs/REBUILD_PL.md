# Odtwarzanie v11 ze źródeł

[English](REBUILD.md) · [Polski](REBUILD_PL.md)

Potrzebujesz Python 3, py65 oraz MADS. Dla wykresów zainstaluj także zależności z requirements.txt. Nie potrzeba emulatora ani zapisów stanu do przebudowania gry.

```powershell
python -m pip install -r requirements.txt
python scripts/rebuild_current.py --mads tools/mads/bin/windows_x86_64/mads.exe
```

Builder odtwarza v10.1 z oryginału jako etap wewnętrzny, uruchamia generatory up38 w ignorowanym build/up38, a następnie asembluje cztery banki src/v11. Archiwalne źródła pozostają nienaruszone. Powstają ROM/CAR i XEX z poprawionymi wskaźnikami melodii. Każdy wynik jest porównywany bajt w bajt z optimized version/, a IPS nakładany kontrolnie na oryginał. Wynik: build/reconstruction.json. Hashe: dist/build-manifest.json.

Pełny ROM v11: ec01982121b70baca35f04568617965c3164e716e0a5eb3c6ebcbb123566a868.
Poprawiony XEX: ac0c217074d52a4db6163ad94339031e4610e9a99a5c7d02f629c6b34ce9a20b.
Nie są wymagane lokalne pliki z dawnego katalogu roboczego. Historyczne skrypty badawcze mogą natomiast wymagać niepublikowanych fixture; nie myl ich z aktualnym builderem.

```powershell
python scripts/report_v11.py
```

To odtwarza angielskie wykresy bez emulatora z zachowanych pojedynczych obserwacji. Nowe pomiary: scripts/benchmark_v11.py --help i metodyka benchmarks/METHOD_PL.md. Headless Altirra i MADS są narzędziami zewnętrznymi; identyfikatory wcześniej użytych wersji znajdują się w docs/tools oraz planach results/v11. Nie zastępuj opublikowanych obserwacji nową serią pod tymi samymi nazwami.

XEX wymaga 320 KB Rambo, 576 KB albo 1088 KB, zgodnego PORTB i wyłączonego BASIC-a. Wersja kartridżowa wymaga tylko 64 KB RAM. Należy uruchamiać nowy plik od początku, nie ze starego zapisu emulatora.

Testy funkcjonalne po przygotowaniu Altirry i przebudowaniu: `python scripts/test_v11_xex.py` oraz `python scripts/test_v11_level_transition.py candidate --release` (opcjonalnie `--ntsc`, `576k`, `1088k`, `--equal`).
