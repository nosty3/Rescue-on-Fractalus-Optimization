# Budowanie v14

Wymagane: Python 3, py65 i MADS. Budowanie od oryginału przez źródła v11, następnie źródła Solo v14. Wynik ROM/CAR oraz IPS są porównywane bajt po bajcie. XEX nie jest generowany.

```powershell
python scripts/rebuild_current.py --mads tools/mads/bin/windows_x86_64/mads.exe
python scripts/report_v14.py
```

Kod Solo: `src/v14`; generatory pracują na kopii w `build/`. Wynik kontroli: `build/reconstruction.json`. Wykresy korzystają wyłącznie z zachowanych obserwacji.
