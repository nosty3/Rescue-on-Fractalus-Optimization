Historical research document. Old paths and results refer to the experiment described; the current implementation is documented in docs/OPTIMIZATIONS.md and aggregate results in docs/benchmarks/METHOD.md (paths from the repository root).

[English](NTSC_COMPARISON.md) · [Polski](NTSC_COMPARISON_PL.md)

# NTSC — original versus v9

2026-10-22. Atari 800XL, 64 KiB RAM, NTSC, no accelerators.

**Original: 5.811446 FPS. V9: 6.982743 FPS.**
**Increase: +1.171297 FPS, or +20.155%.**

| Scenario | Original | v9 | Change |
|---|---:|---:|---:|
| Straight | 5.885863 | 6.931424 | +17.764% |
| Right turn | 5.807564 | 7.088889 | +22.063% |
| Left turn | 5.718009 | 6.826011 | +19.377% |
| Fast flight to the right | 5.834364 | 7.084954 | +21.435% |

The pooled result is total presentation intervals divided by total emulated time per version, not an arithmetic mean of FPS values. Each of the eight measurements lasts at least 3600 NTSC frames, about a minute. New images presented at $B516 are counted, not refresh frames. Every trial remained in flight mode at each presentation.

## Shared initial conditions

The original was cold-booted in NTSC and stopped on first entry to the main flight loop at $A32E in bank 2. The same emulator state was saved for both versions. This is a boundary before geometry calculations, with no active optimized renderer routine on the stack.

Before each trial, the appropriate cartridge and shared state were loaded, then NTSC/64 KiB configuration, PC, bank, the entire visible bank 2, and the fixed ROM bank were checked. The original executed its original RAM code. For v9 only, the documented 215 bytes of RAM code at $7EEB..$7FC1 were replaced with the v9 code required for it to run. Before execution, the entire 32 KiB RAM was checked: identical between versions except for this intentional code segment.

Both versions then ran 120 flight frames with a centered joystick, followed by setting the scenario direction and running 50 warm-up frames. Fast flight additionally held OPTION for 45 frames before warm-up. NTSC clock: 1789772.5 Hz; frame: 29868 ticks (114*262). The appropriate RAM-code signature was checked after each run.

Faster code changes game progression over time, so identical geometry at every subsequent frame is not guaranteed. This compares a shared initial state and control protocol, not renderer cycles alone on a frozen set of scenes. One series provides no confidence interval.

## Relation to the earlier v9 measurement

The earlier 6.810914 FPS came from a separate v9 cold boot. For this comparison, v9 was measured again from the original's shared state. The percentage gain above uses only this new pair of measurements. Do not combine the numerator from one series with the denominator from another. The historical NTSC_V9_MEASUREMENT.md report remains a record of the earlier test.

The original may exhibit the previously identified buffer race; a presentation count does not mean every displayed frame was artifact-free. V9 includes the synchronization fix and PMG optimization.

## Files and reproduction

Original SHA256: `1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68`.
V9 SHA256: `0c8226e1f58ad26b2a103cbf59c4b8b23fdb87caac0e22f2586a83513a859880`.
ROMs, existing filenames, and README were unchanged.

Scripts: `python scripts/compare_ntsc.py prepare`, then `python scripts/compare_ntsc.py benchmark` and `python scripts/report_ntsc_comparison.py`. They require the local Altirra bridge and SDK. Preparation creates a fresh state from the original, so old PAL states or previous dumps are not required. Exact repetition of the same session requires the retained local state; a new cold boot may yield a different random sequence and slightly different results. In the repository copy, the original is at `original/Rescue on Fractalus!.rom`; the script also supports the original local location in the project root.

Compact results and configuration are in `results/ntsc_comparison`. Screenshots, states, and raw presentation timestamps remain local, outside the repository.
