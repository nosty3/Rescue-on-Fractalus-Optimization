# NTSC: main measurement — a fresh process for every trial

[English](NTSC_REPORT.md) · [Polski](NTSC_REPORT_PL.md)

Report data: [results/ntsc_isolated_main](../../../results/ntsc_isolated_main). JSON filenames without a path refer to that directory.

**Note on the outcome definition:** after 47 completed trials, a flight ended naturally before one minute. The procedure was explicitly amended: a trial lasts until the 60 s limit or the end of flight, and shorter flights remain in the mean. The ending animation is excluded. This is not a mean of complete minutes only. The rule was added during the study; see PROTOCOL_ADDENDUM.md. Sample size and schedule did not change. The study was not fully preregistered for this amended definition.

155 native starts of the original and 155 native starts of v9. No saved states or game-memory modifications. The 15, 30, and 60 s measurements are nested within the same flight; the statistical unit is the whole flight.

## Conditions and scenario population

Atari 800XL 64 KB NTSC, stock configuration without accelerators, default level, centered joystick, no booster or firing. START after 3000–3599 video frames from BOOT. Timings are sampled uniformly without replacement separately per version; this does not guarantee a uniform distribution over all game maps. Five trials of each version form a balanced block, with random order within each block. The schedule and sample size were saved in plan.json before starting.

After first entry to $A32E, release START and run 170 video frames of warm-up. Then measure intervals between completed images at $B516 and their duration in Atari ticks (1,789,772.5 Hz). Include the first complete interval past 15/30/60 s. Every counted image completion belongs to flight mode 2. Record complete intervals, terrain hashes, initial memory, and configuration.

Results describe the mean for an explicitly defined population of 600 possible START timings per version in this emulator and scenario. They do not automatically describe all levels, hardware, or playing styles. Maps are not chosen to favor the result, and valid extreme trials are not removed.

We compare native starts of both versions under the same distribution of START timings. Identical maps are not enforced: the audit showed that the same START timing can generate different terrain in the original and v9. Percentage gain concerns the mean result of this usage scenario, not an isolated renderer speedup on identical terrain.

## Means and spread

| Window | Original FPS | Original SD | v9 FPS | v9 SD | Gain |
|---|---:|---:|---:|---:|---:|
| 15 s | 5.7407 | 0.2771 | 6.8404 | 0.3393 | +19.16% |
| 30 s | 5.7637 | 0.2204 | 6.8293 | 0.2895 | +18.49% |
| 60 s | 5.8043 | 0.1937 | 6.8977 | 0.2581 | +18.84% |

## Uncertainty of the 60 s result

- Original: mean 5.8043 FPS, approximate 95% confidence interval 5.7736–5.8350 FPS; distinct terrain tables 155/155.
- Original: flights ending before the 60 s limit: 1/155; actual measured interval durations 52.584–60.194 s.
- v9: mean 6.8977 FPS, approximate 95% confidence interval 6.8567–6.9386 FPS; distinct terrain tables 155/155.
- v9: flights ending before the 60 s limit: 1/155; actual measured interval durations 32.058–60.161 s.

Averaging-method check: total completed intervals / total duration gives 5.8044 FPS for the original and 6.8978 FPS for v9, or +18.84%. This is duration-weighted; the primary result above gives each sampled flight equal weight.

- Gain: +18.84%; approximate 95% interval by variance propagation 17.90%–19.78% (half-width 0.94 percentage points).
- Bootstrap check: 18.03%–19.66%. Whole flights were resampled within each block/version combination, preserving block sizes. 50,000 replications; individual frames were not resampled.

Intervals are approximate and conditional on this sampling plan. The analytical method does not correct for the finite population of 600 scenarios, giving a conservative estimate of sampling-without-replacement error. The bootstrap retains observed blocks and does not model unknown shared changes between future sessions. Technical reproducibility was checked in a separate audit; that audit is not proof of complete emulator correctness.

## 60 s blocks

