# Rescue on Fractalus! — Atari XL/XE optimization

[English](README.md) · [Polski](README_PL.md)

Reverse engineering and 6502 assembly optimization of **Rescue on Fractalus!** for Atari XL/XE. The latest build, **v10**, uses a **128 KB XEGS cartridge** and runs on PAL and NTSC machines with 64 KB RAM, preserving the terrain detail and screen resolution.

## Download

Open **[optimized version](optimized%20version/)** for the latest `.car`, raw `.rom`, and a short version note. Use the `.car` in an emulator; for the raw ROM, select **XEGS 128 KB / cartridge type 14**. Start with a cold boot.

## Measured performance

| System | Original | v10 | Gain vs. original |
| --- | ---: | ---: | ---: |
| PAL | 6.4421 FPS | 7.6359 FPS | **+18.53%** |
| NTSC | 5.8043 FPS | 6.9377 FPS | **+19.53%** |

These are means of **155 flights per version and system**, each lasting up to 60 seconds, from a fresh emulator process and cold boot. v10 uses a new series; the original uses the historical reference series. Historical control flights were reproduced on the same emulator. Four isolated emulator processes were validated for parallel measurement. No saved states were transferred and no outliers were discarded. The [v10 report](docs/benchmarks/RAPORT_V10_PL.md) includes confidence intervals and a historical comparison with the preceding release (in Polish).

FPS counts completed terrain images, not the video refresh rate. The test uses automatic flight with a centered joystick; it does not cover turns or dives. Flights that ended naturally before 60 seconds remain in the sample. See the [measurement method and reports](docs/benchmarks/METODA_PL.md) for details (in Polish).

### PAL

![PAL FPS distribution](docs/benchmarks/charts/FPS_DISTRIBUTION_PAL_EN.png)
![PAL flight duration](docs/benchmarks/charts/FLIGHT_DURATION_PAL_EN.png)

### NTSC

![NTSC FPS distribution](docs/benchmarks/charts/FPS_DISTRIBUTION_NTSC_EN.png)
![NTSC flight duration](docs/benchmarks/charts/FLIGHT_DURATION_NTSC_EN.png)

## What was optimized

- Reordered the terrain rasterizer and removed redundant work after subdivision.
- Accelerated exact integer division and removed unnecessary normalization.
- Specialized mountain profile generation for common depths and widths.
- Aligned plotter row-address tables to avoid page-cross penalties and removed redundant Y-register stores.
- Skipped terrain subdivisions only when a conservative visibility bound proves them hidden.
- Used additional ROM banks for direct screen clearing and specialized terrain filling.
- Replaced repeated geometry command interpretation with specialized code and lookup tables.
- Added fast clipping paths with the original algorithm as a fallback.
- Accelerated interpolation with exact lookup tables and self-modifying code in RAM.
- Unrolled sound mixing loops and removed redundant sound flag clearing.
- Updated only changed PMG bar segments and shortened PMG drawing and erasing loops.
- Protected bank switching across interrupts and fixed display-buffer synchronization to prevent transient terrain artifacts.

See the [complete technical description](docs/OPTYMALIZACJE_PL.md) and [rebuild instructions](docs/ODTWORZENIE_PL.md) (in Polish).

## Repository layout

- **[optimized version/](optimized%20version/)** — the latest playable CAR and ROM, plus version and performance information.
- **[original/](original/)** — the unchanged original ROM used as build input and benchmark reference.
- **[dist/](dist/)** — distribution support files: the current IPS patch and build manifest.
- **[src/](src/)** — MADS assembly sources for the optimizations and experiments.
- **[scripts/](scripts/)** — reconstruction, analysis, validation, benchmark, and plotting tools.
- **[analysis/](analysis/)** — disassembly and code analysis supporting the reverse engineering.
- **[results/](results/)** — selected machine-readable measurements and verification results, including historical research.
- **[docs/](docs/)** — the consolidated change description and research grouped by topic, including PMG, terrain, and benchmarks.

Older release binaries and release notes remain in Git history. Research documents are in Polish and use `_PL` filenames. Emulator binaries, saved states, memory dumps, and test screenshots are not included.
