Historical research document. Old paths and results refer to the experiment described; the current implementation is documented in docs/OPTIMIZATIONS.md and aggregate results in docs/benchmarks/METHOD.md (paths from the repository root).

[English](DISTRIBUTION_ANALYSIS_AND_METHOD.md) · [Polski](DISTRIBUTION_ANALYSIS_AND_METHOD_PL.md)

# FPS distribution and a proposed reliable NTSC procedure

This analysis concerns the existing 80 trials: two series of 20 independent starts per version. No new flights were run. All results, including extremes, were retained. Analysis code: `scripts/analyze_ntsc_distribution.py`; detailed statistics: `distribution_analysis.json`.

## Descriptive results

| Version / series | Mean FPS | Median FPS | Standard deviation | Middle 50% (Q1–Q3) |
|---|---:|---:|---:|---:|
| Original / 1 | 5.7764 | 5.6786 | 0.2776 | 5.5866–5.8709 |
| Original / 2 | 5.7708 | 5.7401 | 0.2324 | 5.6115–5.8477 |
| v9 / 1 | 6.7344 | 6.7355 | 0.1935 | 6.6047–6.8649 |
| v9 / 2 | 7.0054 | 7.0281 | 0.3153 | 6.7809–7.2033 |

Both original samples have a right tail: a few high FPS values pull the mean above the median. Sample skewness is 1.12 and 1.43. The v9 samples are approximately symmetric (skewness 0.05 and 0.01), but differ in location and spread. With n=20, the exact distribution family cannot be reliably identified. Failure to reject v9 normality with Shapiro–Wilk does not prove population normality. The original samples show departures from normality (p=0.048 and 0.010), but these tests are diagnostic only.

`ROZKLAD_FPS_NTSC_PL.png` shows empirical cumulative distributions without choosing histogram bins. Each point represents one flight. The v9 median shifts as well as its mean. The 1.5 IQR rule flags no v9 results as outliers; it flags 1 and 2 original results. This is not grounds for removal: easier terrain is a valid test outcome.

## Series comparison and inferential limitations

- Original: mean difference -0.0056 FPS. Welch test p=0.945; permutation test p=0.946. Failure to detect a difference is not proof of strict equivalence.
- v9: mean difference +0.2710 FPS. Welch test p=0.00256, approximate 95% interval for the difference +0.1025 to +0.4396 FPS. Permutation test (100,000 draws) p=0.00232; Mann–Whitney p=0.00512. The latter tests distribution/rank differences, not just means.
- Series 1 gain: +16.58%, approximate 95% bootstrap interval +13.79% to +19.33%.
- Series 2 gain: +21.39%, approximate 95% bootstrap interval +18.24% to +24.48%.

These are exploratory analyses, with p-values uncorrected for multiple tests. Tests assume independent and appropriately comparable trials; permutation assumes exchangeability under the null. A p-value is not the probability of emulator error or of the null hypothesis. We do not determine whether the cause was an unlucky map sample, the sampling method, emulator state, or another factor. Bootstrap does not repair systematic error or unstable conditions either.

In v9 series 2, FPS correlates with waiting time before START: Spearman rho=0.641, p=0.00234; series 1 does not reproduce this association (rho=-0.211, p=0.373). v9 series 1 shows increasing FPS with trial number (rho=0.471, p=0.036), absent in series 2. Original series 2 has a negative waiting-time correlation (rho=-0.483, p=0.031). These are clues for an initialization/sampling audit, not established laws. Distinct sampled tables do not guarantee independence or a representative distribution.

## Recommendation: audit the procedure first, then increase the sample

### 1. Technical repeatability audit

Before hundreds of measurements, run a small, separately labeled test reproducing an identical scenario. Use a new emulator process for each run, identical configuration, and controlled START timing. Each version must execute its own ROM and initialization. Record configuration, image and world-data hashes, level, position, direction, speed, and completed-image timestamps.

Check whether repeating the same version actually gives the same world and trajectory. If worlds differ, explain randomness/seed sources before calling the test deterministic. If world and conditions match but measurements do not, investigate the clock, synchronization, and image counter. Also compare a fresh process with the previous repeated-BOOT approach in one process. Do not transfer either version's saved state to the other.

