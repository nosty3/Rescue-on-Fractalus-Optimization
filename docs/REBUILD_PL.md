# Odbudowa v13

Wymagane Python 3, py65 i MADS. Wykresy korzystają też z numpy/matplotlib (requirements.txt).

```text
python scripts/rebuild_current.py --mads PATH_TO_MADS
```

Wcześniejsze etapy są odtwarzane wewnętrznie od original/Rescue on Fractalus!.rom. Banki v12 tworzą bazę; src/v13 zawiera generator drzew, wybór banków i relokację XEX. Nie wymaga prywatnej paczki ilmenita, emulatora, starych obrazów wydań ani zrzutów pamięci. Oba CAR/ROM, XEX i obie łatki IPS są sprawdzane bajt w bajt. Wynik: build/reconstruction.json. Generowane źródła ASM są w ignorowanym build/v13/workers.

```text
python scripts/report_v13.py
python scripts/plot_v13.py
python scripts/write_v13_docs.py
```

Polecenia odtwarzają statystyki, wykres i opisy z zachowanych danych. Nowa seria: scripts/benchmark_current.py --help i świeży katalog wynikowy; nie nadpisuj opublikowanych obserwacji. Zainstaluj Altirrę pod tools/bridge lub ustaw FRACTALUS_BRIDGE_DIR.

```text
python scripts/test_v13_xex.py
python scripts/test_v13_level_transition.py candidate --release 1088k --equal
python scripts/test_v13_level_transition.py candidate --release 1088k --ntsc
```

Modelowe testy scen korzystały z prywatnych zapisów RAM, wyłączonych z repo; wybrane wyniki są w results/v13/validation. Nie są one potrzebne do odbudowy ani nowych testów natywnych. XEX wymaga rozszerzenia 1 MB RAM, 1088 KB łącznie; oba cartridge’e tylko 64 KB.
