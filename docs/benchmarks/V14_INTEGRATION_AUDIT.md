# v14 audit and integration options

[English](V14_INTEGRATION_AUDIT.md) · [Polski](V14_INTEGRATION_AUDIT_PL.md)

Analysis performed locally on 2026-11-03, before publication as v14. Solo's input package was left untouched outside the published repository. The published sources are in `src/v14/`, and retained results are in `results/v14/`; exploratory variants remain in the local audit workspace.

## Conclusion

**v14 itself is the best basis for further work, retaining the 128 KB cartridge.** It is a substantial optimization of v11. Copying entire v12/v13 banks over it would replace faster Solo implementations with older ones. Our existing incremental geometry implementation also loses against Solo's new geometry code.

Ilmenit's compiled trees remain an optional direction, but **the tested integrations with v14 increase rendering cost**. More cartridge space does not automatically improve performance. Further work would require a generator built around Solo's new algorithms, rather than a direct port of current v13.

The independent `$AA` shortcut is assessed in the final study below. Removing the remaining Y bookkeeping is possible if hot-code addresses are preserved, but saves roughly 11–13 cycles per image, not a substantial FPS increase.

## Verifying the performance claim

| System, 50/50 mean | Original | v11 | v14 | v14 / original | v14 / v11 |
|---|---:|---:|---:|---:|---:|
| PAL | 6.2717 FPS | 8.7829 FPS | **10.9172 FPS** | **+74.07%** | **+24.30%** |
| NTSC | 5.5915 FPS | 8.0031 FPS | **9.8961 FPS** | **+76.98%** | **+23.65%** |

These means were recomputed from the **620 supplied v14 observations**, 155 per video system and scenario. They are not presented as 620 new measurements performed in this audit. I independently ran **50 native cold-boot flights**, using predefined positions spread across every series and also covering natural early ends. All 50 exactly reproduced the package's FPS, presentation-interval count, and entry RAM hash. This strongly confirms reproducibility.

Detailed v14 means: PAL straight 11.32771777; PAL descent 10.50674380; NTSC straight 10.36047279; NTSC descent 9.43175131 FPS. Solo's table gives NTSC combined as 9.8962. Computing directly from the JSON files yields 9.89611205, which rounds to **9.8961**. This is a minor table/data discrepancy.

Conditions: Atari 800XL/64 KB, no accelerator, fresh emulator and cold boot for every flight, historical `menu_frames`, 170 warmup frames, up to 60 seconds of Atari time. Presentations counted at `$B516`; elapsed time from the emulated clock. Descent repeats 1 s joystick up / 3 s neutral. Natural ends retained, no outlier rejection. The 50/50 statistic is half the mean FPS in each scenario; percentage gain is the ratio of means minus one.

Faster VBI already runs in the menu and shifts the POKEY RANDOM read. Identical START timing therefore does not guarantee the same planet between v11 and v14. Original/v11 comparisons use independent series, not identical trajectories. No cross-ROM state transfers were used for FPS measurements.

## What Solo actually changed

| Area | New implementation | Relationship to our changes |
|---|---|---|
| Mountain rasterizer, bank 5 | Tight subtree height bound Ex(w), fused split/leaf paths, shorter exits, better Y use and code placement | Replaces much of the code targeted by v12 and v13 trees; gains cannot be added |
| Fill, bank 9 | `out = x XOR (Q[x] AND SK)`, `SK' = Z[x] AND SK`; roughly 32 rather than 43 cycles per row, including lower-row specialization | Faster general path; AA can be added separately, but its benefit must be measured again |
| Geometry grid, banks 10–13 | Map-index movement tables, carry reuse, combined spiral-corner steps, fewer loads/stores | Broader than v12's grouped classification of points 33–44 |
| Geometry preparation and postpass | Tables/calculations in bank 4 and faster unrolled postpass in bank 2 | Makes complete recomputation cheaper, undermining the old cache |
| VBI | Bank-7 multiplication tables, faster interpolation, sound queue with minimum-validity state, faster min/max | Substantial new work, not double-counted v11 optimizations |
| Projection and edge loop | Improved division paths, dead-remainder elimination, scale tables, less loop overhead | Should be retained alongside the new rasterizer |
| Waiting for the previous image | Safe projection work before the wait completes, without framebuffer writes | Reduces idle time; procedure cycle counts alone do not describe the entire FPS gain |

Sources: `package/tools/gen_fill9.py`, `gen_scene.py`, `gen_scene7.py`, `gen_proj.py`, `patches_vbi2.py`, `patches_reorder.py`, `patches_proj.py`, `package/src/v11/raster5.asm`, `package/src/vbi2_snd14.asm`, and `package/AGENT.md`. Author descriptions were treated as claims to check, not proof of correctness.

## Integration variants and measured costs