### 2. Measure normal starts without modifying the game

- Fix the scenario in advance: NTSC, initial level, identical warm-up, and one straight flight. Conclusions concern that scenario; general game performance requires other representative scenarios too.
- Plan 60-second flights as a reasonable starting point, but use a pilot first to check whether this reduces spread without introducing game endings or other scenario changes. Do not assume a flight four times as long gives four independent samples. Retain 15/30/60 s checkpoints as dependent outcomes of the same flight.
- Use a new emulator process and native game start for every trial. Sample START timing from a predefined range after confirming menu readiness. A wider range does not guarantee uniform map sampling; world-data distribution must be monitored.
- Use small balanced time blocks, e.g. 5 original and 5 v9 trials, with random order within each block. Retain block identity in analysis. This reduces confounding version with startup time/conditions, but does not equalize maps.
- Retain all valid trials. Define technical-error criteria beforehand; do not remove collisions or game endings after the fact merely because they change the mean. Their handling must be defined in the scenario.
- The statistical unit is a separate flight, not each frame or each 15 s portion of one flight.
- For each flight, compute completed images / time. Then report mean flight FPS with its confidence interval and gain G=100*(v9_mean/original_mean-1) with its own interval. Also report median and spread; do not remove valid extreme flights.
- Bootstrap whole independent flights; when grouping reflects shared conditions, resample appropriate whole blocks. Do not resample individual frames. Between-block stability still needs checking.

### 3. Precision and sample size

Choose a practical target beforehand, e.g. a 95% confidence interval for percentage gain with half-width no greater than 1 percentage point (such as +19% ±1 pp). This differs from ±1% relative precision for one version's mean FPS.

Conditional estimates based on the current spread of 15-second trials, assuming stable independent starts:

| Target | Approximate flights per version |
|---|---:|
| Each version's mean FPS: ±1% relative, 95% | 70–74 |
| Percentage gain: ±2 percentage points, 95% | 51 |
| Percentage gain: ±1 percentage point, 95% | 203 |

This is a normal approximation for planning, not a guarantee. Variance propagation for the ratio of means gives n ≈ (1.96*R/h)^2*(CV_original^2+CV_v9^2), where R is the ratio of means, h the required half-width for R (0.01 corresponds to 1 percentage point of gain), and CV is standard deviation / mean. The observed v9 shift weakens the stability assumption. Recalculate these numbers after the audit and 60 s pilot.

Practical plan: a separate pilot of 20 flights per version, 60 s each; assess spread and block stability, then fix the main-test sample size before it begins. Do not automatically add pilot data to the confirmatory test. Do not stop collecting merely because the current result looks good; adaptive stopping needs an appropriate sequential method. A nonsignificant difference between two series is not an agreement criterion: define an acceptable difference and assess its interval.

## Option for measuring the optimizations themselves: matched worlds

The best terrain-variability control is independent initialization of both ROMs with identical, controlled world data and flight conditions. This does not mean transferring the entire memory state, stack, or registers from original to v9. Consider controlling random-generator input during world generation, or transferring only identified world data after native initialization. This requires a separate demonstration of consistency for all dependent data, not only table $0900.

On the same world, both versions should perform a defined comparable task. Since a faster loop may affect simulation speed, check the route and world state throughout the test rather than assuming equivalence from the start alone. A fixed number of corresponding updates or frames on the same route measures computational speedup; 60 s of gameplay measures user experience. These are different questions.

For verified pairs, analyze differences and the ratio of means with bootstrap resampling of whole pairs. Pairing reduces uncertainty only to the extent that world difficulty affects both versions similarly; no specific sample-size reduction can currently be promised. Such a benchmark complements normal-start testing rather than replacing it.

## Methodological sources

- NIST, block design and order randomization: https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm
- NIST, confidence intervals for means and precision versus spread and sample size: https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm

Conclusion: there is no basis for reducing the problem to too few trials or extreme values alone. First explain initialization/sampling stability, then measure to a predefined precision target. A larger sample reduces random error but does not remove systematic changes in conditions.