| Block | Original FPS | v9 FPS | Gain |
|---|---:|---:|---:|
| 1 | 5.7635 | 6.5797 | +14.16% |
| 2 | 5.7565 | 7.0618 | +22.67% |
| 3 | 5.9290 | 6.8616 | +15.73% |
| 4 | 5.7994 | 6.8895 | +18.80% |
| 5 | 5.7034 | 6.8953 | +20.90% |
| 6 | 5.8785 | 6.7978 | +15.64% |
| 7 | 5.7619 | 6.7439 | +17.04% |
| 8 | 5.8541 | 7.0029 | +19.62% |
| 9 | 5.8835 | 6.8543 | +16.50% |
| 10 | 5.7214 | 6.8718 | +20.11% |
| 11 | 5.6800 | 7.0532 | +24.18% |
| 12 | 5.7831 | 6.8257 | +18.03% |
| 13 | 5.7939 | 7.0811 | +22.22% |
| 14 | 5.8964 | 6.6699 | +13.12% |
| 15 | 5.8090 | 6.6889 | +15.15% |
| 16 | 5.7409 | 6.9208 | +20.55% |
| 17 | 5.7531 | 6.9892 | +21.49% |
| 18 | 5.8044 | 6.9080 | +19.01% |
| 19 | 5.8372 | 6.9278 | +18.68% |
| 20 | 5.9029 | 6.8579 | +16.18% |
| 21 | 5.8107 | 7.0653 | +21.59% |
| 22 | 5.7946 | 7.2790 | +25.62% |
| 23 | 6.0444 | 6.8892 | +13.98% |
| 24 | 5.7376 | 6.8669 | +19.68% |
| 25 | 5.9071 | 6.8861 | +16.57% |
| 26 | 5.8007 | 7.0614 | +21.73% |
| 27 | 5.7629 | 6.7765 | +17.59% |
| 28 | 5.8302 | 6.8940 | +18.25% |
| 29 | 5.8211 | 6.9440 | +19.29% |
| 30 | 5.6961 | 6.9544 | +22.09% |
| 31 | 5.6762 | 6.7305 | +18.57% |

## Dependence on flight duration and order

Order in these diagnostics means position in the frozen schedule. During parallel execution, it is not the exact order in which processes start or finish.

- Original: SD for 60 s / SD for 15 s = 0.699; order–FPS correlation rho=-0.039, p=0.627; Kruskal test between blocks p=0.797.
- v9: SD for 60 s / SD for 15 s = 0.761; order–FPS correlation rho=0.087, p=0.281; Kruskal test between blocks p=0.040.

Diagnostic tests do not establish block equivalence. A change in mean during a longer flight may reflect different workloads farther along the route; 60 s is not merely a more precise estimate of the same initial 15 s segment.

For v9, the between-block test gives uncorrected p≈0.040. This is a diagnostic signal among several comparisons, not proof of emulator drift or equivalence of small series. Blocks contain different randomly assigned scenarios. No significant monotonic dependence on schedule position was observed; other differences are not ruled out. The reported main interval describes sampling from a fixed scenario population, not unknown variation across emulators or sessions.

## Assessment of planned precision

The ±1 percentage point target was achieved under the approximate interval used: ±0.94 percentage points. No additional trials were selected after seeing the result, and pilot data were not included.

## Materials

- `plan.json`: schedule saved in advance.
- `benchmark.json`: all results and metadata.
- `summary.json`: statistics.
- `scripts/benchmark_ntsc_isolated.py`: measurement procedure.
- `scripts/summarize_ntsc_isolated.py`: calculations.
- `scripts/report_ntsc_isolated.py`: report and chart.

Auxiliary RAM dumps, full emulator logs, and tick lists should not be published in the repository.

## Change in execution method

The first 86 trials ran sequentially. Following user authorization and exact validation of four flights (pilot minimum and maximum FPS for each version), the remaining trials ran in up to four separate emulators. Validation covered every image interval, the 15/30/60 s checkpoints, and full 32 KB RAM at three points; all matched exactly. Planned scenarios did not change. Details: ../ntsc_parallel_validation/VALIDATION.md.
