# v12 — local build and full FPS benchmark

The current compact candidate is promoted to v12 without changing its bytes. The cartridge is 128 KB; the XEX needs 320 KB Rambo, 576 KB or 1088 KB RAM with BASIC disabled. This release is available on branch `v12`.

v12 continues the work by nosty with ChatGPT-6 Astra and Solo with the Opus/Fable team. This stage also uses ideas from ilmenit, adapted and checked for the v11 renderer.

| System | Original FPS | v11 FPS, full reference | v12 FPS | v12 gain over original |
|---|---:|---:|---:|---:|
| PAL | 6.2717 | 8.7829 | **8.9329** | **+42.43%** |
| NTSC | 5.5915 | 8.0031 | **8.1499** | **+45.75%** |

The result is the 50/50 mean of the two scenario means. Original and v11: 155 straight and 155 descent flights per system; v12: 78 straight and 77 descent flights per system. Every flight cold-boots. FPS is measured with the CAR on an Atari 800XL/64 KB.

![FPS comparison](charts/V12_COMPARISON.png)

## Changes since v11

- An exact `$AA` shortcut accelerates fill when all 42 control-row bytes have this value, preserving the cache and output state.
- An earlier first-column test shortens failed occlusion checks, and a small table replaces the four-column group-count calculation.
- The root scan keeps the height threshold in A and preserves a separate `Hmax=0` case.
- Further redundant Y bookkeeping is removed at depths d0–d4, restoring Y=5 before generic code.
- Geometry-point classification for points 33–44 and borrow setup are shortened, preserving map-sampling order.

The rejected empty-view shortcut, larger segment trees and distant-mountain experiment are excluded from v12.

## Files and reproduction

- [Rescue on Fractalus! - optimized v12 128KB.car](../../optimized%20version/Rescue%20on%20Fractalus!%20-%20optimized%20128KB.car): 131088 bytes.
- [Rescue on Fractalus! - optimized v12 128KB.rom](../../optimized%20version/Rescue%20on%20Fractalus!%20-%20optimized%20128KB.rom): 131072 bytes.
- [Rescue on Fractalus! - optimized v12 320KB-1MB.xex](../../optimized%20version/Rescue%20on%20Fractalus!%20-%20optimized%20320KB-1MB.xex): 262699 bytes.

`manifest.json` identifies the binaries and sources. `sources/` contains unchanged snapshots of the six MADS sources and both builders. Their original project-relative path layout remains in the code; run the build commands from the project root:

```text
python scripts/rebuild_current.py --mads PATH_TO_MADS
python scripts/benchmark_v12.py
python scripts/report_v12.py
python scripts/plot_v12.py

```

Rerunning the benchmark resumes its matching frozen plan; it is not a new independent study. Raw observations, the plan, report and chart are in `results/v12/`.

The build retains the Esc fix and the XEX loader with corrected level-end music descriptors. Earlier validation of the identical candidate covers the renderer, pause/resume and controlled XEX level transitions; scope and evidence hashes are in `results/v12/functional-validation.json`.

## Precision and comparisons

### PAL

v12: **8.932929 FPS**, 95% bootstrap interval [8.854022, 9.011272].

| Reference | Reference FPS | Delta FPS | Gain | Gain 95% interval |
|---|---:|---:|---:|---:|
| Original, full data | 6.271731 | +2.661198 | +42.4316% | [+41.0787%, +43.7830%] |
| v11, full data | 8.782928 | +0.150001 | +1.7079% | [+1.0790%, +2.3444%] |
| v11, same 155 assigned trials | 8.743560 | +0.189369 | +2.1658% | [+1.6135%, +2.6986%] |

Natural early ends: 8/155. Measured duration range: 36.823–60.188 s. Mean wall time per trial including boot/menu: 15.81 s; measurement call alone: 11.16 s.
### NTSC

v12: **8.149851 FPS**, 95% bootstrap interval [8.080669, 8.218045].

| Reference | Reference FPS | Delta FPS | Gain | Gain 95% interval |
|---|---:|---:|---:|---:|
| Original, full data | 5.591516 | +2.558335 | +45.7539% | [+44.4038%, +47.0836%] |
| v11, full data | 8.003108 | +0.146743 | +1.8336% | [+1.1732%, +2.4948%] |
| v11, same 155 assigned trials | 7.991736 | +0.158115 | +1.9785% | [+1.4598%, +2.4902%] |

Natural early ends: 9/155. Measured duration range: 36.664–60.161 s. Mean wall time per trial including boot/menu: 15.51 s; measurement call alone: 10.98 s.

## Method and data checks

The new series contains 310 independent cold boots: 155 PAL and 155 NTSC, on four isolated emulators. It took 20.25 minutes of wall time. These are fresh v12 measurements; original and v11 results are retained historical data.

The 78/77 assignment and start order were fixed in advance. Each start has 170 warmup video frames. FPS counts whole `$B516` presentation intervals against the Atari clock. The nominal 60 s window closes at a whole interval; a natural end closes it earlier. Descent input is 1 s joystick up and 3 s neutral, repeated every 4 s. Input deadlines match the predefined cycle schedule. No state transfer between ROMs, outlier removal or retries of valid inconvenient samples were used.

The packet transport retains every presentation event, input deadline and the RAM snapshot at the selected endpoint. The emulator executable is unchanged from the audit; the unbuilt paused-loop patch was not applied. `integrity.json` confirms counts, monotonic timestamps, FPS arithmetic and input deadlines.

Confidence intervals use 20,000 percentile-bootstrap replicates, seed 2026102912. Whole start plans are resampled separately within the 78 and 77 groups, preserving dependence with v11 and historical original descent. Original straight flights use an independent plan and are resampled independently. Gain is a ratio of means, not a mean of percentages. Scenario labels remain internal even though the headline result is combined.

Full references and v12 have different sample sizes. The v11 comparison restricted to the same 155 assigned trials reduces the effect of sample composition and gives an additional estimate of the improvement since v11. It does not replace the headline original-game reference. The test describes the two predefined automatic scenarios, not every possible game situation.

## Data files

- `plan.json`, `analysis-plan.json`: frozen measurement and analysis plans.
- `flights.jsonl`, `flights.csv`: 310 individual results; JSONL retains all presentation and input timestamps.
- `summary.json`, `integrity.json`, `run.json`: statistics, integrity checks and execution time.
- `functional-validation.json`: hashes and exact scope of previous tests of the identical binaries.
- `charts/V12_COMPARISON.png` / `.svg`: chart with English labels.

ROM SHA-256: `4959a82ab36528a0448a40e6178fdb72d321e5d1e23c258036f5e22e51cfa20e`.
Plan SHA-256: `7ebe095a3bc081af064114256a0590d2ed78afb91ac8644bd15d987b55ac4e8b`.
