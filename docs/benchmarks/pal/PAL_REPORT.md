# PAL — repeating the automatic original/v9 test

[English](PAL_REPORT.md) · [Polski](PAL_REPORT_PL.md)

Report data: [results/pal_isolated_main](../../../results/pal_isolated_main). JSON filenames without a path refer to that directory.

Completed 155 native starts of each version. Mean FPS: original **6.4421**, v9 **7.5623**, gain **17.39%**.

## Protocol fixed before measurement

- Atari 800XL, 64 KB, PAL, stock addons, no accelerators. Same original/v9 images and emulator as in the NTSC study.
- A new emulator process for every start. No state loading or game-memory modification.
- Exactly the same 155-trial-per-version schedule as NTSC: START after 3000–3599 video frames, sampled without replacement separately per version. Blocks of five flights per version.
- First entry to $A32E, release START, 170 warm-up frames, centered joystick. No turns, dives, firing, or booster.
- Image-interval counter at $B516, PAL clock 1,773,447.5 Hz. PAL frame: 35,568 ticks (312 × 114).
- The 15/30/60-second checkpoints are successive windows of the same flight, not independent trials. The first complete interval past the limit is included.
- Trials that leave flight mode early remain in the dataset. Count complete intervals through the final completed flight image; the ending animation is excluded. This rule was fixed before PAL began.
- Four isolated emulators, separate ports/tokens/files. One thread saves the aggregate in plan order. Each block finishes before the next begins.
- The sample size of 155 was fixed before measurement to repeat NTSC. No new PAL sample-size pilot or additional trials chosen after seeing results.

170 warm-up frames take about 3.41 s PAL versus 2.84 s NTSC. Menu waiting is also longer in PAL. The protocol's frame counts were preserved, not their duration in seconds. The actual measurement limit is 60 seconds of emulated Atari time in both standards.

## Technical validation

Before the main series, four 15-second scenarios (two per version) were run sequentially and again in parallel. All image intervals and the full 32 KB RAM at entry, after warm-up, and at the end were identical. These eight control flights are excluded from the main mean. Data: `results/pal_parallel_validation/validation.json`.

After completion, all 310 trials were checked against the plan, along with unique START timings per version, PAL mode, event and RAM hashes, and FPS recomputed from ticks. Result: `integrity.json`.

## Results

| Limit | Original FPS | SD | v9 FPS | SD | Gain |
|---|---:|---:|---:|---:|---:|
| 15 s | 6.4231 | 0.3473 | 7.5984 | 0.3954 | 18.30% |
| 30 s | 6.4249 | 0.2769 | 7.5709 | 0.3251 | 17.84% |
| 60 s | 6.4421 | 0.2213 | 7.5623 | 0.2771 | 17.39% |

## Uncertainty and shorter flights

- Original: approximate 95% confidence interval for mean 6.4070–6.4772 FPS; median 6.4159; 155/155 distinct terrain tables.
- Original: 3/155 flights shorter than the 60 s limit; measured durations 44.223–60.168 s.
- v9: approximate 95% confidence interval for mean 7.5183–7.6063 FPS; median 7.5340; 155/155 distinct terrain tables.
- v9: 4/155 flights shorter than the 60 s limit; measured durations 47.131–60.188 s.
- Gain 17.39%; approximate 95% confidence interval 16.46–18.32%, half-width 0.93 percentage points.
- Stratified bootstrap (50,000 replications of whole flights within block/version): 16.56–18.23%.
- Time-weighting check: 6.4430 and 7.5634 FPS; gain 17.39%. The primary result gives every flight equal weight.

Intervals are approximate. The analytical interval does not apply a correction for sampling without replacement from 600 possible START timings, which is conservative. The bootstrap retains observed blocks; it does not model unknown changes between future sessions. Precision concerns the defined scenario population, not the entire game.

## Comparison with NTSC

| Standard | Original FPS | v9 FPS | Gain |
|---|---:|---:|---:|
| PAL | 6.4421 | 7.5623 | 17.39% |
| NTSC | 5.8043 | 6.8977 | 18.84% |

Difference in point estimates of gain, PAL minus NTSC: -1.45 percentage points. This is a descriptive comparison, not a separate equivalence test between standards.

The same START timings in frames do not guarantee identical maps or trajectories across versions or standards. Results describe native starts with a centered joystick, not the renderer alone on identical inputs. They do not cover controlled valley flight, turns, or other levels.

## Spread and order diagnostics

- Original: SD of 60 s window / SD of 15 s window = 0.637; correlation with schedule position rho=-0.035, p=0.662; Kruskal test between blocks p=0.547.
- v9: SD of 60 s window / SD of 15 s window = 0.701; correlation with schedule position rho=-0.019, p=0.815; Kruskal test between blocks p=0.810.

Diagnostic p-values are not corrected for multiple comparisons and do not establish equivalence of small blocks. Order refers to the frozen schedule, not the exact order of process completion.

## Materials

- `plan.json`, `benchmark.json`, `summary.json`, `integrity.json` — schedule, results, statistics, and integrity checks.
- `FPS_DISTRIBUTION_PAL_EN.png` / `.svg` — English FPS distribution and cumulative distribution.
- `FLIGHT_DURATION_PAL_EN.png` / `.svg` — English chart of the mean versus measurement duration.
- `scripts/benchmark_pal_parallel.py` and `pal_repro_common.py` — study execution.
- `scripts/summarize_ntsc_isolated.py main --video pal` — statistics.
- `scripts/verify_ntsc_main_data.py --video pal` — data checks.
- `scripts/plot_ntsc_english.py --video pal` — charts.
- `scripts/report_pal_isolated.py` — this report.

RAM dumps and full logs are local diagnostic material, not intended for copying into the repository.
