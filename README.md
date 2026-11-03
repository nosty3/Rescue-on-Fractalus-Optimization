[English](README.md) · [Polski](README_PL.md)

# Rescue on Fractalus! — Atari XL/XE optimization

**nosty**, **Solo** and **ilmenit** worked on this project using **ChatGPT 6 Astra/Sol** and **Claude Opus/Fable** agents. The latest and largest optimizations are the work of **Solo**.

## Download the game

An optimized **Rescue on Fractalus!** for Atari XL/XE, preserving the original graphics and gameplay. **v14: 128 KB cartridge, 64 KB RAM required.**

Download **CAR** for an emulator, or **ROM** if your hardware requires a raw image. Start the game from a cold boot.

[**CAR**](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20128KB.car) · [**ROM**](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20128KB.rom)

## Performance

| System | Original FPS | v14 FPS | Gain over original |
|---|---:|---:|---:|
| PAL | 6.2717 | **10.9172** | **+74.07%** |
| NTSC | 5.5915 | **9.8961** | **+76.98%** |

![PAL FPS](docs/benchmarks/charts/V14_PAL.png)

![NTSC FPS](docs/benchmarks/charts/V14_NTSC.png)

## How we measure FPS

Each flight lasts up to **60 seconds** and starts from a fresh game boot. We test **PAL and NTSC** in two scenarios: straight flight and descent pulses (1 s joystick up, 3 s neutral). The combined result gives both scenarios equal **50/50** weight.

**The standard reduced series contains 310 flights in total:** 155 PAL and 155 NTSC, with 78 straight and 77 descent flights per system.

**The v14 results in the table come from a larger series run by Solo: 620 flights in total**, with 155 straight and 155 descent flights for each system. Verification reran 50 selected flights from this series; it was not a new full 310-flight series. Original-game results come from retained earlier measurements. Gain is calculated from the ratio of mean FPS, not the mean of percentage gains.

[Metodyka / Method](docs/benchmarks/METHOD.md)

## What was optimized — from the start of the project through v14

- Exact multiplication, division and interpolation were accelerated using tables and specialized code while preserving the original rounding.
- Geometry preparation, terrain-grid traversal and point classification were streamlined.
- Perspective projection, segment clipping and the edge loop were accelerated.
- Mountain-profile rasterization was rewritten, specializing common cases and skipping only subtrees proven to be hidden.
- Image clearing and fill work were reduced using per-column clear boundaries, lazy clearing and faster color propagation.
- Object plotting, player/missile graphics (PMG) and cockpit indicators were accelerated.
- VBI interrupt work, sound mixing, the effect queue and channel selection were streamlined.
- Time spent waiting for the previous image now performs safe calculations while preserving buffer synchronization.
- Redundant register and memory operations were removed, hot-loop layout improved, and self-modifying RAM code used.

[Szczegóły / Details](docs/OPTIMIZATIONS.md) · [Budowanie / Rebuilding](docs/REBUILD.md)

## Directories

- **optimized version/** — current game downloads and release information.
- **original/** — original game image.
- **dist/** — IPS patch and checksums.
- **src/** — assembly sources and generators.
- **scripts/** — game building, measurements and chart generation.
- **results/** — measurement data and verification results.
- **docs/** — detailed optimizations, methodology and research.
- **analysis/** — analysis of the original game code.
- **arc/** — historical supporting material.
