# Rebuilding v12

Requires Python 3, py65 and MADS. Install requirements.txt. From the repository root:

```text
python scripts/rebuild_current.py --mads PATH_TO_MADS
```

The builder reconstructs v10.1 and v11 as internal stages, then assembles the six src/v12 banks. XEX relocates the same sources, retaining the verified loader and corrected music pointers. ROM, CAR, XEX and IPS are compared byte-for-byte with the current release. Result: build/reconstruction.json. No emulator, saved states or private research files are required.

```text
python scripts/report_v12.py
python scripts/plot_v12.py
```

These regenerate statistics and the English chart from results/v12. The bridge is needed only for new flights. Retained reference observations are historical data, not freshly run measurements when generating a report.
