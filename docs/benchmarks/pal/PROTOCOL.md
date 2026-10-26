# PAL: repeating the automatic NTSC test

[English](PROTOCOL.md) · [Polski](PROTOCOL_PL.md)

The plan was saved before measurement. Sample size: 155 per version, 310 total, without adjusting the size after inspecting results. Scenarios and ordering copy the main NTSC study schedule. No pilot is being run to plan a new PAL sample size.

Each trial: a new AltirraBridgeServer process, stock Atari 800XL 64 KB PAL, native BOOT of original or v9, START after the recorded number of menu frames (3000–3599), first entry to $A32E, release START, 170 warm-up frames. Joystick centered throughout, without firing or booster. Turns and dives into valleys are outside the study.

Intervals are measured at $B516 with flight mode 2 active, using PAL clock 3546895/2 = 1773447.5 Hz. A PAL frame is 114 × 312 = 35568 ticks. The 15/30/60-second limits end at the first complete interval crossing the limit. These are nested windows of one trial. Host-computer execution time does not enter FPS.

The following rule applies from the start: if the game leaves flight mode early, retain the trial and its result through the last complete flight interval. Do not include the ending sequence or replace the scenario. No measurable interval or another unexpected stop is an error requiring diagnosis, not grounds for silently removing a trial.

The numbers of waiting and warm-up frames are preserved, not their elapsed duration: 170 frames are about 3.41 s PAL versus 2.84 s NTSC. The main flight limit is 60 seconds in both standards. Identical maps are not assumed for PAL, NTSC, original, and v9.

Before the main series, four 15 s PAL scenarios (two per version) were validated, each sequentially and in parallel. Image intervals and RAM at entry, after warm-up, and at measurement end match exactly. Data: `results/pal_parallel_validation/validation.json`. Validation flights do not enlarge the main sample.

Execution: up to four isolated processes, each with its own port, token, controller, and files. Balanced blocks of five flights per version; a block starts only after the preceding one finishes. One thread writes the aggregate in schedule order using atomic file replacement.

The primary statistic is the arithmetic mean of flight FPS, the v9/original ratio of means, and an approximate 95% confidence interval. Cross-checks: bootstrap whole flights within block/version and a time-weighted result. No extreme values are discarded. The interval concerns the defined scenario population, not every way of playing.

After completion: check agreement with the plan and hashes, recompute counters, prepare a Polish report and corresponding English PNG/SVG charts. Game files and their names remain unchanged.
