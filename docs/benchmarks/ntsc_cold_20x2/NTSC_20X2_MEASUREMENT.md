Historical research document. Old paths and results refer to the experiment described; the current implementation is documented in docs/OPTIMIZATIONS.md and aggregate results in docs/benchmarks/METHOD.md (paths from the repository root).

[English](NTSC_20X2_MEASUREMENT.md) · [Polski](NTSC_20X2_MEASUREMENT_PL.md)

# NTSC: two series of 20 cold starts of the original and v9

Each series contains 20 original trials and 20 v9 trials: 80 separate starts in total. No saved states were loaded, no memory was transferred between versions, and neither game code nor data was modified.

## Procedure

- Headless Altirra, Atari 800XL, 64 KB, NTSC, no acceleration expansions.
- Each trial loads and starts the game image from the beginning with BOOT.
- Time before START: 3000–3599 video frames, chosen independently for each trial. The two series have different recorded seeds for the waiting-time generator. No seed is imposed on the game's terrain generator.
- Default initial level, centered joystick, no booster or firing. On first entry to the flight loop ($A32E), release START and run 170 warm-up video frames.
- Measure completed game images at $B516, not NTSC refresh frequency. Measurement begins at the first hit after warm-up and ends at the first hit after 15 seconds. Completing the final image avoids counting a partial frame; the actual duration of each trial is recorded in JSON.
- Trial FPS = complete image intervals / actual duration of those intervals. Time comes from the emulated Atari clock: 1,789,772.5 Hz.
- Reported mean is the arithmetic mean of individual trial FPS values. Original and v9 alternate, reversing their order in successive pairs.
- Check flight mode throughout measurement, NTSC configuration, ROM bank, and v9 code. SHA-256 of table $0900–$09FF checks terrain-data diversity.

## Results

| Series | Original: mean FPS | v9: mean FPS | FPS increase |
|---|---:|---:|---:|
| 1 | 5.7764 | 6.7344 | +16.58% |
| 2 | 5.7708 | 7.0054 | +21.39% |
| Combined (40 + 40 trials) | 5.7736 | 6.8699 | +18.99% |

## Between-trial spread

| Series | Version | Min–max FPS | FPS standard deviation | Mean ± half-width of 95% confidence interval | Distinct terrain tables |
|---|---|---:|---:|---:|---:|
| 1 | original | 5.4295–6.4817 | 0.2776 | 5.7764 ± 0.1299 | 20/20 |
| 1 | v9 | 6.4227–7.0497 | 0.1935 | 6.7344 ± 0.0906 | 20/20 |
| 2 | original | 5.5018–6.3944 | 0.2324 | 5.7708 ± 0.1088 | 20/20 |
| 2 | v9 | 6.4674–7.6483 | 0.3153 | 7.0054 ± 0.1476 | 20/20 |
| Combined | original | 5.4295–6.4817 | 0.2527 | 5.7736 ± 0.0808 | 40/40 |
| Combined | v9 | 6.4227–7.6483 | 0.2924 | 6.8699 ± 0.0935 | 40/40 |

Confidence intervals use Student's t distribution and treat trials as independent samples. They describe uncertainty in this scenario's mean, not the FPS range of the entire game.

## Repeatability

- Original: series 2 minus series 1 = -0.0056 FPS (-0.10%).
- v9: series 2 minus series 1 = 0.2710 FPS (4.02%).
- Difference in estimated FPS gain between series: 4.81 percentage points.

## Assessment of these two series

The original produced almost identical means in both series. For v9, the difference was about 4.02%, and estimated gain rose from 16.58% to 21.39%. Both series confirm a clear v9 advantage in this scenario, but do not yet confirm repeatability of the precise gain percentage. Under the stated statistical assumptions, the two v9 means' 95% intervals do not overlap. The discrepancy cannot simply be dismissed as negligible.

The combined mean describes the 40 trials of each version; it does not eliminate the between-series discrepancy. Different maps are confirmed, but these measurements do not establish whether they explain the entire difference in means. Further analysis should check initialization conditions and workload distributions for the sampled maps before calling the procedure stable at roughly 1%. No additional series were selected after seeing results, and no extreme trials were discarded.

Each version receives its own independently generated maps. This compares samples of normal starts, not both versions on identical maps. Agreement between series is assessed from differences in means and spread, without assuming in advance that they must agree.

Results concern initial straight flight, excluding 170 warm-up video frames. They do not automatically generalize to later levels, combat, landing, or other controls. Previous results of 6.8109 and 6.9827 FPS covered a different, longer scenario set and are not direct repetitions of this test.

## Files and reproduction

- `benchmark.json`: all 80 results, durations, image counts, terrain hashes, and parameters.
- `summary.json`: statistics and between-series differences.
- `scripts/benchmark_ntsc_cold.py`: complete measurement procedure; requires the emulator launched through `scripts/launch.ps1`.
- `scripts/report_ntsc_cold.py`: generates this report without an emulator.

To repeat, run `python scripts/benchmark_ntsc_cold.py`, then `python scripts/report_ntsc_cold.py`. The script overwrites its output directory's result; preserve earlier results first.

Original SHA-256: `1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68`.

v9 ROM SHA-256 (excluding CAR header): `0c8226e1f58ad26b2a103cbf59c4b8b23fdb87caac0e22f2586a83513a859880`.
