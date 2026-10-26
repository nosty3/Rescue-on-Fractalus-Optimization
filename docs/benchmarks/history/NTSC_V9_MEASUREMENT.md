Historical research document. Old paths and results refer to the experiment described; the current implementation is documented in docs/OPTIMIZATIONS.md and aggregate results in docs/benchmarks/METHOD.md (paths from the repository root).

[English](NTSC_V9_MEASUREMENT.md) · [Polski](NTSC_V9_MEASUREMENT_PL.md)

# V9 — FPS measurement and functional checks in NTSC

2026-10-22. Only the existing v9 release was tested. Neither the ROM nor filenames were modified. The original and other versions were not tested.

**Mean result for the set: 6.810914 FPS.**

| Scenario | Presentation intervals | Emulated time [s] | FPS |
|---|---:|---:|---:|
| Straight | 405 | 60.127 | 6.735696 |
| Right turn | 414 | 60.144 | 6.883467 |
| Left turn | 408 | 60.161 | 6.781825 |
| Fast flight to the right | 412 | 60.211 | 6.842619 |

Total: 1639 intervals between new images in 240.643187 s. The result is total intervals / total time, not the arithmetic mean of four FPS values.

## Configuration and method

Headless Altirra, 800XL, 64 KiB RAM, NTSC, no Rapidus, VBXE, or U1MB.
File: `dist/Rescue on Fractalus! - PAL optimized v9 128KB.car`.
ROM SHA256: `0c8226e1f58ad26b2a103cbf59c4b8b23fdb87caac0e22f2586a83513a859880`.

NTSC clock: 3579545/2 = 1789772.5 Hz. Frame: 114*262 = 29868 ticks. Constants agree with local Altirra source (`analysis/altirra-constants.h`). Empirically checked: 120 frames give exactly 3584160 ticks. NTSC and 64 KiB configuration were also confirmed after loading each state.

Loading old PAL states restores PAL; changing configuration to NTSC resets the emulated machine. All new states were therefore prepared from a v9 cold boot in NTSC. RAM code from old states was not substituted. Initialized v9 RAM code was checked while excluding the eight deliberately self-modified interpolation operands.

The four flights start from the same fresh NTSC state, saved 120 frames after first entry to the main flight loop at $A32E. Each measurement has 50 warm-up frames; the fast variant additionally holds OPTION for 45 frames. Each measurement covers at least 3600 NTSC frames (~60 s). Successive executions of $B516 count presentations of new buffers, not every refresh frame. All FPS trials remained in flight mode ($4A=2) at every recorded presentation.

This is a new input set. Its percentage difference from the old PAL figure of 7.764418 FPS should not be reported directly: states and flight trajectories differ. No percentage gain over the original NTSC game was calculated because, at the user's request, the original was not tested.

## Functional checks

- Cold boot, title screen, flight start, and another cold boot.
- Additional states after 7 and 15 SELECT pulses (12 frames held and 12 released). These name selection sequences, not level numbers. Three 3600-frame flight trials per state. The three select7 trials ended in mode 0; the inspected image showed the score table. They are not included in FPS measurement or described as uninterrupted flight. select15 trials ended in mode 2.
- START from banks 5,6,8,9,10,11,12,13,14: all returned to flight. In geometry banks, four orientations were forced as explicit test inputs to check every bank. Other trials did not change game data.
- 240 PMG entries: 80 for each of three states; bar contents and retained boundary matched, with handling in bank 2.
- 120 entries to actual screen clearing: 40 for each of three states, always after VBI acknowledged buffer switching ($42=0).
- START while waiting for buffer release: returned to flight.
- Four control trials up/down/left/right with FIRE held, 1200 frames each; continued emulator operation and RAM-code signatures checked. These tests alone do not prove complete hit/collision correctness.
- Images recorded over 1200 consecutive NTSC frames, with selected images and left-side changes inspected visually. The detector also reports legitimate terrain and object changes; it is not automatic proof of the absence of every glitch.

Inspected flight and cockpit images showed neither the repaired wedge artifact nor visible PMG corruption. The main check of the old race is $42 before clearing, not a single final screenshot.

## Conclusion and limits

V9 works correctly in the NTSC tests performed. No need for a separate NTSC ROM was found. This does not prove correctness of every game phase and level: no complete playthrough, sample-by-sample audio comparison, or physical Atari test was performed. FPS measurement is one series of four scenarios without a confidence interval.

## Reproducing the study

Script order: `prepare_ntsc_v9.py`, `benchmark_ntsc_v9.py`, `stress_ntsc_v9.py`, `validate_ntsc_v9.py`, `visual_ntsc_v9.py`, `report_ntsc_v9.py`. They require a working local Altirra bridge and SDK. Preparation creates fresh NTSC states and does not require old PAL states. Do not run multiple scripts against one emulator simultaneously. Tools and states remain outside the repository copy.

Compact results are in `results/ntsc_v9/*.json`. Screenshots, raw timestamps, and test states remain local. Existing filenames were unchanged.
