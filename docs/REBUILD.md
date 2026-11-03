# Rebuilding v14

Requires Python 3, py65 and MADS. Builds from the original through v11 sources, then Solo up74 sources. ROM/CAR and IPS are verified byte-for-byte. No XEX is generated.

```powershell
python scripts/rebuild_current.py --mads tools/mads/bin/windows_x86_64/mads.exe
python scripts/report_v14.py
```

Solo sources: `src/up74`; generators operate on a copy in `build/`. Verification: `build/reconstruction.json`. Charts use retained observations only.
