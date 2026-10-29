# Rescue on Fractalus! — Atari XL/XE optimization

The first optimization stage was prepared by **nosty** with **ChatGPT-6 Astra** (+18%). Then **Solo**, working with a team of **Opus** agents, found further optimizations, achieving about 39%. **Astra** subsequently improved their work to reach the current result. **v12** also develops ideas from **ilmenit**, preserving terrain detail and screen resolution. Combined result: **+42.43% PAL and +45.75% NTSC**.

[English](README.md) · [Polski](README_PL.md)

Branch `v12`: 128 KB cartridge for Atari XL/XE with 64 KB RAM; XEX requires 320 KB Rambo, 576 KB or 1088 KB, with BASIC disabled. Cold-boot the new file.

[CAR](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20128KB.car) · [ROM](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20128KB.rom) · [XEX](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20320KB-1MB.xex)

| System | Original FPS | v11 FPS | v12 FPS | Gain over original |
|---|---:|---:|---:|---:|
| PAL | 6.2717 | 8.7829 | **8.9329** | **+42.43%** |
| NTSC | 5.5915 | 8.0031 | **8.1499** | **+45.75%** |

![FPS comparison](docs/benchmarks/charts/V12_COMPARISON.png)

The 50/50 result is the mean of the two scenario means. v12: 155 cold boots per system (78 straight, 77 descent), nominally 60 s, four isolated emulators. Descent: 1 s joystick up, 3 s neutral. Original and v11 retain their full references of 155 flights per scenario/system. Natural early ends remain in the data. FPS counts completed terrain images. These are CAR results; XEX has separate functional validation.

[Method](docs/benchmarks/METHOD.md) · [Report](docs/benchmarks/V12_REPORT.md) · [Rebuild](docs/REBUILD.md)

## What was optimized

- Exact division, projection, interpolation and geometry-command execution.
- Mountain-profile rasterization, clipping and common subdivision depths.
- Clearing and fill, including safe buffer synchronization and column caching.
- PMG, cockpit indicators, sound mixing and VBI work.
- Solo/Opus: beam-aware clearing, hidden-subtree rejection and shorter interrupt work.
- Solo/Fable team: inline division and a shorter projection-edge loop.
- Astra: HD=152, lazy clear/fill without redundant conversions, and shared Y restoration.
- v12: exact `$AA` shortcut, earlier occlusion check, group-count table and threshold held in A.
- v12: further Y bookkeeping removal at d0–d4 and grouped geometry classification for points 33–44.
- Esc and music-pointer fixes that prevented XEX level completion are retained.

[Details](docs/OPTIMIZATIONS.md)

## Directories

- **optimized version/** — Current CAR, ROM, XEX and version information.
- **original/** — Original ROM for rebuilding and comparisons.
- **dist/** — Current IPS patch and checksums.
- **src/** — MADS sources; latest banks in src/v12.
- **scripts/** — Build, benchmark and analysis tools.
- **analysis/** — Reverse engineering of the original game.
- **results/** — Selected research data; latest full series in results/v12.
- **docs/** — Optimization details, methodology and research.
- **arc/up38/** — Archive of Solo/Opus sources and binaries.

Earlier releases remain in Git history. The archived up38 XEX has a known level-end bug; use the current XEX. Documentation: English without a suffix, Polish with `_PL`.
