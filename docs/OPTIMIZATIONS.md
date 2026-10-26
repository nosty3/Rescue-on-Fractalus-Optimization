# Rescue on Fractalus! optimizations — complete description of the current build

[English](OPTIMIZATIONS.md) · [Polski](OPTIMIZATIONS_PL.md)

This document describes all changes present in **v10.1**, organized by code area rather than release sequence. The reconstruction entry point is [rebuild_current.py](../scripts/rebuild_current.py); MADS sources are in [src](../src/). Experimental sources have been retained for further research, but the builder determines what goes into the release. Not every file in `src` is an active patch.

## Esc fix in v10.1

Resuming the game at $AB1D now removes nine stack bytes instead of eight. The extra byte is the bank marker pushed by the VBI guard introduced in v2. The resume path bypassed normal bank restoration, corrupting the return address. MADS source: `src/pause_resume_stack.asm`; the builder applies this patch after the plotter. The ROM differs from v10 only at offset $1EB1E ($08 → $09).

A candidate identical to the release passed 12 pause/resume cycles in PAL and 12 in NTSC; five successive images were confirmed after each resume. The FPS results below are for v10; no new measurements were made for v10.1. [Diagnosis](research/ESC_DIAGNOSIS.md).

## Results and scope

The game runs on Atari XL/XE machines with 64 KB RAM, using an XEGS 128 KB cartridge (CART 14), in PAL and NTSC. Resolution and terrain detail are unchanged. Expanding the ROM provides room for specialized code and tables; simply repackaging the game into a larger cartridge does not make it faster.

| System | Original | v10 | Gain over original |
| --- | ---: | ---: | ---: |
| PAL | 6.4421 FPS | 7.6359 FPS | **+18.53%** |
| NTSC | 5.8043 FPS | 6.9377 FPS | **+19.53%** |

These are means of 155 independent automatic flights per version and system. The [method and limitations](benchmarks/METHOD.md) apply to both series. The microtest results below come from studies of individual routines: they are not additional measurements of final FPS, and their percentage gains must not be added together.

Original ROM SHA256: `1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68`.

Optimized ROM SHA256: `afa04d6802a03333516936b4912f8f7abf23a1837362ac2b0ceaa83b6b6414da`.

## Rasterizer and terrain subdivision returns

At `$9937`, the STX/TXA operations were reordered to share the required part of the entry path. Post-subdivision jumps at `$9A18`, `$9A36`, and `$9A52` target `$9939`, skipping a repeated boundary check and a store of the unchanged `$82` value. This saves 7 cycles per such return. Preserving the semantics of `$82` is essential; moving the store unconditionally would be incorrect. Source: `raster_order.asm` and address patches in the builder.

## Plotter row-address tables and Y stores

Bank 5 uses two 48-byte ROM tables at $9768 and $97A8. For heights Y=104..151, the row address is $1010+96*(151-Y). Effective read bases $9700 and $9740 eliminate page crossings. General paths, including unusual heights, retain the original RAM tables.

Removed 48 STY $B5 instructions from specialized paths in which Y is restored by LDY with a constant depth anyway. The number of bank switches and buffer synchronization are unchanged. Source: `v10_plotter.asm`.

Across 58 scenes, the average saving was 1248.09 cycles per rendering-and-filling operation. Also passed: 6000 random segments, 309 edge cases, and 232 VBI checks. B5 after the renderer and B4/B5 after subsequent geometry may differ as scratch values not used by the later computations examined; dead stack memory was excluded. Registers and flags match at the tested exits. The [v10 report](benchmarks/V10_REPORT.md) describes the scope and limitations, together with the full FPS measurement.

## Integer division

The routine at `$8224` keeps the high part of the remainder in the accumulator, reducing RAM accesses and branches. The implementation occupies 224 bytes. A further change directs entry to `$8235` instead of `$8231`, skipping unnecessary normalization when the calling conditions hold. The exact quotient is preserved, including zero-divisor handling; the ordinary range examined is `0 <= N < D < 32768`.

