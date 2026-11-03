# Fractalus up74 - technical handoff for an AI agent

This file is for a coding agent (and a human who wants the details) who wants to verify, rebuild or merge
round 2 of our work on Rescue on Fractalus! for Atari XL/XE. up74 is built on **v11 by nosty3** (his repo,
commit `3726a11`, ROM SHA256 `ec019821...`). It lists every change on top of v11, the bytes it occupies, the
assumptions it relies on, how it was verified and how to repeat each check. Read README.md first.

## 1. Result

155 flights x 60 s per scenario and TV system with nosty3's protocol (`docs/benchmarks/METHOD.md`, scenarios as
in `V11_REPORT.md`). Details and raw data: `results/results.md`, `results/full155_up74_*.json`.

| Scenario | Original | v11 | up74 | up74 vs v11 | up74 vs original |
|---|---:|---:|---:|---:|---:|
| PAL straight | 6.4421 | 9.0779 | 11.3277 | +24.78% | +75.84% |
| PAL descent | 6.1013 | 8.4879 | 10.5067 | +23.79% | +72.20% |
| PAL 50/50 | 6.2717 | 8.7829 | 10.9172 | **+24.30%** | **+74.07%** |
| NTSC straight | 5.8043 | 8.3120 | 10.3605 | +24.64% | +78.50% |
| NTSC descent | 5.3787 | 7.6942 | 9.4318 | +22.58% | +75.35% |
| NTSC 50/50 | 5.5915 | 8.0031 | 9.8962 | **+23.65%** | **+76.99%** |

Original and v11 are his published numbers. Our `tools/bench.py` reproduces his flights to the digit (620/620 in
round 1), and it is deterministic: rerunning trials 2 and 4 of the up74 series while preparing this package gave
the same `fps` and the same entry hash as the JSON files, PAL straight and descent.

## 2. Build and file identity

Requirements: Python 3.11+ (tested 3.13), `py65` 1.2 (`pip install py65`), MADS 2.1.0 (Mad-Assembler,
`mads.exe`). For the emulator tools: the AltirraBridge server + Python SDK (fork github.com/ilmenit/AltirraSDL,
tested build `fed7854`) and a clone of nosty3's repo (for `results/ntsc_isolated_main/plan.json`).

Paths, `tools/paths.py`, each overridable by an environment variable:
`FRACTALUS_WORK` (work dir: base ROM, builds, scenes; default `<package>/work`), `FRACTALUS_MADS` (default
`<WORK>/mads/mads.exe`), `FRACTALUS_NOSTY` (his clone; default `<WORK>/repo`), `ALTIRRA_BRIDGE` (dir with
`AltirraBridgeServer.exe` and `sdk/python`).

```
python tools/build.py --name=up74 v11src vbi2_mul vbi2_sound vbi2_interp scene_grid scene_pre reorder proj2 loop2
```
writes `<WORK>/build/up74.rom` and `up74.car` (CART type 14, XEGS 128 KB). The base is `work/base/v11.rom`,
identical to `optimized version/Rescue on Fractalus! - optimized 128KB.rom` in his repo at `3726a11`; `build.py`
asserts its SHA256. Every patch asserts the base bytes it overwrites (`put(..., expect=...)`, SHA256 of whole
regions in `patches_proj.py`), so a different base fails loudly instead of building something wrong.

| File | SHA256 |
|---|---|
| `bin/fractalus_up74.car` | `8362476209a3740162c304b0eff710615af45656838f5f9a88fbe63e88160526` |
| `bin/fractalus_up74.rom` | `63baff0da13b5da2678eba44d4b392e7fa3de6df18044233a7eb7b19d796b3c7` |
| `work/base/v11.rom` | `ec01982121b70baca35f04568617965c3164e716e0a5eb3c6ebcbb123566a868` |

`bin/up74_from_v11.ips` turns `v11.rom` into `fractalus_up74.rom` (167 records, no RLE).

Patch order matters: `proj2` after `reorder` (reorder checks bytes at `$87D3` and `$984C` that proj2 changes),
`loop2` after `proj2`. Build time is a few seconds.

