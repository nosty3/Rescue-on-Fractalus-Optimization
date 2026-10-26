Historical research document. Old paths and results refer to the experiment described; the current implementation is documented in docs/OPTIMIZATIONS.md and aggregate results in docs/benchmarks/METHOD.md (paths from the repository root).

[English](V5_OPTIMIZATION_OPTIONS.md) · [Polski](V5_OPTIMIZATION_OPTIONS_PL.md)

# Fresh v5 audit — optimization options

Date: 2026-10-21. Scope: investigation, overview, and cost models. Game code was not changed; no new release or prototype ROM was built.

Reference: released v5, XEGS 128 KiB, SHA-256 `9a6445651455d011008238ab5038e4186badc9e4b7a84a2881b6ab2e02d0d5ef`.
The last measured mean remains **7.367256 FPS**, not the model results below.

## New measurements

Call and instruction profiles were collected from scratch in four scenarios: straight, right, left, and fast flight to the right. Each run covers 3000 PAL frames, 106,704,000 machine ticks, about 60.17 s: eight profiler runs in total. Emulator: 800XL, 64 KiB RAM, PAL, no accelerators; all runs ended in flight mode. No new FPS measurement of a modified game was made.

Additionally, v5 instructions were traced on 58 retained renderer inputs covering different directions and levels. Observation did not change executed code. Old renderer inputs do not replace new whole-game tests.

| Area | Mean share of machine time, exclusive cost |
|---|---:|
| Mountain profile subdivision/rasterization, entry `$982A`, bank 5 | 33.56% |
| Division `$8224` | 9.55% |
| Filling `$9308`, bank 9 | 9.19% |
| Other `$87D3` pipeline code | 6.83% |
| Geometry preparation `$8309` | 6.49% |
| Segment clipping `$9627` | 5.17% |
| Projection `$85D4`, excluding division calls | 5.17% |
| Clearing `$9214` | 4.76% |
| Flight-logic interpolation in RAM `$7EEB` | 2.03% |
| Flight logic `$7310`, excluding children | 1.71% |
| Main sound routine `$B91C`, excluding children | 1.54% |

Whole VBI including children takes about 11.82%; all sound about 3.38%. These include table entries and **must not be added to them**. The profiler also attributes machine delays, including DMA, to instructions. Banked addresses in raw profiles use a different representation from CPU addresses: e.g. `$8002B82A` corresponds to CPU entry `$982A` in bank 2, which switches to bank 5. Cost remains attributed to that entry despite a JMP-based bank switch.

## Options and trial order

Gains below are increments over 7.367256 FPS. They are conditional models, not measured results or confidence intervals. Unsuccessful integration can yield no gain or a regression. Detailed budgets are in `estimates.json`.

| Priority | Idea | Preliminary FPS gain | Memory and assessment |
|---|---|---:|---|
| 1 | Skip division normalization if its scratch state is dead | **+0.10–0.15** | No extra bank. Strongest cycle model; state use outside the renderer still needs proof. |
| 2 | Specialized subdivision paths for widths 4 and 5 | **+0.05–0.15** | Estimated 1–3 KiB code; needs good space allocation among depths. Do not switch banks per leaf. |
| 3 | Replace interpretation of fixed direction tables with generated code for 45 points | **+0.03–0.09** | About 16–32 KiB, 2–4 banks; select bank once per routine. Budget only, no generator yet. |
| 4 | Exact `$7EEB` interpolation using a 4 KiB table | **+0.03–0.08** | One bank for table/helper; a small self-modifying fragment in existing RAM code is possible. Arithmetic verified, implementation cost estimated. |
| 5 | Improve hot branch/table alignment relative to page boundaries | **+0.007–0.028** | Alignment and relocation, usually without a new bank. Loss data measured. |
| 6 | Use the same table for RAM multiplication `$7CD6` | **+0.006–0.021** | Extra helper, shared table with option 4. Final state and early exits need separate proof. |
| 7 | Further simplify the 14-channel sound loop | **+0.006–0.022** | Small code change; estimated 2–5 fewer cycles per entry. Lower priority than mountains/division. |
| 8 | Extend filling specialization to first rows 33–48 | **+0.004–0.014** | Extra code; worthwhile only without a new bank switch per column. |