Scratch fields `$AE..$B1` need not contain identical normalized data on return because they are not subsequently used as output. This is a deliberate exception to whole-memory comparison, not permission for arbitrary differences. The first 50,042 cases showed a 13.57% reduction in routine cycles. Further verification covered 20,033 cases, 58 scenes, and 232 VBI variants; 176,642 cycles were saved in that test set. Sources: `division_fast.asm`, `opt14_division.asm`.

## Mountain profile generation

Bank 5 separates handling of the eight subdivision depths. Known indices were replaced with zero-page addresses, repeated calculations removed, and fixed properties of Y and carry exploited. Shorter paths were added for width 3, then widths 4 and 5 at depths 1–4. Other cases use the general path.

These specializations preserve rounding, carries, and the V flag at the right edge; they do not approximate the terrain mathematics. Tests covered 58 scenes and series of 5000, 5000, and 6000 cases. Sources: `mountain_cull.asm`, `opt14_width45.asm`; detailed routine analysis is retained in the [mountain profile study](terrain/MOUNTAIN_PROFILE.txt).

### Skipping fully occluded subdivisions

Skipping uses a conservative upper bound on the height of all future points, not just segment endpoints. For width `w`, the bound is:

```
E(w) = 0                                      for w <= 2
E(w) = floor(w/4) + 1 + max(E(floor(w/2)), E(ceil(w/2)))
Hmax = min(255, max(left_height, right_height) + E(w))
```

A subdivision can be skipped only if the occluding profile in every covered screen column is at least as high as `Hmax`. Screen-boundary conditions are preserved. Differences in dead stack memory are allowed; tests deliberately varying unused memory checked that it did not later become an input to the computation.

## Clearing the screen buffer

The original entry at `$9214` performs 44 stores for each of 42 columns. For the two typical X values, direct stores were generated for 1848 bytes plus 32 edge bytes: bank 6 for X=3 and bank 8 for X=51. Unusual X values still use the original loop. A, X, Y, flags, and `$94` are preserved according to the routine's contract.

A typical call fell from 9792 to 7586 or 7590 cycles, including bank switching. Tested 456 cases, including all X values. Sources: `clear128_entry.asm`, `clear128_bank6.asm`, `clear128_bank8.asm`. The builder determines the source files and exact assembly process.

## Terrain filling

The first row retains the original semantics. In later rows, OR-testing four bytes allows zero groups to be skipped; other data uses the general path. The assumption that examining only the horizon was sufficient proved inadequate and was not included in the final algorithm.

Code in bank 9 replaces repeated calculation of `$1010 + 96*r` with specialized addresses and absolute,Y access. It reconstructs `$80/$81`, carries, and exit conditions. It preserves the special masks `$95=0`, `$96=$55` and tables `$3A00/$3B00`. Starting positions 0–32 have specializations; 33–48 use a general path. Lengths 1–48 are unrolled, while 49 and above use a fallback rather than cutting off the bottom of the image. Banking occurs once per routine.

Verification covered 58 scenes, 256 random bitmaps, and 56 boundary cases, including lengths up to 69. In the comparison set, cost fell from 774,828 to 718,543 cycles. Active sources: `fill_final.asm`, `fill_rows.asm`. Earlier `fill_zero` and `fill_first` variants are research material.

## Geometry: from interpreters to specialized code

Four tables of 45 commands at `$9A55`, `$9A82`, `$9AAF`, and `$9ADC` were replaced with programs in banks 10–13. Classification of points 0–32 was unrolled using fixed addresses; points 33–44 share code to fit within an 8 KB bank. Tables at `$9D00/$9E00` replace four-bit shifts. The invariant `$8B` value is computed once; `$9F` is preserved on the stack.

