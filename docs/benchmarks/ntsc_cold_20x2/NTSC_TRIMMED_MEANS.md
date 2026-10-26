Historical research document. Old paths and results refer to the experiment described; the current implementation is documented in docs/OPTIMIZATIONS.md and aggregate results in docs/benchmarks/METHOD.md (paths from the repository root).

[English](NTSC_TRIMMED_MEANS.md) · [Polski](NTSC_TRIMMED_MEANS_PL.md)

# NTSC: means after excluding extreme results

For each series and version separately, the 20 FPS results were sorted, the lowest 3 and highest 3 discarded, and the arithmetic mean of the remaining 14 computed. No new measurements were made; the source benchmark.json is unchanged.

| Series | Original: 20 trials | Original: 14 trials | v9: 20 trials | v9: 14 trials | Gain after trimming |
|---|---:|---:|---:|---:|---:|
| 1 | 5.7764 | 5.7298 | 6.7344 | 6.7319 | 17.4882% |
| 2 | 5.7708 | 5.7289 | 7.0054 | 7.0097 | 22.3569% |

## Difference between series

- Original: series 2 minus series 1 = -0.0010 FPS (-0.0168%).
- v9: series 2 minus series 1 = 0.2778 FPS (4.1265%).

## Excluded trials

Trial numbers refer to numbering 1–20 within each series.

- Series 1, original: lowest: 6 (5.4295 FPS), 9 (5.4836 FPS), 17 (5.5140 FPS); highest: 4 (6.1714 FPS), 10 (6.2309 FPS), 8 (6.4817 FPS).
- Series 1, v9: lowest: 6 (6.4227 FPS), 9 (6.4583 FPS), 4 (6.4655 FPS); highest: 16 (7.0031 FPS), 19 (7.0419 FPS), 15 (7.0497 FPS).
- Series 2, original: lowest: 18 (5.5018 FPS), 13 (5.5018 FPS), 3 (5.5496 FPS); highest: 4 (5.9989 FPS), 14 (6.2656 FPS), 7 (6.3944 FPS).
- Series 2, v9: lowest: 20 (6.4674 FPS), 4 (6.5177 FPS), 19 (6.5915 FPS); highest: 14 (7.3578 FPS), 13 (7.3905 FPS), 17 (7.6483 FPS).

Trimming did not remove the discrepancy between v9 means across series. This is a trimmed mean (15% from each tail), not the mean of all normal game starts. The extreme trials were not considered erroneous; they were omitted according to the chosen calculation method.
