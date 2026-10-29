# Rebuilding v13

Requires Python 3, py65 and MADS. Plotting also uses numpy/matplotlib (requirements.txt).

```text
python scripts/rebuild_current.py --mads PATH_TO_MADS
```

Earlier stages are rebuilt internally from original/Rescue on Fractalus!.rom. v12 banks form the base; src/v13 contains the width-tree generator, bank selection and XEX relocation. No private ilmenit package, emulator, old release images or memory dumps are required. Both CAR/ROM, XEX and both IPS patches are verified byte-for-byte. Result: build/reconstruction.json. Generated bank ASM is in ignored build/v13/workers.

```text
python scripts/report_v13.py
python scripts/plot_v13.py
python scripts/write_v13_docs.py
```

These recreate statistics, charts and release notes from retained data. For a new series use scripts/benchmark_current.py --help and a fresh output directory; do not overwrite published observations. Install Altirra under tools/bridge or set FRACTALUS_BRIDGE_DIR.

```text
python scripts/test_v13_xex.py
python scripts/test_v13_level_transition.py candidate --release 1088k --equal
python scripts/test_v13_level_transition.py candidate --release 1088k --ntsc
```

The CPU-model scene tests used private RAM fixtures excluded from this repository; selected results are in results/v13/validation. Those fixtures are not needed to rebuild or run new native tests. XEX needs 1 MB extended RAM, 1088 KB total; both cartridges need only 64 KB.

Sound/banking repair regression, without private RAM states or FPS measurements:

```text
python scripts/test_v13_sound_fix.py
python scripts/test_v13_sound_fix.py --native
```

The second command additionally runs four Altirra cases: both CARs, PAL/NTSC, 130XE with 1088 KB RAM and sustained turns. Results go to `build/v13-sound-fix-tests.json`. Current image checksums are in `src/v13/expected.json` and `dist/`.
