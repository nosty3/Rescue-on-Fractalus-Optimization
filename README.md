# Rescue on Fractalus! — Atari XL/XE optimization

The first optimization stage was prepared by **nosty** with **ChatGPT-6 Astra** (+18%). Then **Solo**, working with a team of **Opus** agents, found further optimizations, achieving about 39%. **Astra** subsequently improved their work to reach the current result. **v13** adds width-specific compiled subdivision trees from **ilmenit**'s ideas, on top of v12.

[English](README.md) · [Polski](README_PL.md)

Both cartridges run on an Atari XL/XE with the standard 64 KB RAM. The 512 KB XEX requires a 1 MB expansion (1088 KB total), compatible PORTB banking and BASIC disabled. The 1 MB cartridge has no XEX with this loader layout. For a 320/576 KB XEX use [branch v12](https://github.com/nosty3/Rescue-on-Fractalus-Optimization/tree/v12). Cold-boot new files.

- [CAR 512 KB](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20512KB.car) / [ROM 512 KB](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20512KB.rom)
- [CAR 1 MB](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%201024KB.car) / [ROM 1 MB](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%201024KB.rom)
- [XEX 512 KB — 1 MB RAM](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20512KB%20-%201MB%20RAM.xex)

| System | Variant | FPS | Gain over original | Gain over v11 |
|---|---|---:|---:|---:|
| PAL | 512 KB | **9.2791** | **+47.95%** | **+5.65%** |
| PAL | 1 MB | **9.3856** | **+49.65%** | **+6.86%** |
| NTSC | 512 KB | **8.4698** | **+51.48%** | **+5.83%** |
| NTSC | 1 MB | **8.5354** | **+52.65%** | **+6.65%** |

![FPS comparison](docs/benchmarks/charts/V13_COMPARISON.png)

The 50/50 result is half of the straight-flight mean and half of the descent mean. Each v13 variant: 155 PAL cold boots and 155 NTSC, with 78 straight and 77 descent, nominally 60 s. Total: 620 new flights in four isolated emulators. Same plan as v12; all initial maps match. Original retains the full historical 155+155 reference per system. Natural early ends remain in the data. FPS measures CAR; XEX passed separate functional validation.

[Method](docs/benchmarks/METHOD.md) · [Full report](docs/benchmarks/V13_REPORT.md) · [Ilmenit ideas](docs/ILMENIT_IDEAS.md)

## What was optimized

- Exact division, projection, interpolation, geometry, clipping and common mountain-profile depths.
- Clearing and fill: safe buffers, beam-aware wait, lazy clear and per-column caching.
- PMG, cockpit indicators, sound mixing and VBI interrupt work.
- Solo/Opus/Fable: hidden subtrees, beam-aware clearing and inline projection division.
- Astra: HD=152, fewer height conversions, threshold held in A and shared Y restoration.
- v12: exact `$AA` shortcut, group-count table, earlier scan test, further Y removal and shorter geometry classification.
- v13: compiled trees for selected widths and clipping, with exact v12 fallback.
- v13: selective occlusion tests inside trees and HD/lazy-clear integration for every accepted write.
- v13 XEX: 62 extended pages, a 1 MB RAM check and VBI restoration of all new banks; Esc and level-end fixes retained.

[Details](docs/OPTIMIZATIONS.md) · [Rebuild](docs/REBUILD.md)

## Directories

- **optimized version/** — Current 512 KB / 1 MB CAR/ROM, 512 KB XEX and version information.
- **original/** — Original ROM for rebuilding and comparisons.
- **dist/** — IPS patches for both sizes and checksums.
- **src/** — Sources and generators; latest in src/v13, earlier internal stages support rebuilding.
- **scripts/** — Build, benchmark, statistics, chart and XEX test tools.
- **results/** — Measurement and validation data; latest series in results/v13.
- **docs/** — Changes, methodology and research; concise ILMENIT_IDEAS summary.
- **analysis/** — Reverse engineering of the original.
- **arc/up38/** — Solo/Opus archive, with its historical XEX level-end defect.
