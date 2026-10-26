# PAL and NTSC measurement method

[English](METHOD.md) · [Polski](METHOD_PL.md)

v10 has its own series of 155 PAL flights and 155 NTSC flights. The [v10 report](V10_REPORT.md) presents results, validation, and uncertainty. It repeats the START timings from the v9 schedule and the rules below. The original and v9 remain historical references; control flights reproduced the v9 results. The table below documents the earlier study of the original and v9.

Historical results come from two series of **155 original flights and 155 v9 flights**, separately for PAL and NTSC. Sources are the [PAL report](pal/PAL_REPORT.md), [PAL protocol](pal/PROTOCOL.md), [NTSC report](ntsc/NTSC_REPORT.md), and [NTSC protocol addendum](ntsc/PROTOCOL_ADDENDUM.md).

| System | Original FPS | v9 FPS | Gain | 95% confidence interval for gain |
| --- | ---: | ---: | ---: | --- |
| PAL | 6.4421 | 7.5623 | 17.39% | 16.46–18.32% |
| NTSC | 5.8043 | 6.8977 | 18.84% | 17.90–19.78% |

## Conditions and counter

Every flight ran in a fresh Altirra process, starting from a native cold boot of the appropriate cartridge: Atari 800XL, 64 KB, no accelerator. No state was transferred and no game memory was patched. The joystick stayed centered, without firing, turning, diving, or using the booster.

The frozen schedule uses seed 2026102303 and 155 distinct START timings per version, sampled without replacement from menu frames 3000–3599. In 31 blocks, five trials of each version were interleaved. PAL repeats the same schedule in frames; this does not imply identical maps across standards or versions.

At the first entry to `$A32E`, START was released and 170 warm-up frames ran: about 3.41 s PAL or 2.84 s NTSC. Measurement counts complete intervals between completed images at `$B516`. Time is taken from emulated Atari ticks, using 1,773,447.5 Hz PAL or 1,789,772.5 Hz NTSC, and includes DMA and interrupts. FPS = complete intervals / duration of those intervals; it is neither the VBI rate nor host-computer speed.

The 15/30/60-second windows are nested portions of one flight. The first complete interval past each limit is included. If the game ends a flight naturally before the limit, complete intervals before leaving flight mode are counted, excluding the ending animation. Such trials remain in the mean; neither extremes nor shorter flights were discarded. This affected 3 original and 4 v9 flights in PAL, and one flight of each version in NTSC.

## Parallel execution and analysis

NTSC began sequentially; after 86 flights, the remaining 224 ran in parallel after comparison of four complete 60 s scenarios. PAL used four processes after comparing four 15 s scenarios sequentially and in parallel. Controls required matching measurement events and RAM. Processes had separate ports, tokens, and files; the aggregate was saved in plan order. Controls are not included in the main mean.

The primary statistic is the mean of individual flight FPS values, with equal weight per flight. Gain is `100 × (v9_mean / original_mean − 1)`. It is not an average of percentages from arbitrarily paired maps. NTSC sample size was chosen after a pilot; PAL was assigned the same size in advance. Time-weighted results and a stratified bootstrap with 50,000 replications were also checked. The natural-ending rule was clarified after the first 47 NTSC flights; it was fixed before PAL measurement. The NTSC report preserves details and limitations of that addendum.

Confidence intervals are approximate and concern the scenario distribution of this protocol. They do not establish performance in all valleys, turns, levels, or missions. The same version may have different FPS on a different map. A difference between two short flights should not be equated with a code change.

## Files and historical studies

- [PAL data](../../results/pal_isolated_main) and [NTSC data](../../results/ntsc_isolated_main) contain the plan, individual trials, summary, and consistency-check results.
- [PAL validation](../../results/pal_parallel_validation/validation.json) and [NTSC validation](../../results/ntsc_parallel_validation/validation.json) document parallel-execution checks.
- [charts/](charts/) contains English PNG and SVG charts for both series, used in the README.
- [history/](history/), [ntsc_cold_20x2/](ntsc_cold_20x2/), [ntsc_repro_audit/](ntsc_repro_audit/), [ntsc_isolated_pilot/](ntsc_isolated_pilot/), and [ntsc_parallel_validation/](ntsc_parallel_validation/) describe how the current method was developed.

Historical results from short flights, shared states, trimmed means, and the four-flight PAL set do not replace the current table. Old paths, version numbers, and recommendations in those studies refer to the time they were written; old files can be recovered from the corresponding commit. Raw RAM dumps and screenshots are not published.
