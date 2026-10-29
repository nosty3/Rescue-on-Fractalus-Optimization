# Odbudowa v12

Wymagane Python 3, py65 i MADS. Zainstaluj requirements.txt. Z głównego folderu repo:

```text
python scripts/rebuild_current.py --mads PATH_TO_MADS
```

Builder odtwarza v10.1 i v11 jako etapy wewnętrzne, następnie asembluje sześć banków src/v12. XEX powstaje przez relokację tych samych źródeł, z zachowaniem sprawdzonego loadera i poprawionych wskaźników muzyki. ROM, CAR, XEX i IPS porównywane są bajtowo z bieżącym wydaniem. Wynik: build/reconstruction.json. Bez emulatora, zapisów stanu ani prywatnych plików badawczych.

```text
python scripts/report_v12.py
python scripts/plot_v12.py
```

Te polecenia odtwarzają obliczenia i angielski wykres z danych w results/v12. Instalacja bridge potrzebna jest tylko do nowych lotów. Pełne wcześniejsze wyniki pozostają danymi historycznymi, nie są nowymi pomiarami przy uruchomieniu raportu.
