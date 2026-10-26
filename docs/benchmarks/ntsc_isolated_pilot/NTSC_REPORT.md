Historical research document. Old paths and results refer to the experiment described; the current implementation is documented in docs/OPTIMIZATIONS.md and aggregate results in docs/benchmarks/METHOD.md (paths from the repository root).

[English](NTSC_REPORT.md) · [Polski](NTSC_REPORT_PL.md)

# NTSC: pilot — a fresh process for every trial

20 native starts of the original and 20 native starts of v9. No saved states or game-memory modifications. The 15, 30, and 60 s measurements are nested within the same flight; the statistical unit is the whole flight.

## Conditions and scenario population

Atari 800XL 64 KB NTSC, stock configuration without accelerators, default level, centered joystick, no booster or firing. START after 3000–3599 video frames from BOOT. Timings are sampled uniformly without replacement separately per version; this does not guarantee a uniform distribution over all game maps. Five trials of each version form a balanced block, with random order within each block. The schedule and sample size were saved in plan.json before starting.

After first entry to $A32E, release START and run 170 video frames of warm-up. Then measure intervals between completed images at $B516 and their duration in Atari ticks (1,789,772.5 Hz). Include the first complete interval past 15/30/60 s. Every counted image completion belongs to flight mode 2. Record complete intervals, terrain hashes, initial memory, and configuration.

Results describe the mean for an explicitly defined population of 600 possible START timings per version in this emulator and scenario. They do not automatically describe all levels, hardware, or playing styles. Maps are not chosen to favor the result, and valid extreme trials are not removed.

## Means and spread

| Window | Original FPS | Original SD | v9 FPS | v9 SD | Gain |
|---|---:|---:|---:|---:|---:|
| 15 s | 5.6056 | 0.2446 | 6.7503 | 0.3112 | +20.42% |
| 30 s | 5.6586 | 0.2116 | 6.7900 | 0.2443 | +19.99% |
| 60 s | 5.6922 | 0.1953 | 6.8369 | 0.2268 | +20.11% |

## Uncertainty of the 60 s result

- Original: mean 5.6922 FPS, approximate 95% confidence interval 5.6008–5.7836 FPS; distinct terrain tables 20/20.
- Original: flights ending before the 60 s limit: 0/20; actual measured interval durations 60.011–60.161 s.
- v9: mean 6.8369 FPS, approximate 95% confidence interval 6.7308–6.9430 FPS; distinct terrain tables 20/20.
- v9: flights ending before the 60 s limit: 0/20; actual measured interval durations 60.011–60.144 s.

Averaging-method check: total completed intervals / total duration gives 5.6922 FPS for the original and 6.8369 FPS for v9, or +20.11%. This is duration-weighted; the primary result above gives each sampled flight equal weight.

- Gain: +20.11%; approximate 95% interval by variance propagation 17.60%–22.62% (half-width 2.51 percentage points).
- Bootstrap check: 17.93%–22.40%. Whole flights were resampled within each block/version combination, preserving block sizes. 50,000 replications; individual frames were not resampled.

Intervals are approximate and conditional on this sampling plan. The analytical method does not correct for the finite population of 600 scenarios, giving a conservative estimate of sampling-without-replacement error. The bootstrap retains observed blocks and does not model unknown shared changes between future sessions. Technical reproducibility was checked in a separate audit; that audit is not proof of complete emulator correctness.

## 60 s blocks

| Block | Original FPS | v9 FPS | Gain |
|---|---:|---:|---:|
| 1 | 5.6309 | 6.7501 | +19.88% |
| 2 | 5.7242 | 7.0272 | +22.76% |
| 3 | 5.7624 | 6.7989 | +17.99% |
| 4 | 5.6514 | 6.7713 | +19.82% |

## Dependence on flight duration and order

Order in these diagnostics means position in the frozen schedule. During parallel execution, it is not the exact order in which processes start or finish.

- Original: SD for 60 s / SD for 15 s = 0.798; order–FPS correlation rho=0.067, p=0.779; Kruskal test between blocks p=0.635.
- v9: SD for 60 s / SD for 15 s = 0.729; order–FPS correlation rho=-0.030, p=0.900; Kruskal test between blocks p=0.315.

Diagnostic tests do not establish block equivalence. A change in mean during a longer flight may reflect different workloads farther along the route; 60 s is not merely a more precise estimate of the same initial 15 s segment.

## Planning a separate main measurement

For a target of ±1 percentage point of gain (95%) and the observed 60 s spread: approximately 127 trials per version. With a 20% margin and rounding to complete blocks: 155 trials per version.

This is a prediction, not a guarantee of final precision. Freeze the number before the main measurement; do not stop based on a favorable interim result. Do not add the pilot to the confirmatory-test mean.

## Materials

- `plan.json`: schedule saved in advance.
- `benchmark.json`: all results and metadata.
- `summary.json`: statistics.
- `scripts/benchmark_ntsc_isolated.py`: measurement procedure.
- `scripts/summarize_ntsc_isolated.py`: calculations.
- `scripts/report_ntsc_isolated.py`: report and chart.

Auxiliary RAM dumps, full emulator logs, and tick lists should not be published in the repository.