Entry from bank 2 at `$835E` leads to `$9863`. The bank switch at `$9890` continues at `$9893`, and exit goes through `$98E0`, bank 2 at `$98E7`, and `$84FD`. Verification checked the active bank, carries, signs, and rounding. Successive stages saved 82,736 and a further 70,336 cycles across 58 scenes. Also compared: 1000 random cases and actual emulator calls. Current final sources: `opt14_geometry_entry.asm`, `v7_geometry_bank10.asm` through `v7_geometry_bank13.asm`.

## Screen clipping

Entry `$963D` was redirected to `$8380` in bank 2. The fast path identifies cases with X=0 and zero high coordinate bytes, checks ordering and the left boundary, and decides whether to draw or reject. Mixed cases return to the original algorithm: they restore the skipped initial normalization and continue at `$9648`.

Exits `$972E`, `$974A`, `$9788`, `$9797`, and scratch fields `$9F/$B5` are preserved. Tests of 3000 random cases and 58 scenes matched; the tested set saved 105,365 cycles. Source: `v7_clipping.asm`.

## Interpolation and self-modifying RAM code

Bank 14 contains 16 pages of arithmetic contribution tables and a four-bit shift table. Results preserve the original's exact rounding. RAM code at `$7EEB..$7FC1`, with the routine at `$7F20`, modifies eight instruction operands so that subsequent reads have ready-to-use addresses. All these operands are initialized before use.

The code is loaded from bank 1. It requires no additional RAM beyond the game's available area. DLI does not use this routine, and VBI restores the active bank. SEI alone would not protect against NMI: safety comes from the interrupt and banking contract. All 5000 random cases matched, including poisoned scratch memory. Cost was 314–339 cycles, averaging 326.4432, including banking. Sources: `opt14_interpolation_bank14.asm`, `opt14_interpolation_ram.asm`. Use a cold boot so that RAM contains the correct code.

## Sound and small logic loops

The mixer's 12-iteration minimum/maximum selection loops at `$BB19/$BB3E` were unrolled. Helpers occupy 322 and 344 bytes, use bank 2 and jumps from the fixed bank, and do not add a separate bank switch for each sound operation. Tie-breaking order and channel state are preserved. Savings per call were 65–76 and 53–54 cycles respectively.

Flag `$0718` is cleared at entry and then after each handled event, except for the final channel. This removes 13 redundant stores when there are no events; with many events, overhead may be greater. The change does not guarantee a speedup on every path.

Compared 6000 mixer cases, 5800 flag cases, 400 synthetic scenarios, and 1160 scene calls. A study of 271 POKEY writes preserved their values and order; this does not mean identical timing for every audio sample. Sources: `lowlevel_sound_minimum.asm`, `lowlevel_sound_maximum.asm`, `lowlevel_sound_flag.asm`.

## PMG: drawing, erasing, and the indicator bar

Three- and five-row loops were unrolled, and the 21-row copy handles three rows per iteration. The bar handled at `$A55C` updates only the changed segment. A full redraw remains for an old value of zero and values outside 0–55; this matters during initialization such as 0→29.

Bank 2 helpers occupy `$83CA..$8470` and `$84B0..$84F3`, without overlapping clipping at `$8380..$83C9`, synchronization at `$84A0..$84AE`, or continuation at `$84FD`. They are called in VBI with bank 2 already active. No new variables or self-modification were added to PMG.

Verification covered 5268 CPU cases, 320 bar checks, the first 40 real calls after startup, levels 10/26, and restarts from expansion banks. All RAM except the dead stack, plus registers and flags, matched. A historical four-flight test showed roughly +0.044 FPS over the preceding build; this is not a separate statistical estimate of PMG's contribution to the current 155-flight series. Sources: `pmg_short_loops.asm`, `pmg_bar_delta.asm`. [PMG research](pmg/) also describes ideas that were not implemented.

## Banking and interrupts

The `$8000..$9FFF` window is selected through `$D500`, while `$A000..$BFFF` remains the fixed bank. After ROM expansion, a copy of the old fixed bank is in bank 15; the old bank 7 is not automatically free space. The `$9FFF` marker is `$FF` for bank 2 and the bank number for expansion banks. The guard at `$BFEA` recognizes numbers below 15 and restores the bank after VBI.