The following are **CPU cycles on identical input states**, excluding ANTIC DMA and native VBI scheduling. They are not FPS percentages. Positive cost means a regression relative to v14.

| Experiment | Result | Decision |
|---|---|---|
| Whole v12 fill replacing Solo bank 9 | +3537 cycles/image, 48 scenes | Reject; retain Solo's faster fill |
| v12 grid banks 10–13, retaining Solo preparation/postpass | +1272 cycles/scene preparation, 24 scenes | Reject; retain Solo's grid |
| v12 rasterizer replacing Solo bank 5 | +11166 cycles/image, 48 scenes | Reject; image agreement does not compensate for the slowdown |
| Remaining INY instructions removed without preserving layout | About +68 cycles/image, 384 fresh scenes | Reject this form: altered page alignment costs more than the removed instructions |
| Same INY removal with hot-loop addresses preserved | About **−11 cycles/image**, 384 fresh scenes; −13 in the older 48-scene set | Small option, insufficient to claim a noticeable FPS improvement |
| v13 512 KB trees on v14 | **+1557 cycles/image**, 384 fresh scenes | Do not integrate this implementation |
| v13 1 MB trees on v14 | **+2027 cycles/image**, same scenes | Do not integrate; selecting more trees hurts here |
| Widths 40–64 after Solo's hidden-subtree rejection, tighter Ex(w), shorter exits | **+276 cycles/image**, 384 fresh scenes; 27 extra banks | Better than a direct port, still slower; fits 512 KB, while 1 MB executes identical code |

Trees were also checked on 3611 real rasterizer calls, with no differences in the framebuffer, clearing heights, or occlusion data. Some wide segments are faster, but dispatch, bank switching, and slower cases consume the saving. Whole-pipeline checks remain deliberately strict: they report differences at `$0170/$0171` (the relocated lazy-clear jump pointer), and `$B4` for the 1 MB variant (left-tree scratch state). These are not presented as fully approved releases. With no performance justification, full native FPS series were not run for them.

**Incremental geometry:** on 320 identical states, old v13 full geometry averages 10031 cycles, the existing cache 9039, and Solo full geometry **7497**. The old cache is **1542 cycles slower** than Solo. Even an optimistic cost model replacing its preparation with Solo's faster version remains about **395 cycles slower**, before extra relocation/integration costs. This assesses the particular existing cache, not every possible future incremental algorithm. Its old code starting at `$7F70` also overlaps the new multiplier through `$7F78`, and bank 7 now contains multiplication tables.

## AA shortcut — full study

**310 new flights** were completed (155 PAL + 155 NTSC), using four emulators and the frozen v12 mixed plan: 78 straight and 77 descent flights per system. The comparison uses the exactly corresponding v14 observations from the package, not a different subset.

| System | v14, matching subset | v14 + AA | FPS difference | 95% difference CI |
|---|---:|---:|---:|---:|
| PAL | 10.9302 | 10.9590 | +0.0288 | [-0.0166, +0.0743] |
| NTSC | 9.8850 | 9.8652 | -0.0198 | [-0.0723, +0.0331] |

**AA is not recommended for the default v14 variant.** PAL does not establish a benefit, the NTSC estimate is negative, and both intervals include zero. This does not prove the shortcut never helps; the adopted method has not confirmed a benefit. Bootstrap: 10000 replicates, preserving menu/trial pairs and separate scenario strata, seed 742027. No observations removed. Natural ends: PAL 11/11 (v14/AA), NTSC 10/8.

The v14 means here differ from the main table because this table uses 155 mixed flights per system, whereas the main table uses all 310 supplied flights per system. Both use 50/50 weighting regardless of the 78/77 stratum sizes.

309/310 initial AA entry hashes matched v14. PAL trial 54 once had a different full-RAM hash, although its terrain hash matched. Two repeated v14 flights and one AA flight exactly reproduced their respective FPS; repeated RAM captures from both ROMs were identical. The full dump from the original anomalous read was not retained, so the differing bytes could not be identified; no speculative cause is asserted. The observation remains in the analysis. See `trial54-recheck.log` and `entry-difference-analysis.json`.


## Losslessness checks

