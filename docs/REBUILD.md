# Rebuilding v11 from source

[English](REBUILD.md) · [Polski](REBUILD_PL.md)

Requires Python 3, py65 and MADS. Install requirements.txt for plotting dependencies as well. No emulator or saved states are required to rebuild the game.

```powershell
python -m pip install -r requirements.txt
python scripts/rebuild_current.py --mads tools/mads/bin/windows_x86_64/mads.exe
```

The builder reconstructs v10.1 from the original as an internal stage, runs the up38 generators in ignored build/up38, then assembles the four src/v11 banks. Archived sources remain untouched. It produces ROM/CAR and XEX with corrected music pointers. Every output is compared byte-for-byte with optimized version/, and IPS is applied to the original for verification. Result: build/reconstruction.json. Hashes: dist/build-manifest.json.

v11 ROM: ec01982121b70baca35f04568617965c3164e716e0a5eb3c6ebcbb123566a868.
Fixed XEX: ac0c217074d52a4db6163ad94339031e4610e9a99a5c7d02f629c6b34ce9a20b.
No files from the old local workspace are needed. Historical research scripts may still require unpublished fixtures; they are distinct from the current builder.

```powershell
python scripts/report_v11.py
```

This regenerates English charts without an emulator, using retained individual observations. New measurements: scripts/benchmark_v11.py --help and benchmarks/METHOD.md. Headless Altirra and MADS are external tools; previously used tool identities are in docs/tools and results/v11 plans. Do not overwrite published observations with a new series under the same names.

XEX requires 320 KB Rambo, 576 KB or 1088 KB, compatible PORTB banking and disabled BASIC. Cartridge builds need only 64 KB RAM. Cold-boot new files instead of loading an old emulator save state.

After installing Altirra and rebuilding, functional tests: `python scripts/test_v11_xex.py` and `python scripts/test_v11_level_transition.py candidate --release` (optional `--ntsc`, `576k`, `1088k`, `--equal`).