The RAM trampoline at `$7FFE` has an operand crossing `$8000`, so its correctness depends on banking and the interrupt guard. Title-screen VBI and START may abandon the current context. Restarts from banks 2, 5, 6, and 8–14 were checked. The NOP at `$AE88` and WSYNC stores to `$D40A` were not removed: they are part of display timing dependencies.

| Bank | Use in the changes |
| --- | --- |
| 1 | Image of code copied to RAM |
| 2 | Entry points, clipping, PMG, sound, and synchronization |
| 5 | Mountain profile and skipping occluded subdivisions |
| 6, 8 | Specialized buffer clearing |
| 9 | Terrain filling |
| 10–13 | Specialized geometry |
| 14 | Interpolation tables |
| 15 | Fixed bank |

## Buffer synchronization and the left-side artifact

The game signals a completed buffer through flag `$42` at `$A34A/$A3AF`. VBI switches the ANTIC display and then clears the flag at `$B518` (entry `$B516`). If the main loop starts clearing the buffer before this acknowledgement, it can write into memory still being displayed. Since clearing starts on the left, the symptom is a transient terrain fragment on that side.

Diagnostics also found the original entering clearing while a switch was pending: 51 of 120 observations, versus 18 of 45 in one faster build. These are not percentages of visible artifacts or measurements of their frequency throughout the game, but evidence of a risky operation order.

Clearing entry `$9214` now goes to `$84A0..$84AE`, which waits for `$42=0`. Geometry calculations before this point can still run ahead. A/X/Y, flags, and SP are preserved; the helper temporarily uses two stack bytes. For a zero `$4A` mode, a bypass avoids waiting for inactive switching. Source: `buffer_sync.asm`.

Tested 256×4 waiting variants, 240 clears with `$42=0`, cold boot, START, and levels 10/26. A test of 3000 continuous frames reproduced the old artifact; it was not found in the checked candidates after the fix. This is not proof against every possible display bug. Do not remove the wait merely to improve FPS: that would reintroduce the buffer race.

## Verification and reproducibility

The new builder reconstructs the current ROM without old release files, the emulator SDK, or saved states. It checks the output SHA256, CAR equivalence, and application of IPS to the original. It verifies the v9 stage and then the final v10.1 ROM, CAR, and IPS byte for byte. The [instructions](REBUILD.md) describe requirements and distinguish building from historical research.

CPU microtests compare specific routine contracts; they do not replace an emulator with DMA, VBI, and DLI. Early apparently high results of 8–10.7 FPS were rejected because of a faulty trampoline and instructions unsupported by the model. Subsequent tests required strict opcode handling and bank/PC checks. A profile capped at 4096 samples is not a complete counter of all calls.

Tests were performed in a CPU model and headless Altirra; they do not certify every mission or constitute testing on physical Atari hardware. The user confirmed that v9 works. Current FPS measurements cover automatic flight without steering, not all gameplay behavior.

## Ideas retained for future research

Other small options were not implemented: page alignment, multiplication at `$7CD6`, further restructuring of sound-channel scanning, and specialization of fill starting positions 33–48. They are retained in the [options overview](research/V5_OPTIMIZATION_OPTIONS.md), [future directions](research/FUTURE_DIRECTIONS.txt), and [PMG audit](pmg/PMG_AUDIT.md). They are hypotheses, not parts of the released ROM. Further work used an estimated-gain threshold of 0.05 FPS, with a separately approved exception for a small PMG change. Finishing the current work does not prove that an absolute optimum has been reached.

An additional mixer-channel-selection cache study was rejected: after accounting for writes from RAM, the internal mixer saving averaged only 14.63 cycles/VBI before subtracting external overhead. This experiment is not in v10. New shortcuts for perspective scaling were likewise excluded.
