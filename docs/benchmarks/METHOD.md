# FPS measurement method — v11

[English](METHOD.md) · [Polski](METHOD_PL.md)

## Scenarios and sample size

Two video standards: PAL and NTSC. Two scenarios: straight flight with a centered joystick, and repeated 1 s joystick up (descent) / 3 s neutral. Input starts at measurement time zero; warmup remains neutral. No firing or turns. Each version/standard/scenario combination contains 155 trials. Four up38/v11 × straight/descent configurations produced 1240 flights; original-game descent adds 310. Historical original straight flights supply the other 310 observations for original–v11 comparison.

## Boot and counter

Each trial launches a fresh isolated AltirraBridge process, Atari 800XL/64 KB without acceleration, and natively cold-boots the cartridge. No states are transferred and no game memory is patched. Four workers have separate ports, tokens and files; host speed does not determine measurement time.

The start schedule was frozen earlier (seed 2026102303, menu_frames 3000–3599, 31 blocks of five). Both up38/v11 scenarios and new original descent use the 155 v9-arm starts from the historical NTSC plan. Historical original straight flights have independently sampled starts and must not be treated as paired with v11. A shared start does not guarantee identical later geometry/events because execution timing can influence game evolution.

At the first $A32E entry, START is released and 170 video frames warm up. The first $B516 presentation is time zero. Count complete intervals between subsequent finished-image presentations. FPS = interval count / interval duration, not VBI frequency or display refresh. Atari clocks: PAL 1773447.5 Hz; NTSC 1789772.5 Hz. Measurement includes DMA, VBI/DLI and synchronization waits.

The first complete interval crossing 60 s closes the window. The 15/30/60 s checkpoints are nested, not independent trials. A $4A write watch detects natural flight end: keep all complete flight images before that transition, excluding the ending animation. Shorter flights and extremes remain in the sample. New original descent had 4/155 early ends in PAL and 4/155 in NTSC.

Joystick cues follow emulated ticks, not rendered FPS or host time: descent at 0, 4, 8… s; neutral at 1, 5, 9… s. Maximum recorded cue deviation was 0.5 tick.

## Faster execution and controls

Validated batching sends FRAME/CYCLES, PC/mode read and CLOCK in one TCP write. Breakpoints and execution ordering remain active. A truncated 4096-entry profile was not used as the image counter. Transport checks and sequential/parallel controls matched events and memory. All 310 up38 straight flights reproduced historical counts and FPS.

During part of the earlier 1240-flight study, two runners overlapped accidentally (up to eight emulators). The duplicate was stopped; one completed record per trial was retained without FPS-based selection. Four repetitions from that period reproduced all timestamps and memory. Details remain in results/v11/runtime_notes.json. The new 310 original flights used one runner and four emulators, taking 1455.2 host seconds.

Eight PAL entry-state groups in the up38/v11 comparison differed only at $0270–$0277. Normalization checks and watchpoints established equality of the remaining RAM and no reads of those bytes in the checked scenarios. They were not modified during benchmarks.

## Calculations

The primary statistic is the arithmetic mean of per-flight FPS with equal flight weights. Combined = (straight mean + descent mean) / 2. Gain = 100 × (v11 mean / original mean − 1), including the combined row. Scenario percentages are not averaged. A 50/50 weighting defines the benchmark; it is not an empirical estimate of typical gameplay behavior.

For up38/v11, intervals use 50000 paired whole-flight bootstrap replications within 31 blocks, seed 2026103001. Those intervals are not transferred to original–v11 tables: historical original straight flights are unpaired. Main tables report point estimates. Distribution plots show all flights.

## Data and limitations

- results/v11/flights.jsonl: 1550 new observations, presentation timestamps and input cues.
- results/pal_isolated_main/benchmark.json and results/ntsc_isolated_main/benchmark.json: historical original straight flights.
- results/v11/summary.json: original–v11 tables; up38_comparison_summary.json: additional gain over up38.
- scripts/report_v11.py reproduces charts and checks table values from individual observations.
- scripts/benchmark_v11.py runs new series in a separate --output directory; do not run it merely to regenerate charts.

These are cartridge results. No separate full XEX FPS series was run. The protocol does not cover every turn, level, rescue event or hardware accelerator. XEX transition tests deliberately set diagnostic game data; they are excluded from FPS measurements.
