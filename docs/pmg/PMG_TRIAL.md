Historical research document. Old paths and results refer to the experiment described; the current implementation is documented in docs/OPTIMIZATIONS.md and aggregate results in docs/benchmarks/METHOD.md (paths from the repository root).

[English](PMG_TRIAL.md) · [Polski](PMG_TRIAL_PL.md)

# First PMG optimization trial based on v8

2026-10-21. Experiment, not a new release. ROM SHA256: `0c8226e1f58ad26b2a103cbf59c4b8b23fdb87caac0e22f2586a83513a859880`.

## Result

| Flight | v8 | PMG trial |
|---|---:|---:|
| straight | 7.513947 | 7.592925 |
| right | 7.742457 | 7.776753 |
| left | 7.844759 | 7.922579 |
| fast_right | 7.781929 | 7.765336 |

Pooled result: v8 **7.720697 FPS**, trial **7.764418 FPS**.
Difference **+0.043721 FPS**, **+0.566%**.
The +0.05 FPS threshold was **not reached**.
The trial was not promoted to a new release. v8 remains the recommended release.

Method: total presentations at $B516 divided by total PAL time, four standard scenarios of at least 3000 frames each, with 50 warm-up frames. Baseline is the retained v8 measurement using the same protocol and initial states. This is not an arithmetic mean of four FPS values. Speed changes may alter flight trajectories; one series provides no confidence interval.

## Changes

- Bar at $A55C: differential update. Given a consistent previous image, writes |new-old| bytes instead of 57. If the old value is zero or values fall outside 0..55, uses the original full redraw. Old value zero covers initialization after clearing state $2830..$28D5. If both values match, the original update skip remains.
- 21-row copy: seven iterations of three rows; final counter $BD=0.
- Five-row clearing and copying: unrolled loops, preserving X/Y and $BB.
- Two three-row missile loops: unrolled, preserving other missiles' masks.

Code occupies free bank 2 space: $83CA..$8470 and $84B0..$84F3. It does not overlap clipping at $8380..$83C9, buffer guard at $84A0..$84AE, or geometry continuation at $84FD. No extra bank or new RAM variable. Code is called from VBI, whose existing guard makes bank 2 available. No SMC was used; these simple variants do not require it.

## Verification

- 5268 CPU cases: all 56x56 bar transitions with a consistent previous image, 300 full-redraw-path cases, 600 cases for each of three other routines, and 32 retained game inputs. All RAM except dead stack, GTIA, and A/X/Y/P/SP matched.
- 320 emulator bar-handler entries: 80 each after cold boot, in basic flight, and in level 10/26 states. Every previous nonzero state matched the actual bar bytes.
- Cold boot, flight, level 10/26 trials, restarts from expansion banks, and another start: passed. Some trials end in mode 0, so they do not mean uninterrupted flight for the entire test.

In the CPU model, the changed 21-row copy saves 106 cycles per active call, five-row handling up to 44, and three-row handling up to 12. Skipped updates gain nothing. The bar can be slower on large jumps: the worst difference in the exhaustive transition test was 233 extra cycles. This first trial did not tune another threshold for switching to full redraw.

## Limitations and reproduction

Differential updating assumes consistency between the old value and image memory. Tests cover the listed scenarios, not every possible gameplay sequence. Old external save states with inconsistent state are not covered. Physical Atari hardware and every PMG animation variant were not tested.

Sources: `src/pmg_short_loops.asm`, `src/pmg_bar_delta.asm`.
Local build: `python scripts/build_pmg_trial.py`, requiring `build/buffer_sync.rom` and MADS at `tools/mads/bin/windows_x86_64/mads.exe`. The script generates these sources.
Tests: `scripts/test_pmg_trial.py`, `scripts/validate_pmg_trial.py`, `scripts/stress_pmg_trial.py`. Some require retained local states.
Experimental binaries: `build/pmg_trial.rom` and `build/pmg_trial.car`.
The v8 files in dist were not replaced.
