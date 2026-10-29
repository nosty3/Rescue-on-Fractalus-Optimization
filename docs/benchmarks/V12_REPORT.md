# Full v12 FPS benchmark

310 fresh cold boots: 155 PAL and 155 NTSC, with 78 straight and 77 descent per system. Four isolated emulators, nominal 60 s windows, closed at a whole presentation. The 50/50 result is half of each scenario mean. Original and v11 retain full data of 155 flights per scenario/system.

![FPS](charts/V12_COMPARISON.png)

| System | Original FPS | v11 FPS | v12 FPS | Gain over original |
|---|---:|---:|---:|---:|
| PAL | 6.271731 | 8.782928 | 8.932929 | +42.4316% |
| NTSC | 5.591516 | 8.003108 | 8.149851 | +45.7539% |

### PAL

| Reference | Reference FPS | Delta FPS | Gain | Gain 95% interval |
|---|---:|---:|---:|---:|
| Oryginał | 6.271731 | +2.661198 | +42.4316% | [+41.0787%, +43.7830%] |
| v11 pełne dane | 8.782928 | +0.150001 | +1.7079% | [+1.0790%, +2.3444%] |
| v11 te same 155 prób | 8.743560 | +0.189369 | +2.1658% | [+1.6135%, +2.6986%] |

v12 — przedział FPS 95%: [8.854022, 9.011272]. Naturalne wcześniejsze końce: 8/155.

### NTSC

| Reference | Reference FPS | Delta FPS | Gain | Gain 95% interval |
|---|---:|---:|---:|---:|
| Oryginał | 5.591516 | +2.558335 | +45.7539% | [+44.4038%, +47.0836%] |
| v11 pełne dane | 8.003108 | +0.146743 | +1.8336% | [+1.1732%, +2.4948%] |
| v11 te same 155 prób | 7.991736 | +0.158115 | +1.9785% | [+1.4598%, +2.4902%] |

v12 — przedział FPS 95%: [8.080669, 8.218045]. Naturalne wcześniejsze końce: 9/155.

Series wall time: 20 min 15 s. All 17 natural early ends are retained, without outlier removal. Gain is a ratio of means, not a mean of percentages. Intervals: 20,000 bootstrap replicates, seed 2026102912, resampling whole starts within the 78/77 groups. Historical original straight flights use an independent plan. The matched v11 check uses the same selected 155 trials as v12; the full v11 reference has 310 flights.

[Method](METHOD.md) · [Build instructions](../REBUILD.md) · [Data](../../results/v12/)

New measurement: `python scripts/benchmark_current.py --output results/new_v12`. Install the bridge under tools/bridge or set FRACTALUS_BRIDGE_DIR. Do not overwrite published data. `python scripts/report_v12.py` and `python scripts/plot_v12.py` regenerate statistics and the chart.

ROM SHA-256: `4959a82ab36528a0448a40e6178fdb72d321e5d1e23c258036f5e22e51cfa20e`.
