Historical candidate research promoted to v12. Full study: ../benchmarks/V12_REPORT.md.

# Further optimization within 128 KB — working candidate

2026-10-29. Comparison baseline: v11 with the retained standalone `$AA` shortcut (SHA-256 `7bd31c022afd3c3e81e161106b66851c0d12c26a04864c8569d510b99eb917d3`). Candidate: `4959a82ab36528a0448a40e6178fdb72d321e5d1e23c258036f5e22e51cfa20e`. The cartridge remains 128 KB, without extended RAM or changes to graphics, draw distance or intended game speed. This is not a numbered release; published v11 and its XEX are unchanged.

## Accepted changes

1. **Test the first occlusion-scan point earlier.** If it already rules out subtree rejection, return to exact subdivision before preparing the group counter. The conservative height bound and occlusion condition are unchanged.
2. **Four-column group-count table.** A small table in existing bank-5 padding replaces `TYA/CLC/ADC/LSR/LSR/TAY`. It preserves the original 8-bit arithmetic, including wraparound at widths 253–255. Placing it at `$9600` avoids indexed-read page penalties.
3. **The whole-segment entry scan also keeps its threshold in A.** Four memory CMP instructions replace four LDA/CMP pairs; INX preserves A. A separate `Hmax=0` exit protects the subtract-one transformation rather than applying it unconditionally.
4. **Remove more Y depth bookkeeping.** Specialized d0–d4 paths use Y for bitmap operations without redundant INY/DEY/immediate LDY or restoration after failed culls. Generic fallback explicitly receives **Y=5**. This differs from ilmenit's generator for the older d0–d7 implementation; copying Y=8 would be incorrect. The actual caller reloads Y from `$272E` after rendering.
5. **Ilmenit's compact geometry improvement.** Batch classifiers 33–43, classify point 44 inline and shorten borrow setup with CMP. Coordinate calculation and map-sampling order are retained. This idea and broader Y removal come from ilmenit's package; the underlying renderer/cache were developed in the earlier nosty/ChatGPT, Solo/Opus and subsequent v11 stages.

MADS sources: `candidate.asm` (bank 5), `sky_b9.asm` (retained `$AA`, bank 9), and `geometry_bank10.asm`–`geometry_bank13.asm`. No new RAM variables or banks. Bank markers and buffer-clear synchronization retain v11's protocol.

## Rejected trials

Occlusion thresholds were tuned on 40 scenes across five depths, several values and two coordinate-descent sweeps. Most omissions regressed. The best old configuration saved only approximately 20 cycles per scene; the candidate instead improves the scan itself without fitting thresholds to those maps.

Two versions merging visible equal-height pixel pairs in one byte matched the image but **increased cost** versus their respective versions without merging, by approximately 413 and 346 cycles per scene. Recognition and cache/flag preservation consumed the benefit. Neither is included. This does not rule out a different future batching design.

## Code cost

Below are 80 identical scenes, with positive savings relative to standalone `$AA`. Rows are complete variants, not increments to add together:

| Variant | Mean cycles saved/scene | Reduction |
|---|---:|---:|
| `cull_early` | 378.65 | 0.3457% |
| `cull_groups` | 531.01 | 0.4848% |
| `cull_root` | 926.70 | 0.8461% |
| `depth` | 2099.90 | 1.9172% |
| `pair_12` | 513.91 | 0.4692% |
| `pairdepth_12` | 1753.53 | 1.6009% |

Final candidate: **320 scenes, 2108.95 cycles saved per measured rendering interval, 1.9291% reduction**. The 40 separate k=4,12,… scenes yield 1.8815%; they were not used to tune thresholds. All 320 comparisons match the bitmap, horizon, active cache, live state and final CPU flags.

**Scope matters:** recorded `$A331/$A36F` windows cover clearing, projection/terrain and fill; geometry preparation occurs earlier. Geometry was checked separately in 320 cases: identical active RAM and CPU registers/flags, averaging **176.69375 cycles saved**. These numbers are not percentages of whole-game speedup.

## Limited FPS pilot

64 cold boots: 2 ROMs × PAL/NTSC × straight/descent × 8 preselected starts. Nominal 15-second windows finish on a complete `$B516` presentation interval; all 64 flights completed their windows without game termination. Neutral warmup of 170 video frames, a one-second north joystick pulse every four seconds, four separate emulators and the existing fast transport. No states were transferred between ROMs; corresponding initial maps matched.

Both scenarios have 50/50 weight; percentages use the ratio of mean FPS, not an average of scenario percentages:

| System | Baseline with $AA FPS | Candidate FPS | FPS change | Gain |
|---|---:|---:|---:|---:|
| PAL | 8.7814 | 8.9573 | +0.1759 | +2.00% |
| NTSC | 7.5275 | 7.6312 | +0.1036 | +1.38% |

Individual scenarios:

| System | Scenario | Baseline FPS | Candidate FPS | Gain |
|---|---|---:|---:|---:|
| PAL | straight | 8.9700 | 9.1482 | +1.99% |
| PAL | steering | 8.5929 | 8.7664 | +2.02% |
| NTSC | straight | 7.9729 | 8.1178 | +1.82% |
| NTSC | steering | 7.0821 | 7.1445 | +0.88% |

The result is promising, but **this is an eight-start pilot with shorter flights, not 155 flights of 60 seconds**. It does not replace official averages or establish a new gain over the original game. `pilot-results.json` also includes indicative 95% bootstrap intervals, resampling complete paired starts and retaining both scenarios. Eight clusters limit their precision. The 0.05 FPS threshold is now advisory, following the user's decision.

## Validation and reproduction

- 4000 random segments: clipping, heights/seeds, existing bitmap and HD cache 108–152; matching bitmap, entire horizon, cache and X/SP. Individual exits need not preserve A/Y/flags identically because the actual caller does not consume them in that form.
- 332 explicit `Hmax=0` cases, widths 1/2 across interior positions: matching results.
- 160 scenes from native candidate execution, PAL/NTSC, random directions and firing: matching rendering, live state and all final flags. Six Esc pause/resume cycles passed.
- All levels, physical hardware and accelerators were not exhaustively tested. The XEX counterpart and its separate tests are described in [XEX.md](XEX.md). The buffer-availability wait procedure was not changed.

Build with `python experiments/compact_128/build.py`. Requires the local published v11 ROM, six local ASM files and project MADS; ilmenit's package/generators are not required. SHA-256 verifies the output. Run the sole CAR/ROM in this experiment's top directory: `Fractalus - compact candidate 128KB experiment`.

Research: `research.py` reproduces scan, Y-removal and pair-merging trials; `validate_candidate.py fuzz`, `zero`, `geometry`, `native` reproduce validation; `native_pilot.py` runs the pilot or loads matching saved results. An independent study requires a separate output directory; cached results are not a new measurement. `write_report.py` regenerates reports. Intermediate sources, binaries and rejected images are under `work/`.

The next separate direction remains exact projection division, with careful integration-cost accounting. It was not changed in this stage.
