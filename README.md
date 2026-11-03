# Rescue on Fractalus! — Atari XL/XE optimization

An optimized version of **Rescue on Fractalus!** for Atari XL/XE. It runs more smoothly while preserving the original graphics and gameplay. **Version v14 fits a 128 KB cartridge and requires the standard 64 KB RAM.** The new optimizations in this release are by **Solo** and his **Opus/Fable** agent team.

[English](README.md) · [Polski](README_PL.md)

[CAR](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20128KB.car) · [ROM](optimized%20version/Rescue%20on%20Fractalus%21%20-%20optimized%20128KB.rom)

Download **CAR** to run the game as a cartridge in an emulator, or **ROM** if your hardware requires a raw image. Start the game from a cold boot instead of loading a save state from an older version.

| System | Original FPS | v11 FPS | v14 FPS | Gain / original | Gain / v11 |
|---|---:|---:|---:|---:|---:|
| PAL | 6.2717 | 8.7829 | **10.9172** | **+74.07%** | **+24.30%** |
| NTSC | 5.5915 | 8.0031 | **9.8961** | **+76.98%** | **+23.65%** |

50/50 result: half the straight-flight mean plus half the descent-flight mean. Solo supplied 620 flights (155 per scenario and system), up to 60 s, cold boot, 170 warmup frames. An independent audit exactly reproduced 50 selected flights. Original and v11 references are historical. No cross-version state transfers; faster VBI can change the randomized planet. Natural early ends remain in the data.

![PAL FPS](docs/benchmarks/charts/V14_PAL.png)

![NTSC FPS](docs/benchmarks/charts/V14_NTSC.png)

## New optimizations by Solo

- Tighter hidden-subtree rejection and rewritten mountain rasterization.
- Faster column fill with identical image output.
- Table-based multiplication, interpolation and sound queue in VBI.
- Faster grid geometry, preparation and postpass.
- Faster projection and edge loop.
- Safe projection work performed while waiting for the previous image.

[Details / Szczegóły](docs/OPTIMIZATIONS.md) · [Method / Metodyka](docs/benchmarks/METHOD.md) · [Audit / Audyt](docs/benchmarks/UP74_INTEGRATION_AUDIT.md) · [Build](docs/REBUILD.md)

## Directories

- optimized version/ — current CAR, ROM and release information.
- original/ — original ROM.
- dist/ — original-to-current IPS patch and checksums.
- src/ — sources; new Solo work in src/up74.
- scripts/ — rebuilding, measurements and charts.
- results/ — results; current data in results/v14.
- docs/ — changes, methodology and research.
- analysis/ — reverse engineering of the original.
- arc/ — historical up38 material.

## Credits

The first optimization stage was prepared by **nosty** with **ChatGPT-6 Astra** (+18%). Then **Solo**, working with **Opus** agents, achieved about 39%, and **Astra** developed this into v11. The next substantial performance increase in v14 is by **Solo** and his **Opus/Fable** team. These historical percentages are not additive.
