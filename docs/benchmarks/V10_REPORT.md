# v10 — plotter and full PAL/NTSC measurements

[English](V10_REPORT.md) · [Polski](V10_REPORT_PL.md)

Completed 155 new v10 flights per standard. The original and v9 come from historical series of 155 flights each; a 60-second v9 control flight in each standard reproduced the same events and initial memory. The emulator has the same SHA256. The complete control series were not rerun.

## Results

| System | Original FPS | v9 FPS | v10 FPS | Gain over original | Gain over v9 |
|---|---:|---:|---:|---:|---:|
| PAL | 6.4421 | 7.5623 | 7.6359 | +18.53% | +0.0736 FPS (+0.97%) |
| NTSC | 5.8043 | 6.8977 | 6.9377 | +19.53% | +0.0400 FPS (+0.58%) |

## Method and uncertainty

Each trial used a separate process, cold boot, stock Atari 800XL 64 KB, START according to the 155 v9 entries in frozen plan 2026102303, 170 warm-up frames, and a centered joystick. Four-emulator execution was validated by repeating four 15-second trials sequentially and in parallel; events and RAM were identical. Controls are excluded from the means.

The B516 counter and emulated Atari time include DMA/VBI. The 15/30/60 s windows are dependent parts of a flight. Natural early endings remain in the sample. Every flight has equal weight. No extreme values were removed. Integrity checks confirm agreement with the plan, 155 trials per standard, event hashes, and FPS recomputed from ticks.

Stratified bootstrap: 50,000 replications of flights in blocks of five; comparison with the original treats the series as independent. An additional Student's t interval for the v10−v9 difference uses pairs with identical START timings. This pairs schedules; it does not promise identical maps or gameplay trajectories.

- PAL: 95% bootstrap interval for gain over original 17.70–19.36%; 95% interval for mean difference from v9 +0.0504–+0.0969 FPS. Identical initial RAM: 155/155 pairs. Shortened v10 flights: 3/155.
- NTSC: 95% bootstrap interval for gain over original 18.68–20.37%; 95% interval for mean difference from v9 +0.0177–+0.0622 FPS. Identical initial RAM: 155/155 pairs. Shortened v10 flights: 2/155.

These intervals describe this automatic-flight method. They do not cover every level, diving, or turning. Tests were not performed on physical Atari hardware.

## Code change and correctness

The only ROM change relative to v9 is bank 5. The ROM row tables have effective bases $9700 and $9740 and do not cross pages for Y=104..151. Removed 48 redundant STY $B5 instructions in specialized paths that restore Y from a constant. General paths retain RAM tables. No changes to the mixer, perspective, banking, or buffer synchronization.

The code passed 58 rendering-and-continuation scenes, 6000 segments, 309 low-height cases, 2784 table comparisons, and 232 VBI tests. Mean saving in the scene set: 1248.09 cycles per rendering-and-filling operation. This should not be converted directly into overall FPS.

Memory contract: B5 may differ after the renderer and B4/B5 after subsequent geometry; they are treated as scratch values unused by the later computations examined. Tests exclude dead stack memory. Registers and flags at the tested exits remain equivalent. This is testing and an audit, not a formal proof for every game state.

ROM SHA256: `fde2166f28d768514a933a76654c9c3f9a583d4cdac182ed08aa14d15761bc37`. Source: `src/v10_plotter.asm`. Results: `results/v10/`. Chart labels are in English.