Generated sources (edit the generator, not the output; the build calls most generators itself):

| Source | Generator | When |
|---|---|---|
| `src/v11/sky_b9.asm` (bank 9 fill) | `tools/gen_fill9.py` | run by hand, then build |
| `src/scene_b10..b13.asm` | `tools/gen_scene.py` | during the build (`patches_scene.py`) |
| `src/scene_b4.asm`, `src/scene_post2.asm` | `tools/gen_scene7.py` (its docstring still says bank 7: the code went to bank 4) | during the build |
| `src/proj3.asm`, `src/proj_*.asm` | `tools/gen_proj.py` | during the build (`patches_proj.py`) |
| bank 7 tables (no source file) | `tools/gen_vbi2_mul.py` | during the build (`patches_vbi2.py`) |

Hand-written: `src/v11/raster5.asm` (bank 5; started from Astra's v11 source, then edited in round 2),
`src/vbi2_*.asm`, `src/reorder_*.asm`. Unchanged from v11: `src/v11/sky_b6.asm`, `src/v11/sky_b8.asm` (Astra's
sources). Regenerating writes files with the platform line ending; content is the same.

## 3. Machine facts (short; full list in the up38 AGENT.md, section 3)

- XEGS 128 KB: `sta $D5xx` selects the 8 KB window `$8000-$9FFF`, bank 15 fixed at `$A000-$BFFF`. After the
  bank switch the next opcode comes from the new bank at the next address, so cross-bank calls need landing
  bytes at the same address in both banks.
- Banks 0/1 are copied at boot to RAM `$4000-$7FFF` (resident code).
- The VBI guard (`$BFDA`/`$BFEA`) restores the interrupted bank from the marker byte `$9FFF` of the current bank.
  Every bank that runs code during flight needs `$9FFF` = its number. Bank 2 has `$FF` (restored as bank 2).
  New markers in round 2: bank 4 (`4`, scene_pre) and bank 7 (`7`, produced by the order of the multiply table
  pages). Bank 3 got `3` in round 1.
- Flight loop `$A32E`/`$A36C`: `jsr $8309` (scene), clear (`jsr $9214`), render (`jsr $87D3`), fill
  (`jsr $9308`), objects, publish the image in `$42`. VBI `$B4F4` flips the display list. `$B516` = image counted.

## 4. The changes

In order of merge into our master. Gains: native, PAL, 24 flights x 60 s, the build without and with the step,
unless noted; short series have about +-2 percentage points of noise, the final 155-flight result is separate.

| # | Change | Patch | Where | Gain (straight / descent) |
|---|---|---|---|---|
| 1 | Exact subtree cull bound Ex(w) | `v11src` | bank 5 `cull_extra`, `src/v11/raster5.asm` | +1.98% / +0.77% |
| 2 | Faster fill on the bitmap | `v11src` | bank 9, `src/v11/sky_b9.asm` (`gen_fill9.py`) | with 1: +4.11% / +2.69% |
| 3 | VBI round 2: multiply by tables, sound queue, terrain interpolation | `vbi2_mul`, `vbi2_sound`, `vbi2_interp` | bank 7, bank 14, resident code, fixed bank | steps 1-3: +8.14% / +6.99% (48 flights) |
| 4 | Scene `jsr $8309`: grid and prelude | `scene_grid`, `scene_pre` | banks 10-13, bank 4 `$9141-$9FFF`, bank 2 | +1.21% / +0.96% |
| 5 | Rasteriser rewritten | `v11src` | bank 5, `src/v11/raster5.asm` | steps 1-5: +20.33% / +18.72% (48 flights) |
| 6 | Projection during the beam wait | `reorder` | bank 2 `$87D7-$884D`, `$9FD5-$9FEE`; bank 3 | +2.04% / +1.10% |
| 7 | Projection and edge loop, round 2 | `proj2`, `loop2` | bank 3 `$97F1-$9F82`, bank 2 `$85D4-$87D2`, bank 14 | +2.59% / +2.69% |
| 8 | Shorter rasteriser exit | `v11src` | bank 5 | -0.56% pipeline cycles (within the noise of 24 flights) |

The render pipeline (from the clear to the end of the fill) of up74 takes 17.7% fewer CPU cycles than v11 on the
48 sample scenes (`equiv.py`, 107 619 -> 88 592 per image); `jsr $8309` 26% fewer (10 131 -> 7 471); VBI in
flight about 12% fewer (3 370 -> 2 979 per VBI on the sample).

### 4.1 Ex(w) (bank 5)
`cull_extra` skips a subdivision subtree when it cannot rise above the drawn horizon. The bound E(w) from
nosty3's analysis is replaced by the exact maximum excursion Ex(w), computed exhaustively for widths 3..64 and by
recursion up to 101 (from 102 the old E). Safety when the bound clips to 0: an interval with clipping has all
heights <= 103 = the starting occlusion (`$67`/`$6B`, constant, set by the render prolog).

### 4.2 Fill (bank 9)
Same column function as v11 (Astra's `build_fill_rows.py`), cheaper: row step `out = x ^ (Q[x] & SK)`,
`SK' = Z[x] & SK` (32 instead of 43 cycles), columns 0..40 without restoring the end state (the last column
does), specialised first rows 0..48, dispatch by RTS on HD. Depends on `$3A00`/`$3B00` being the standard tables;
the only writer in the ROM is `$5C96` from the constants `$5CC0-$5CC7`. Scratch `$96-$99` (dead after the
pipeline, in the DEAD list of `equiv.py`).

### 4.3 VBI round 2
- `vbi2_mul`: the logic multiply `$7CD6` (resident) is f(M,N) = sum over the bits of N of ceil((M>>k)/2) mod 256,
  linear in the bits of N, so f = T1[N>>4][M] + T2[N&15][M]: bank 7 (a stale copy of the fixed bank, never
  selected in v11) holds the tables, new code at `$7F4B-$7F78` (former NOPs), `jsr` operands at `$7C9B`,
  `$7CBC`, `$7564`. 136 -> 66 cycles, all 65536 pairs equal.
- `vbi2_sound`: bank 14 `$90C2-$9484`, fixed bank `$B922-$B923` (operand) and `$B9B0-$B9B7`. The mixer used to
  recompute the minimum volume three times per 25 Hz tick although its inputs had not changed; the event queue now
  has two loop states (minimum stale / valid), no work RAM. Exit through bank 2 `$9889` because `$B91C` is also
  called from the menu (`$B7E8`).
- `vbi2_interp`: bank 14 `$9490-$973D`, resident `$7F20-$7F45` (lerp) and `$7EEB-$7EF8` (wrapper). `$9000`
  directly, intermediate results on the stack, lerp with v1 in X.

### 4.4 Scene `jsr $8309`
- `scene_grid`: banks 10-13 (4 heading-quadrant variants, 45 spiral points) regenerated from the original code
  (the generator parses and asserts the template of every point): grid index by page tables, carry for
  `sbc $8c` from `cmp $80`, t in Y, corners by one 16-bit add. Tables `$9D00-$9EFF` and the marker kept.
- `scene_pre`: the bank 2 prelude (`$9148`, sin/cos `$8055`, four products `$8558`) as new code with tables in
  bank 4 `$9141-$9FFF` (free after the intro code). Bank 2: `$8309 jmp $9148`, `$9148 lda #4 / sta $d500`,
  `$914D jmp $830F`; the post-pass `$84FD` is unrolled at bank 2 `$8055` and the exit of banks 10-13 (`$98EA`)
  jumps there. Dead in bank 2 now (not `$FF`, but no longer executed): `$8055-$821B` outside the new code,
  `$8558-$85D3`, `$9150-$91DF`.

### 4.5 Rasteriser (bank 5)
About 10 thousand cycles less per image in straight flight (-20% in this bank): splits merged with leaves,
"ordinary split first" dispatch, Y dead (no `INY`/`LDY #k`), no `cull_entry` (it repeated the depth-0 test),
negated tables for shifts and the cull threshold, `STX $82` only where `$82` is read, clamp to `$97` out of line,
leaf of width 2 before its parent node, layout aligned so hot branches rarely cross a page (30 instead of 128
per image).

### 4.6 Projection during the beam wait (`reorder`)
The game waited for the beam before clearing the hidden buffer (1.1% of the frame in PAL). The wait loop `pre`
(bank 2 `$87D7-$884D`) now projects edge pairs of the next image while waiting; `$9214 jmp pre`; old wait_beam
`$9FD5-$9FEE` reused as landings; bank 3 `$984C jmp tail3`, `$9F83-$9FE1` (tail3 = `stx $a7` + the scalar
prolog tail byte for byte). Nothing in the wait touches the frame buffers. Wait drops to 0.1-0.2% of the frame.

### 4.7 Projection and edge loop, round 2 (`proj2`, `loop2`)
- `proj2`: bank 3 `$97F1-$9F82` rewritten (islands `$9847-$9853` and `$9D7E-$9D84` unchanged), `$9FC4-$9FD6`,
  `$9FE8-$9FFE`; the occlusion fill moved from bank 3 to bank 14 `$973E-$97FF`, `$9D88-$9DFF`, `$9F00-$9FCD`
  (`$9D78 jmp`); bank 2 `$9FE3-$9FE7`, `$87D3 jmp $9FE3`. Division without the dead shift counter `$9F` on the
  n = 0 paths (75% of coordinates), successful subtract falls through, last step of the first division only
  compares, X/Y scale from a table T[Q] = $80 + ((Q + Q>>1 + 1) >> 2), Y correction from `$270E` folded into the
  store, n = 1 and n >= 2 without the shift loop.
- `loop2`: bank 2 `$85D4-$87D2`, pair tables in the dead old division `$8224-$82B3` + sparse end `$82B4`. The loop
  walks pairs downwards in one page (`$86xx`); the clip gets X = p2, Y = p1 straight from the tables; `$28DB` and
  `$272E` are not written per pair, the end state is rebuilt once at the end.

### 4.8 Shorter rasteriser exit (bank 5)
New `rexit` at bank 5 `$9904` (`lda #2 / sta $d500` ends at `$9908`, execution continues at the bank 2 `RTS` at
`$9909`): no `php/pha` in bank 5 and no `pla/plp` in bank 2, 26 jumps retargeted. `o0_hidden` falls into `rexit`.
`plotchk` inlined at three `dg` sites. Bank 2 `$9907/$9908` stay in place (no longer used by the rasteriser).

## 5. Dead-state assumptions (what each patch relies on)

All of these were checked by the fuzzers and, where noted, by poisoning (random values put into the location
before the code runs, result must not change). If you change the code around them, re-check.

| Patch | Assumption |
|---|---|
| rasteriser (#5, #8) | After the return from the rasteriser A, Y and the flags N/Z are dead; C/V/I/D are unchanged by the exit (`lda/sta` only). Return sites: `$8674` in the edge loop (next `LDY` sets N/Z, A is overwritten by `$8600 LDA` or `$8705 PLA`) and `$9797` in the clip (`CPX` sets N/Z/C, then `LDA` or `RTS` to `$8674`). Poisoned on 6595 returns. |
| rasteriser (#8) | X at `o0_hidden` is dead (reloaded from `$60`). |
| all | Stack bytes below the current SP are not state. |
| rasteriser | Zero-page software stack `$82 $84 $86 $96-$9E $EB-$F3 $F5-$FD` and `$B5` are dead after the pipeline (DEAD list of `equiv.py`, round 1 liveness analysis). |
| fill (#2) | `$3A00`/`$3B00` hold the standard tables (built once from `$5CC0-$5CC7`). Only the V flag is carried between columns 0..40; column 41 restores A, X, Y, C, V, N, Z, `$80`, `$81`, `$95`, `$96`, `$9F` exactly. |
| proj2 (#7) | `$9F` (shift counter) is dead: read only by the clip `$8665`/`$9677` and the fill `$9312`, each after its own write. Remainder of the first division is dead. Flag `$10` in `$24B4,X` is read by nobody before the end of the routine. At the return A/Y/P are dead (callers: `ldy $272e / ldx ...`; `pre`: `pla/tay`), X is preserved. |
| loop2 (#7) | The V flag at `$88E8` differs from v11 and is dead (every path continues with `adc`, which sets V). `$9F = $14` only before `$972E`/`$974A`. End state rebuilt once: `$272E` = 2k+2 of the last pair after the p1 test, `$82-$86`, p2 copies, X, Y, `$28DB` = 43, C = 1. |
| vbi2_mul (#3) | The caller has bank 2 selected (checked: 4179 calls from the menu through flight with random input, all bank 2). `$28D6` is dead after the multiply (its only read is the `asl` in the loop; every caller writes it before). |
| vbi2_sound (#3) | `$066C-$0677` are always < 16 (checked on all writers), so min/max need no `and #$0f`. |
| vbi2_interp (#3) | The wrapper needs no `php/pha`: every caller overwrites A and the flags right after. |
| scene_grid (#4) | Scratch `$80` (restored at the end) and the output bytes of point 44 (written later in the same routine); RAM after `$8309` identical byte for byte. |
| scene_pre (#4) | Temporaries `$2277-$2279`, `$22A4`, `$22D2`, `$2300`, `$232E` are rewritten by banks 10-13 before the routine returns. The VBI guard never runs with bank 4 selected in v11 (checked from boot through the menu to flight), so the new marker `$9FFF = 4` does not change the intro. VBI reads nothing written by `$8309` except `$2809-$280C` (same values). |
| reorder (#6) | The work done in the beam wait (prolog tables, projection of edge pairs in the edge loop's order) touches no frame buffer and nothing the VBI writes or reads. It stops for good at the first point whose map cell `$0A00[$2276,X]` is non-zero (that projection would take the rare visibility path, which reads occ and draws); that point and the later ones are projected in the edge loop as before. The scalar prolog tail (`$2907/$2908`, `$28FC` from `$6A`, `$2912-$2915`, ...) runs after the wait because the VBI writes or reads those bytes. Checked by equivwait (N steps of work, then the VBI flip) and tearcheck. |

## 6. Pitfall: free `$FF` bytes that are read

**Bank 3 `$963A-$97F0` is `$FF` in v11 but is read before the flight** (menu/intro; for example `$9641-$9647`,
`$9660-$9666`, `$9700`: changing `$9700` from `$FF` to `$00` makes `$87` one higher at the flight entry). The
first version of `proj2` put code there; the game still worked, but the RAM at the first `$A32E` changed
(10 bytes: `$87`, sound `$06xx/$07xx`, `$3492-$3497`) and 0/24 benchmark flights entered the same planet. Found by
bisecting ROM bytes and comparing the RAM at the flight entry (`tools/entrydiff.py`). Who reads them is not known
(Altirra read breakpoints gave noise). The area stays untouched; `patches_proj.py` asserts it. Before using any
other free `$FF` bytes, run `entrydiff.py` against the build without the change (0 bytes must differ).

## 7. ROM map: what changed against v11, what is still free

Changed bytes per bank (`$FF` runs of 16 bytes or more counted as free):

| Bank | Changed | Ranges | Free `$FF` left |
|---|---:|---|---|
| 1 (resident `$6000-$7FFF`) | 96 B | `$7565-$7566`, `$7C9C-$7C9D`, `$7CBD-$7CBE`, `$7EF1-$7EF8`, `$7F20-$7F78` | none |
| 2 | 1248 B | `$8055-$81D0`, `$8224-$82F3`, `$8309`, `$85D4-$884D`, `$9148-$914F`, `$9215-$9216`, `$98EA-$98EB`, `$9FD5-$9FEE` | `$85E2`+30, `$8BCA`+20 (+ dead code, 4.4) |
| 3 | 1971 B | `$97F1-$9D5D`, `$9D85-$9FFE` | `$9D5E`+32, `$9DE7`+25, `$9F2C`+87; `$963A`+454 is NOT usable (section 6) |
| 4 | 3523 B | `$914A-$914F`, `$9200-$9FE7`, `$9FFF` | `$9150`+176 (padding before page-aligned tables), `$9FE8`+23 |
| 5 | 7287 B | whole bank reassembled | 1114 B in pieces: `$80AF`+128, `$865B`+20, `$88A4`+116, `$8C2C`+96, `$90EB`+359, `$93BE`+66, `$9700`+104, `$9798`+16, `$97D8`+87, `$98AD`+77, `$9FD2`+45 |
| 6 | 0 | (v11) | 1244 B |
| 7 | 8057 B | multiply tables, whole bank | none |
| 8 | 0 | (v11) | 772 B |
| 9 | 7170 B | whole bank regenerated | 1982 B: `$92F6`+23, `$949B`+357, `$9800`+108, `$9A1A`+1494 |
| 10-13 | about 7120 B each | regenerated | 368-411 B each |
| 14 | 2168 B | `$90C2-$9483`, `$9490-$97FE`, `$9D79-$9D7A`, `$9D88-$9DFF`, `$9F00-$9FCD` | `$9FCE`+49 |
| 15 (fixed) | 9 B | `$B922-$B923`, `$B9B1-$B9B7` | none |
| 0 | 0 | | |

Round 2 adds no RAM variables: scratch use is limited to bytes that are dead at that point (section 5). We found
no free RAM in flight either: the `$0800-$0AFF` PMG area is used (poisoning `$0900-$09FF` in flight changes the
game).

## 8. Verification

### 8.1 What "equivalent" means
For the same machine state at the entry of a changed routine, up74 leaves the same RAM `$0000-$7FFF` (both frame
buffers, the HD table and flags on page 1 included), the same A/X/Y/SP/P where they are live, and the same
hardware writes in the same order (VBI) as v11. Dead bytes and registers (section 5) are excluded only where
listed. Hardware write timing inside the visible lines is not changed: DLI code is untouched, VBI hardware writes
are compared in order and value. This is established by tests and liveness analysis, not by a formal proof.

### 8.2 What was run in round 2 (each change against the previous master)
| Change | Checks |
|---|---|
| Ex(w) | equiv 2017 scenes 0 diffs / 0 P; fuzzseg 10 000 segments 0 |
| fill | equiv 1387 + 300 fresh scenes 0 / 0 P; fuzzfill 10 000 0; hang 20/20; hangrand 8 x 60 s |
| VBI round 2 | vbieq 6728 states (straight, random steering and fire, descent, NTSC, menu) + states captured from the candidate, with poisoning: 0; mul_exhaustive 65536 pairs 0; long flights PAL/NTSC; hang 20/20 |
| scene | scene_eq8309 600 scenes, scene_fuzz8309 4000, scene_exh_pre 16 384, scene_post_fuzz 20 000: 0 |
| rasteriser | equiv 1687 scenes 0 / 0 P; fuzzseg2 (HD and page-1 flags, modes small/edge/clamp/lazy/wide) and fuzzseg; poisoning of A/Y/flags on 6595 returns; hang, hangrand |
| reorder | equiv 1387 scenes 0; equivwait 19 418 runs 0; tearcheck 0/300 twice; hang 10/10 |
| proj2 + loop2 | equiv 1387 scenes 0 / 0 P; equivwait 9800 runs 0; fuzzproj 30 000 0; fuzzloop 2000 0 (V only, dead); entry RAM identical (4 starts); hang 20/20, hangrand 8 x 60 s, tearcheck 0/300 |
| raster exit | equiv 1387 scenes 0 / 0 P; fuzzseg2 10 000 0; fuzzloop 2000 0 / 0 P; equivwait 3080 runs 0; entry RAM identical (4 starts); hang 20/20, hangrand 8 x 60 s, tearcheck 0/300 |

The full scene sets are 229 MB and not included. Scenes for the pipeline tools must be captured from a build
with the sky state (up38 or later); the bundled `f_n`/`f_r1` come from up38, hence `--hd152` (v11 and later use
HD 152 for a clean column, up38 used 151).

### 8.3 Run everything on the bundled sample (no emulator)
```
python tools/check_up74.py            # about 2 minutes: rebuild + SHA, IPS, reference ROMs, 11 checks
python tools/check_up74.py --full     # larger N + exhaustive multiply and heading sweep, about an hour
```
It rebuilds up74, applies the IPS, builds two reference ROMs and runs each check, v11 against up74 directly
except where the tool needs the same caller code on both sides:
- `ref_b5` = up74 with bank 5 copied from v11, for `fuzzseg.py`/`fuzzseg2.py` (they finish the pipeline in the
  candidate code with both register sets);
- `ref_proj` = the first seven patches without `proj2 loop2`, for `fuzzloop.py` (with v11 as reference the dead
  rasteriser bytes differ too).
Expected: `14/14 OK`. Our run while preparing the package (quick mode): equiv 48 scenes 0 / 0 P, equivwait 96 runs
0, fuzzseg2 300 0, fuzzseg 300 0, fuzzfill 500 0, fuzzproj 1000 0, fuzzloop 100 0 (P differs in bit 6 only = V),
vbieq 24 states 0, scene_eq8309 24 0, scene_fuzz8309 500 0, scene_post_fuzz 500 0; and separately
scene_exh_pre 16 384 0, mul_exhaustive 65536 0.

### 8.4 Each tool by hand
Simulator (py65; `REF`, `CAND` = `.rom` or `.car`):
```
python tools/equiv.py --hd152 REF CAND SCENES...            # pipeline: clear + mountains + fill, all RAM + P
python tools/equivwait.py --hd152 [--n=0,3,10] REF CAND SCENES...   # pipeline with N steps of work in the wait
python tools/fuzzseg.py REF CAND SCENE_DIR N [SEED] --hd152  # rasteriser segments (REF with up74 bank 2/3)
python tools/fuzzseg2.py REF CAND SCENE_DIR N [SEED] --hd152 # same + HD table, page-1 flags, more modes
python tools/fuzzfill.py REF CAND N [SEED] [SCENE.in]        # fill, random buffers and HD
python tools/fuzzproj.py REF CAND SCENE_DIR N [SEED]         # projection of one point, random N1/N2/D
python tools/fuzzloop.py REF CAND SCENE_DIR N [SEED]         # whole edge loop incl. rasteriser and clip
python tools/vbieq.py REF CAND VBI_DIR... --ignore=28d6 [--poison=SEED]   # VBI: RAM, hw writes, SP, bank, P
python tools/mul_exhaustive.py REF CAND VBI_DIR              # 65536 multiplications
python tools/scene_eq8309.py REF CAND SCENE_DIR...           # jsr $8309 from captured states
python tools/scene_fuzz8309.py REF CAND SCENE_DIR N [SEED]   # random heading, position, altitude, heightmap
python tools/scene_exh_pre.py REF CAND SCENE_DIR [INDEX]     # all heading combinations for the prelude
python tools/scene_post_fuzz.py REF CAND N SCENE_DIR [INDEX] # unrolled post-pass
```
Emulator (AltirraBridge; use `.car` files, a raw `.rom` does not boot as XEGS):
```
python tools/bench.py pal|ntsc[/descent] N SECONDS WORKERS OUT.json ROM...   # nosty3's protocol
python tools/hang.py ROM N                  # plan starts, neutral flight, reports a hang (300 frames no image)
python tools/hangrand.py ROM N SECONDS [SEED]   # random steering and fire
python tools/tearcheck.py ROM N_FRAMES [SEED]   # rows fetched by ANTIC equal across frames of one image
python tools/entrydiff.py ROM_A ROM_B TRIAL [pal|ntsc]   # RAM at the first $A32E, 0 bytes = same flight
python tools/capture.py ROM OUT_DIR N SEED PRESSES       # pipeline scenes (states at $A331/$A36F)
python tools/scene_capture.py ROM OUT_DIR N straight|random|descent TRIAL   # states at jsr $8309
python tools/capture_vbi.py ROM OUT_DIR N SEED PRESSES   # VBI states ($B46C)
python tools/capture_vbi2.py ROM OUT_DIR N SEED PRESSES random|descent|straight [pal|ntsc]
```
Package checks of this run: bench trials 2 and 4 identical to the JSON (PAL straight and descent), hang 3/3,
hangrand 1 x 30 s, tearcheck 100 frames 0 torn, entrydiff `ref_proj` vs up74 0 bytes.

## 9. Integrating with other changes (for example ilmenit's patches)

1. **Compare per bank first.** Section 7 lists every byte range up74 changes. Diff the other patch set against
   v11 the same way (a few lines of Python over the 16 banks). Non-overlapping banks can be combined directly.
   Watch the shared resources: bank 7 (whole, our multiply tables), bank 4 `$9141-$9FFF`, bank 14 (49 B left),
   the `$9FFF` markers, landing bytes after `sta $D500`, bank 2 `$9907-$9909` and `$9FD5-$9FEE`, resident
   `$7F20-$7F78`, fixed bank `$B91C-$B923` and `$B9B0-$B9B7`.
2. **Build ours on the merged base.** Put the other ROM into `build.py` `BASES` (path + SHA256) and build with
   `--base=NAME`. Every patch asserts the bytes it replaces, `proj2`/`loop2` assert SHA256 of whole regions,
   `vbi2_mul` asserts bank 7 equals the base. A failing assert names the bank and address of the overlap.
3. **Do not reuse `$FF` without `entrydiff.py`** (section 6). A change that moves RAM at the flight entry changes
   the planet and breaks paired comparisons.
4. **Re-run the checks on the merge**, REF = merged ROM without our patches (or without the other side's change),
   CAND = merged ROM with both: `check_up74.py` style (equiv, equivwait, fuzzers, vbieq, scene tools), scenes
   captured from the merged candidate (`capture.py`, `scene_capture.py`, `capture_vbi2.py`), then `hang.py`,
   `hangrand.py`, `tearcheck.py`, `entrydiff.py`, and the 155-flight benchmark.
5. If the other side changes code that our dead-state assumptions refer to (section 5: callers of the rasteriser
   at `$8674`/`$9797`, readers of `$9F`, `$28D6`, `$066C-$0677`, `$3A00/$3B00`), the assumption must be checked
   again, not only the bytes.

## 10. Caveats

- Same START, different planet: the shorter VBI already runs in the menu, so POKEY RANDOM is read at different
  cycles and the planet for a plan entry can differ from v11. Series are compared as independent, as in his report.
- The game does not run faster: the logic keeps its 25 Hz tick. More images per second means smoother motion.
- Cartridge only. The `.xex` for extended memory (up38) is not updated for round 2: `mkxex.py` does not know the
  new code in banks 4, 7, 10-14 and in the resident code.
- Tested in Altirra (emulation) only, not on physical hardware.

## 11. Package map

- `bin/` cartridge `.car`, raw `.rom`, `up74_from_v11.ips`.
- `src/` MADS sources (`opt h-`, `org` = CPU address): `src/v11/*` (banks 5/6/8/9) and the round 2 patches.
- `tools/` build, patches, generators, simulator, checks, benchmark (comments mostly in Polish, one-line usage at
  the top of each file). `check_up74.py`, `entrydiff.py`, `mul_exhaustive.py`, `scene_*.py`, `capture_vbi2.py`
  are portable copies of round 2 scripts made for this package; `mkhandoff74.py` built the package (our paths).
- `work/base/v11.rom` base ROM; `work/scenes/` sample states (24 each): `f_n` straight, `f_r1` random steering
  (pipeline, from up38), `vbi_r7` (VBI entry, random steering), `scene_rnd` (`jsr $8309`, random steering).
- `results/` 155-flight data and `results.md`. `report/index.html` results page (Polish). `docs/worklog_pl.md`
  round 2 working log (Polish).