- MADS rebuilding exactly reproduces the supplied ROM, and applying the IPS reproduces the same file. ROM size: 131072 bytes; CAR size: 131088 bytes, type 14.
- ROM SHA-256: `63baff0da13b5da2678eba44d4b392e7fa3de6df18044233a7eb7b19d796b3c7`.
- Supplied check runner executed successfully: **14/14** checks, covering the rendering pipeline, waiting, rasterizer, fill, projection, edge loop, VBI, and geometry.
- Fresh v14 captures: **384 pipeline states, 384 geometry states, 384 VBI states**, with straight flight, descent, turns, firing, PAL/NTSC. No output-image/state mismatches in v11→v14 comparisons, with explicit dead-field and changed-code exclusions.
- Fresh geometry: approximately 10209→7503 cycles. Fresh rendering pipeline: approximately 101598→85183 cycles. These are not FPS figures.
- VBI: identical hardware-write order and values; about 3741→3285 cycles. The reference must align just bank 4's return marker: v14 now actually executes there, whereas v11's `$FF` marker means return to bank 2. The initial unadjusted comparison had zero RAM/hardware differences and six expected return-bank differences. Banks were not broadly ignored to hide this.
- Multiplication: **all 65536 operand pairs**, zero differences, average 136.46→66 cycles.
- Projection: **10000 random cases**, zero differences, including 1002 rare visibility paths.
- Sound: **10000 synthetic queues**, including channel allocations, effect initialization, volumes 0–15, and unique hardware voices. **160568 identical hardware writes**, no RAM/allocation/return discrepancies; 4725→3757 cycles per synthetic queue. This is neither an average-VBI measurement nor a listening test of every gameplay situation.
- Work during waiting: 96 fresh scenes × 4 wait lengths, no discrepancies, including the path that stops early projection for special visibility cases.
- AA shortcut: 384 fresh pipelines and 1000 randomized fill cases without differences. Those pipelines average about +10 cycles rather than a saving, motivating the separate full-flight test.

- Extended rasterizer test: **10000 segments, zero discrepancies**, including 1070 edge cases, 1046 wide, 2263 small, 2263 lazy-clear cases, and 1128 height-clamping cases. The reference places the v11 rasterizer inside v14 so callers and return addresses match; return addresses were not incorrectly transferred between different edge-loop implementations. Scratch A/Y/P differences were checked by finishing the remaining pipeline, with identical outputs. Average segment cost in this synthetic set: 4464→4001 cycles.
- **8/8 native functional tests**: v14 and v14+AA × PAL/NTSC × 64 KB/1088 KB RAM. At least 2738 flight frames per test, sustained turns in both directions, descent/ascent, continued presentation checks, and Esc pause/resume. No crashes; see `functional-summary.json`.

This is strong evidence of equivalence, **not a formal proof over every game state**. The changes do not lower resolution, shorten draw distance, or simplify mountains; they preserve the computed image for identical inputs. Different cold-boot planets may result from shifted RANDOM reads. Physical Atari hardware and all possible accelerators were not tested.

## Recommended integration

1. Adopt the v14 source/generator set built on v11 as a coherent 128 KB base. Do not overlay older binary banks.
2. Retain the new VBI, geometry, projection, rasterizer, fill, and work during waiting together. Tests support equivalence and native measurements confirm the large gain.
3. Assess only additions that still contribute independently: AA as reported above, optionally the small Y change with preserved alignment. Do not add historical v12/v13 percentages.
4. Do not merge the existing incremental geometry or tree set. A future tree generator should target Solo's rasterizer and include dispatch costs from the outset.
5. XEX needs separate relocation work: new banks 4/7, changed sources for banks 2/3/5/9/10–14, resident code, and return markers. The old v11 builder explicitly assumes all banks except 5/6/8/9 remain unchanged; substituting the new ROM does not produce a finished port. No new XEX was released in this audit.
6. Preserve v11's XEX music-pointer fix and level-transition test. Expanded carts must not overwrite mixer `$9D3B–$9FD4` or active bank-2 geometry. Bank-3 `$FF` bytes at `$963A–$97F0` are not automatically free: they are read before flight.

## Artifacts and reproduction

- `reproduction-summary.json`, `native-reproduction/`: independent reproduction of Solo's measurements.
- `package/results/full155_v14_*.json`: supplied 620 observations; original/v11 historical reference: project `release-v11/results/v11/summary.json`.
- `native-aa-full/`, `aa-study-summary.json`: full new AA study and comparison with its matching v14 subset.
- `validation/`, `check-quick.log`, `multiply-exhaustive.log`, `sound-queue-fuzz.json`: correctness and cost checks.
- `incremental-cost.json`, `tree-profile.json`, `fresh-pipeline-*.json`: option comparisons.
- `build_variants.py`, `build_y_aligned.py`, `build_trees.py`, `build_trees_after_cull.py`: local experiment generators. Files under `build/` are **experiments, not a new release**.
- `native_study.py`, `capture_native.py`, `verify_fresh.py`, `native_functional.py`, `analyze_aa.py`: reproduction and validation procedures.

Python uses `tools/up38_audit_deps` in `PYTHONPATH`, MADS at `tools/mads/bin/windows_x86_64/mads.exe`, and the emulator at `tools/bridge/AltirraBridge-nightly-windows-x86_64`. Four independent emulator processes; measurements use Atari time rather than host wall time. The workspace retains logs of unsuccessful initial harness adaptations; these are not counted as successful checks. No rejected variant was published to the repository.
