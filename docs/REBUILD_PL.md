# Budowanie v14

Wymagane: Python 3, py65 i MADS. Budowanie od oryginału przez źródła v11, następnie źródła Solo up74. Wynik ROM/CAR oraz IPS są porównywane bajt po bajcie. XEX nie jest generowany.

```powershell
python scripts/rebuild_current.py --mads tools/mads/bin/windows_x86_64/mads.exe
python scripts/report_v14.py
```

Kod Solo: `src/up74`; generatory pracują na kopii w `build/`. Wynik kontroli: `build/reconstruction.json`. Wykresy korzystają wyłącznie z zachowanych obserwacji.