Ranges are not summed: call frequencies, VBI timing, code layout, and competition for bank space change. Options 4 and 6 share a resource and some costs.

## Rationale for the main options

### 1. Division without normalization

Current code scales numerator and denominator by a shared power of two until bit 6 of the denominator's high byte is set, then computes eight quotient bits. For `0 <= N < D < 32768`, the eight-step algorithm can compute `floor(256*N/D)` without initial scaling: the shifted remainder fits in 16 bits and the quotient is independent of the common scale factor.

In 2766 real calls, denominator values were 64–15330, and normalization averaged 2.363 shifts. The instruction-path model also accounts for changed subtraction frequencies after normalization removal. Result: 13–164 cycles saved, mean **66.862**, with the same quotient in all 2766 cases. The current-routine cost model matched execution of unchanged 6502 code for 163 cases spread across the dataset.

The new profile averages 21,602 calls per 3000 PAL frames, implying about 1.44 million potential CPU cycles saved over that period.

Key condition: `$AE/$AF/$B0/$B1` will not retain their previous normalized values. Observation found no read before overwrite within the 58 renderer calls. After the final division in each call, their use remains unresolved: trace the rest of the main loop, VBI, other game modes, and flag dependencies, especially V. If this state is needed, reconstructing it may consume the saving. Full equivalence is not yet proven and this is not a finished patch.

### 2. Short mountain segments

The current renderer specializes width 3. The trace contained 2824 width-4 and 1704 width-5 entries. Known width can avoid some tests, subdivision-stack handling, and returns while preserving rounding and occlusion-check order. The model assumes 35–55 gross cycles saved per such entry, subtracting 5 cycles of extra path selection from each of 11,455 entries wider than 3.

Bank 5 has limited space: generated code ends at `$966E`, while the switching entry is at `$982F`. Start with the most frequent depths, share code, or limit rarer specializations. An additional bank can hold an entire variant, but frequent per-leaf switching may erase the saving. The estimated range excludes such an expensive design.

### 3. Fixed geometry commands

`$8309` chooses one of four tables at `$9A55/$9A82/$9AAF/$9ADC`, then interprets its 45 entries starting at `$8360`. Command data is fixed. Four code variants could be generated with predetermined operations and point addresses, eliminating command reads, some bit shifts/tests, loop-index handling, and some addressing overhead. Calculations depending on ship position, altitude, and clipping still run.

Budget: 20–45 fewer cycles per point, 45 points, about 439 calls per run; 40 banking cycles per call subtracted. Size 16–32 KiB is an estimate to confirm with a generator, not a completed allocation.

### 4. Table-driven interpolation and RAM

RAM code `$7EEB–$7FC1` performs three eight-step interpolations. Preserving its rounding matters more than replacing it with an ordinary linear-interpolation formula. A four-bit contribution table was derived: `T[4bit_mask][8bit_value]`, or **16*256 = 4096 bytes**. A full eight-bit contribution can be assembled from two reads: the upper mask half with the value, and the lower mask half with the value shifted by 4. The two segment endpoints use a mask and its complement.

Checked all 65,536 contribution identities and 1000 full random interpolation cases against original 6502 code: result `$62` matched. This does not yet establish agreement of all flags, registers, scratch memory, interrupt timing, or future code cost.

Estimated budget: 200–350 net cycles saved per interpolation, 2250 calls per run. The routine itself accounts for only 2.03% of time, so even a large speedup cannot yield several additional FPS.

## Where self-modification makes sense

| Location | Possible use | Condition for benefit |
|---|---|---|
| RAM interpolation | Change table-read operand high bytes according to a half of the fraction | Several reads per configured operand; the table provides the main gain, SMC is an access option. |
| Larger renderer block copied to RAM | Put a block-constant buffer, mask, or table address into instruction operands | Parameters must be reused; first find and verify available RAM. |
| Geometry commands | Small variant updated once per larger batch of work | Prebuilt ROM variants are usually simpler; patching per point consumes the saving. |

