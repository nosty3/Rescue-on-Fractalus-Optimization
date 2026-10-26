# Rebuilding the current ROM and continuing development

[English](REBUILD.md) · [Polski](REBUILD_PL.md)

## Building v10.1

Python 3 and [MADS](https://github.com/tebe6502/Mad-Assembler) are required. Neither an emulator nor saved states are needed to build the game. Install tools locally in `tools/`; this directory is not versioned. Details of the MADS and emulator versions used are in [tools/TOOLS.json](tools/TOOLS.json) and [tools/ALTIRRA-BUILD-INFO.txt](tools/ALTIRRA-BUILD-INFO.txt).

From the repository root, run:

```powershell
python scripts/rebuild_current.py --mads .\tools\mads\bin\windows_x86_64\mads.exe
```

The builder reads `original/Rescue on Fractalus!.rom`, assembles the MADS sources, applies patches, and creates the final ROM/CAR in the ignored `build/` directory. It checks them against the files in `optimized version/` and also applies `dist/fractalus-optimized-128KB.ips` to the original as a verification step. The report is written to `build/reconstruction.json`. Checksums are listed in [dist/build-manifest.json](../dist/build-manifest.json).

The v1–v9 binaries are not required. Intermediate stages exist in the builder's memory and are checked against known hashes; they are not published as additional releases. The old `rebuild_*.py` scripts remain aliases for building the current version. To investigate a historical release using its original scripts, check out the corresponding Git commit.

## Research workflow

Documentation now uses English filenames, with `_PL` retained for Polish versions. Historical packaging scripts and some diagnostic messages still mention former document names (for example, `ODTWORZENIE_PL.md` now corresponds to `REBUILD_PL.md`). These scripts were left unchanged; use the current instructions here and the historical Git revision when reproducing an old packaging workflow.

[OPTIMIZATIONS.md](OPTIMIZATIONS.md) describes the current implementation. Other sources and scripts also preserve experiments and comparative tests. Not every historical `build_*`, `test_*`, or `benchmark_*` script will run without preparation: some expect historical builds or local fixtures deliberately excluded from this repository. Names such as `v7` or `opt14` identify implementations in the sources, not additional downloadable game releases.

Do not remove the VBI guard, the wait for buffer switching, or fallback paths solely on the strength of a CPU microtest. First compare a new change using identical routine inputs, then test it in the full emulator with DMA and interrupts. Document which bytes are live outputs and which are dead scratch memory. Assess complete flights separately from individual routine equivalence.

## Data, charts, and emulator

`python -m pip install -r requirements.txt` installs the analysis libraries. The English charts can be reproduced without an emulator:

```powershell
python scripts/report_v10.py --published-data
```

The analysis script reads the historical series and `results/v10/`, writing PNG/SVG charts to `results/v10/pal/` and `results/v10/ntsc/`. Published copies are in `docs/benchmarks/charts/`. Checking all local event hashes requires unpublished diagnostic files; use `--published-data` to analyze the retained aggregates.

For new flights, download the [Altirra headless bridge](https://github.com/ilmenit/AltirraSDL/releases/tag/nightly-bridge) and extract it into `tools/bridge/<package>/`, containing `AltirraBridgeServer.exe` and `sdk/python/altirra_bridge`. The nightly build may change: compare the emulator hash with the recorded protocol and repeat validation if it differs. The isolation mechanism sets TEMP/TMP to the local `tools` directory, launches windowless servers, and assigns separate ports and tokens.

The main tools are `benchmark_ntsc_isolated.py`, `validate_ntsc_parallel.py`, `benchmark_ntsc_parallel.py`, and `benchmark_pal_parallel.py` (with `--validate`). The retained results form a completed series: the scripts can resume it, rather than automatically start a new one. Run a new experiment in a separate working copy, preserving the published data; prepare empty output directories there and copy the frozen plan when repeating the same schedule. Do not overwrite an existing series while presenting it as a new measurement.

The full [protocol](benchmarks/METHOD.md) and JSON plans define the order and conditions. PAL uses the NTSC plan. Parallel execution is validated before measurement flights; only matching results justify using four processes. Memory and event dumps may be generated locally for validation, but should not be added to the repository. Published hashes and aggregates document the study; they do not replace the omitted dumps when rechecking every byte.

## Repeating v10

The builder also creates `build/reference-v9.car` solely as a historical control in the ignored directory. `pal_v9_common.py` and `ntsc_v9_common.py` point to this file so that older tools do not accidentally use v10 as v9. To run a new series: `benchmark_v10.py --validate`, then `benchmark_v10.py`. Retained completed results are resumed, not overwritten. For an independent replication, prepare a separate copy of the results and an empty destination directory.

## v10.1 pause fix

The builder assembles and applies `src/pause_resume_stack.asm`. The final ROM differs from v10 by one byte. It retains `build/reference-v10.car` only in the ignored directory so that the historical `benchmark_v10.py` script still targets the exact version that was measured. No FPS tests were run for v10.1.