Do not automatically replace every `LDA ($80),Y` with self-modifying `LDA abs,Y`. A read usually saves 1 cycle and a store another 1, while writing a new 16-bit operand costs at least two `STA abs`, or 8 cycles, before address preparation. Two different operands may cost 16 cycles. The rasterizer's address often changes after just one pixel.

Similarly, inserting a denominator into 24 immediate operands of unrolled division would cost 96 cycles in stores alone. Faster reads save too little for one division. Only 949 of 2766 denominators matched the preceding one; this does not justify that design.

SMC requires RAM: adding a cartridge bank does not make ROM writable. Account for code initialization after cold boot and START, data-bank switching, and sharing with interrupts. `SEI` does not block NMI/VBI. Prefer private code for a given context or prove that interrupts cannot execute partially modified instructions. No new free RAM region for renderer relocation has yet been confirmed.

## Smaller options and limitations

- The trace contained 55,116 extra page-crossing cycles, including 17,700 for branches. Removing all would be an unrealistic ceiling; the layout model assumes removing 25–65% without regressions elsewhere.
- A first row above 32 occurred in 501 of 2436 columns (20.57%). v5 already unrolls sky stores for these columns too. Do not count the entire sky-unrolling saving again; only a small first-iteration/subsequent-fill gain remains.
- 5019 of 13,893 pixel stores hit the same address as the previous store. Combining masks or caching the current byte is a reserve option, roughly **0–0.03 FPS** after detection cost. Preserve horizon/visibility update order; hit percentage alone does not prove a gain.
- Fill transition tables might combine AND/ORA and mask computation. However, 15 distinct mask states occurred and many columns end quickly. State-selection, table-layout, and banking costs are not yet counted. Without them there is no credible FPS estimate; lower priority than the main table.
- v4/v5 clearing already has 1880 direct stores. Further instruction unrolling will not materially help. Removing stores requires changing buffer organization and proving old contents are never read.
- A large quotient table does not directly fit 16-bit arguments; reciprocal tables require multiplication and exact correction. First investigate the much cheaper normalization skip.
- Do not treat WSYNC or DLI NOPs as ordinary redundant instructions. Some cost preserves the timing of color and display-register changes.
- Do not reduce logic or sound update frequency as part of these proposals: that changes gameplay behavior rather than providing equivalent code optimization.

## Available banks and their use

In v5, **banks 10, 11, 12, 13, and 14 are entirely empty: 40 KiB**. There is currently no need to expand beyond 128 KiB. This is ROM, not extra Atari RAM; the study still targets a 64 KiB RAM machine. Bank 15 is fixed. Bank 7 contains a copy of the old fixed bank and was not counted as free without auditing every bank selection.

A reasonable working allocation: one bank for table arithmetic, 2–4 for geometry variants, remaining space for rasterization variants. The largest versions of every idea may not all fit simultaneously. Switch banks once at routine entry, not per pixel. The v5 VBI guard recognizes markers below 10. Using banks 10–14 requires extending it and testing START/VBI/DLI; merely placing code in an empty bank is insufficient.

## Estimation method and materials

CPU costs used `F_new = F_v5 / (1 - alpha * saved_cycles / T)`, with `T=106704000`; `alpha=1..1.5` is explicit sensitivity analysis for DMA and code placement, not a measured coefficient or probability. VBI is periodic, presentations synchronize with PAL, and a faster game may encounter somewhat different scenes. Actual FPS therefore requires later measurement of a complete variant, including scenarios that may slow down.

Evidence and scripts:

- `results/research_v5/summary.json`: four profiles, costs, and frequencies.
- `results/research_v5/arithmetic-models.json`: verified arithmetic models.
- `results/research_v5/divider-liveness.json`: scope of scratch-state observation.
- `results/research_v5/estimates.json`: explicit budgets and FPS conversion.
- `scripts/research_v5_*.py`: profiling, code inspection, tracing, arithmetic, and calculations.

Raw profiles and local RAM reads support analysis on the current machine. The repository copy contains the report, scripts, and compact results, without RAM dumps. Trace scripts require old local renderer inputs excluded under the agreed repository scope. If these files are lost, collect new inputs; identical traces cannot be promised.
