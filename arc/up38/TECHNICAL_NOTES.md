# Fractalus up38 - technical handoff for an AI agent

This file is written for a coding agent (and a human who wants the details) taking over work on
Rescue on Fractalus! for Atari XL/XE from build **v10.1 by nosty3**. It lists every change made on top of
v10.1, where it lives, what it must keep true, how it was verified, and what is still open.
Read README.md first for the short version.

## 1. Result

Measured with nosty3's own protocol (`docs/benchmarks/METHOD.md` of his repo): fresh emulator per flight, cold
boot, START after `menu_frames` from the frozen plan (seed 2026102303), 170 warm-up frames, centred joystick,
count completed terrain images at `$B516`, 60 s window of emulated ticks, early natural ends kept, equal weights.

| System | Original | v10.1 | up38 | v10.1 vs orig | up38 vs orig | up38 vs v10.1 |
|---|---:|---:|---:|---:|---:|---:|
| PAL (155 flights) | 6.4421 | 7.6359 | 8.9366 | +18.53% | **+38.72%** (95% bootstrap 37.13..40.31) | +17.03% |
| NTSC (155 flights) | 5.8043 | 6.9377 | 8.1670 | +19.53% | **+40.71%** (95% bootstrap 39.31..42.13) | +17.72% |

The original and v10.1 flights were re-measured with our replica of the protocol: all 620 flights
(2 versions x 155 x PAL and NTSC) match nosty3's published per-flight values exactly. So up38 is measured with
the same ruler, not a similar one. Raw data: `results/full155.jsonl`, summary: `results/fullreport.txt`.

Same START moment, different planet: the VBI changes (step 3) shorten VBI already in the menu, so POKEY RANDOM
is read at different cycles and the generated planet differs from v10.1 for the same plan entry. Step 1 alone
keeps the entry RAM identical to v10.1 in 154/155 flights. The headline comparison therefore treats series as
independent, exactly like nosty3's comparison to the original.

Game speed is not affected: the energy routine (`$A5E2` in the fixed bank) runs about 25 times per second in
both the original (24.96/s) and up38 (24.53/s), while images per second go from 6.1 to 9.9. Game logic runs on a
25 Hz tick (every second VBI, see the counter at `$004B`), rendering is decoupled from it.

## 2. Build

Requirements: Python 3.11+, `py65` (`pip install py65`), MADS (Mad-Assembler, `mads.exe`), a clone of
nosty3's repo (base ROM and his sources `src/v10_plotter.asm`, `src/fill_rows.asm`), and for emulator work
the AltirraBridge server + Python SDK (fork github.com/ilmenit/AltirraSDL, tested build fed7854).

Paths are set in one place, `tools/paths.py`, overridable by environment variables:
`FRACTALUS_WORK` (work dir: builds, captured scenes, results; default `<package>/work`),
`FRACTALUS_NOSTY` (nosty3 clone; default `<WORK>/repo`), `FRACTALUS_MADS` (default `<WORK>/mads/mads.exe`),
`ALTIRRA_BRIDGE` (dir with `AltirraBridgeServer.exe` and `sdk/python`).

```
python tools/build.py --name=final wait_beam sky vbi_sound_idle vbi_gauge proj_loop
```
produces `<WORK>/build/final.rom` and `final.car` (CART type 14, XEGS 128 KB). It asserts the SHA256 of the
v10.1 base ROM (`afa04d68...`) and the expected original bytes at every patched address.
Expected output: `final.car` SHA256 `ddb7466af76da9495bb59cb5b095d1ddc8cd52ac37a4fbdebed644dbb517d25f`,
`final.rom` SHA256 `6087e9b314368b95e7885f5634c88a506bbc61d7a4c988db345e7373377253da`.
`bin/up38_from_v10.1.ips` is the same change as an IPS patch on the raw v10.1 ROM.

Generated sources (do not edit by hand, edit the generator): `src/raster5.asm`, `src/raster5c.asm`
(`tools/gen_raster.py`, reads nosty3 `src/v10_plotter.asm`), `src/sky_b6.asm`, `src/sky_b8.asm`, `src/sky_b9.asm`
(`tools/gen_sky.py` + `tools/skylib.py`, reads nosty3 `src/fill_rows.asm`), `src/fable_*.asm`
(`tools/gen_fable.py`, called from `tools/patches_fable.py`), `src/clear_b6.asm`, `src/clear_b8.asm`
(`tools/gen_clear.py`, used only by the alternative `clear_beam` patch, not in up38).

## 3. Machine facts you need (all verified in v10.1)

- XEGS 128 KB: write to `$D5xx` selects the 8 KB bank at `$8000-$9FFF`; bank 15 fixed at `$A000-$BFFF`.
  After `sta $D500` the next opcode is fetched from the new bank at the same address. Cross-bank calls rely on
  this ("landing" code at the same address in the target bank).
- Banks 0 and 1 are copied at boot to RAM `$4000-$7FFF` (resident code, self-modifying in places).
  Bank 7 is a stale copy of the fixed bank and is never selected.
- nosty3's VBI guard (`$BFDA`/`$BFEA`) saves the current bank via a marker byte at `$9FFF` of every bank.
  Any new bank you use needs its marker (`$9FFF` = bank number); banks 2 and 4 have `$FF` (restored as bank 2).
- Flight loop `$A32E`/`$A36C`: `jsr $8309` (scene/geometry), `ldx #$33 / jsr $9214` (clear), `ldx #$30 /
  jsr $87D3` (render), `ldx #$33 / jsr $9308` (fill), `$8E51` objects, publish image in `$42`. VBI `$B4F4`
  flips the display list and clears `$42`. `$B516` = image counted (benchmark breakpoint).
- Frame buffers: rows at `$1010 + 96*r`, buffer A at column offset 3 (bytes 3..44), buffer B at 51.
  Row 0 is hidden, the display list shows from `$1070`. Sky = `$55` (colour 1), terrain body 0, ridge colour 2.
- Rasteriser (`$982A` in bank 5): fractal midpoint subdivision with a software stack. L = `$82/$84/$86`,
  stacks `sx=$95+y`, `sh=$EA+y`, `sp=$F4+y`. Occlusion table `$260E+x`: plot only when h > occ, clamp at `$97`.
  Row tables `$28CA/$28FA`. Column table `$3900,X` (buffer offset, rewritten every image by the `$87D3`
  prolog). Mask table `$3800,X`.
- Fill (`$9308`, bank 9): per column find first non-zero row r0, write `$55` to rows 1..r0-1, then propagate
  colours via tables `$3A00/$3B00`.
- Object pixel routine `$8B80` (bank 2 in v10.1) has a **second entry at `$8B88`** without the occlusion test,
  called from `$8FAC` and `$8FF4`. Lasers and objects are drawn after the fill.
- Free RAM proven by poisoning tests: page 1 `$0100-$017F` (game never writes there, stack never goes below
  `$01E3`). NOT free: the `$29FD` region (intro) and `$2F74` region (initialised to `$88`).
- PMG at `$0800` (PMBASE `$08`), fonts at `$0400`/`$3C00`. PMG players cover the terrain area (cockpit struts),
  so PMG DMA cannot be reduced.

## 4. The changes, in build order

Gains are from `results/ladder155.jsonl`: each rung is a ROM that adds one change, measured on the same 155 PAL
starts with the full protocol.

| Step | Patch name | FPS | Step gain | vs original |
|---|---|---:|---:|---:|
| base | v10.1 | 7.6359 | | +18.53% |
| 1 | `wait_beam` | 7.7949 | +2.08% | +21.00% |
| 2 | `raster_cull` | 8.1082 | +4.02% | +25.86% |
| 3 | `vbi_sound_idle` + `vbi_gauge` | 8.1728 | +0.80% | +26.86% |
| 4 | `sky` (replaces `raster_cull`, includes its culling) | 8.5400 | +4.49% | +32.57% |
| 5 | `proj_loop` | 8.9366 | +4.64% | +38.72% |

The render pipeline (clear + rasterise + fill) uses 13% fewer CPU cycles than v10.1 (simulator, captured scenes).

### Step 1. `wait_beam` - start clearing as soon as the beam has passed the mountains
`src/wait_beam.asm`, bank 2 `$9FD5`; `$9214` becomes `jmp $9FD5` (was `jmp $84A0`, nosty3's buffer sync).
The old buffer may be overwritten when VBI already flipped (`$42 = 0`) **or** when in this frame the beam is
below the last mountain row (VCOUNT 74..123): ANTIC no longer reads the old buffer and the next VBI is
guaranteed to flip. Mode `$4A = 0` bypasses the wait. Same contract as v10.1: A, X, Y, flags and SP preserved,
continues at `$982F`.

### Step 2. `raster_cull` - skip hidden subtrees of the fractal
`tools/gen_raster.py` builds bank 5 from nosty3's `src/v10_plotter.asm`. At subdivision widths >= 6
(depths d0..d4) a subtree is skipped when for every column x..sx-1 `occ[x] >= Hmax`, with
`Hmax = min(255, max(h_L, h_R) + E(w))` and nosty3's bound `E(w) = w//4 + 1 + max(E(w//2), E((w+1)//2))`.
After a skip the state equals "subtree processed": X = sx, `$84 = h_R`, `$86 = phase_R`, depth - 1.
Two-stage test: quick check of the first column inside the loop (`occ[x] < h_L` means visible, catches most
failed attempts), the full test out of line scanning columns in groups of 4. nosty3's d5..d7 specialisations
(0.08% of time, 1.8 KB) were removed to make room; d4 falls through to the generic `dg` path.

### Step 3. Shorter VBI
`src/vbi_sound_idle.asm`, `src/vbi_sound_exit.asm`, `tools/patches_vbi.py`. Bank 14 `$9801..`, bank 2
`$9885-$988E`, fixed bank `$B91C` (sound) and `$A852` (gauge).
- Sound: the original loop checks every channel Y = 14..1 (28 cycles per idle channel). Unrolled test of
  `$06DB+k | $06A3+k` (10 cycles per channel); at the first active channel it jumps back into the original loop
  at `$B92B` with the same Y, so everything after is original code.
- Cockpit gauge (`$A83E`, path `$A852` when the new value differs from `$062B`): the 8-segment loop is unrolled
  with constant addresses and characters; final variable state equals the original loop's
  (`$BB/$BC = $3364`, `$BD = $BE = $FF`, `$BF = Y`, `$C0 = 0`, `$062B = Y`, X = 0).

### Step 4. `sky` - the sky is never cleared
`tools/gen_sky.py`, `tools/skylib.py`, `tools/gen_raster.py`; banks 5, 6, 8, 9; bank 2 `$8B80-$8BAD`.
Idea: v10.1 clears the whole buffer every image and the fill repaints the sky. up38 remembers, per byte column,
where clean sky ends, clears only from there down, and repaints sky only in the band that changed.

RAM (page 1):
- `$0100+y`: `HD[y] = 152 - D[y]` for byte column y (3..44 buffer A, 51..92 buffer B; other y = `$FF`).
  D = first row from which the column is zero. Rows 1..D-1 are sky `$55`, row 0 is 0.
- `$0160-$0165` scratch, `$0166` saved A for entry 2, `$0167` = 1 while rendering (clear .. start of fill),
  `$0168`/`$0169` validity of buffer A/B (`$A5` = consistent), `$0170/$0171` indirect jump pointer.

Mechanics:
- Clear (banks 6 and 8, entry `$9863`): if mode `$4A` is not 2 or the buffer flag is not `$A5`, full clear and
  HD = 151 for all columns. Otherwise per column a chain of `sta row,x` stores is entered at the row given by
  HD (43 stores + `jmp`, chains at `$8000` and `$8C50+`), then the flag is cleared and `$0167` set.
- Rasteriser (bank 5): every plot site checks the pixel row against `HD` (`cmp $0100,y`); a pixel above the
  boundary calls the lazy routine that zeroes the column from the old boundary down to that row (descending
  chain entered through `$0170`) and moves the boundary up. 40 plot sites patched (variants for width-2 blocks).
- Fill (bank 9, from nosty3's `fill_rows.asm`): scans from D instead of row 1, writes `$55` only in the band
  `[D, r0)`, then sets `HD = 152 - min(r0, 44)` and the buffer flag (`$0168`/`$0169`) when `$4A = 2`.
- Objects: the pixel routine moved from bank 2 `$8B80` to bank 8 (both entries, `$8B80` and `$8B88`, kept with
  three landings that reproduce A and flags exactly). Pixels drawn after the fill only lower the boundary.
Cost: the per-pixel check (about 9 cycles x ~258 plots per image) is the main overhead of this step.

### Step 5. `proj_loop` - projection and division without calls (agent Fable, under our coordination)
`tools/gen_fable.py` (writes `src/fable_proj3.asm`, `src/fable_loop2.asm`, `src/fable_stub2.asm`),
`tools/patches_fable.py`, `src/fable_pro14.asm`, `src/fable_epi2.asm`.
- Bank 3: grid point projection with both divisions inlined (8 steps of `Q = floor(256*R/D)`, no jsr/pha/pla,
  failed rare step undone). Bank 3 now has marker `$9FFF = 3`.
- Bank 2 `$85D4-$87D2` (old projection, the division at `$8224-$8303` is free too): new edge loop, fast clipping
  path with the original algorithm as fallback, copies, final scan; `$885E: jmp $85D4`; stubs `$984C-$9856`
  (`$984F: lda #3 / sta $D500` enters projection, return lands on a `$60` byte in bank 2, alignment chosen by
  `patches_fable.py`).
- Bank 14 `$9950-$9D87`: unrolled `$87D3` render prolog. Bank 2 `$89A1`: epilogue unrolled 4x.

### Not in up38 but in the sources
`clear_beam` (`tools/gen_clear.py`, banks 6/8): clearing row by row racing the beam, +0.5% over step 1, replaced
by `sky`. `raster5c.asm` is step 2 alone (no lazy sky checks).

## 5. How correctness was checked

The rule from nosty3's work is kept: same image, byte for byte.
- `tools/equiv.py REF.rom CAND.rom SCENES...`: runs the pipeline (from the `ldx` before `jsr $9214` to after the
  fill) of two ROMs in the py65 simulator (`tools/fxsim.py`) from the same captured state and compares all RAM
  `$0000-$7FFF`, both frame buffers included. up38: 0 differences on 800 scenes (460 captured from step 4, 340
  from the final build). Ignored bytes: the rasteriser's software stack in zero page
  (`$82 $84 $86 $96-$9E $EB-$F3 $F5-$FD`), proven dead after the pipeline by `tools/liveness.py` (no read
  before write by the rest of the loop) and `tools/vbi_reads.py` (VBI does not read them).
  Scenes must be captured from the candidate build itself (`tools/capture.py`, `tools/capture_loop.py`),
  because step 4 keeps state between images.
- `tools/hang.py`: 20 flights with random steering and firing, no hang. All 310 benchmark flights ended normally.
- `tools/poison.py`: free-RAM test (two identical runs, one with random bytes poured into a region).
- `tools/tearcheck.py`: tearing test (used for `clear_beam`).
- `tools/fullbench.py`, `tools/fullreport.py`, `tools/ladderbench.py`: the measurement protocol, summary with
  bootstrap and t intervals, per-flight match with nosty3's published results.
- Scenes are not in the package (229 MB); capture them with the tools above.

## 6. Pitfalls we hit (check these before changing anything)

1. `$8B88` is a second entry into the object pixel routine. Moving `$8B80` without it hangs the game.
2. Every bank you add code to needs its `$9FFF` marker, or an interrupted bank switch restores the wrong bank.
3. After `sta $D500` execution continues in the other bank at the next address: keep landing bytes in place.
4. Step 4 depends on `$0167-$0169`: anything that draws into the buffers outside the pipeline must lower HD
   or invalidate the buffer flag.
5. Branch range errors in generated code: rare paths are placed after `jmp cull_entry` and reached by
   `jmp` pairs; the generators assert sizes (`ert`) per region.
6. The Altirra profiler misattributes banked code; use the simulator (`tools/simprof.py`, `tools/loopprof.py`)
   for cycle profiles.
7. `$7FFE` in resident code is `jmp $BCA4` whose high operand byte is the first byte of bank 2 (`$BC`): it only
   works with bank 2 selected (already in the original).
8. Bank 4 `$8887` does `DEC $90E8,X` on ROM (no effect on the cartridge); only the intro uses it.

## 7. The .xex for extended memory (320K Rambo, 576K, 1088K)

`bin/fractalus_up38_320k-1mb.xex`, built by `tools/mkxex.py` from `final.rom`, the instruction map
`work/cov/all.json` and the decisions in `xex/decisions.json`. Same speed as the cartridge
(155 PAL flights: 8.919 vs 8.937 FPS, difference within noise).

Layout: resident code moves to `$8000-$BFFF` (plain RAM, BASIC off); each window bank goes to `$4000-$5FFF` of its
own PORTB bank with a copy of the fixed bank at `$6000-$7FFF`. Addresses map as `a ^ $C000` for `$4000-$BFFF`,
low bytes unchanged, so page crossings and cycle counts stay the same. Bank n uses PORTB
`$83 | (n & 3) << 2 | (n >> 2) << 5` (bits 2, 3, 5, 6). The loader checks that 16 PORTB values give 16 distinct
banks and otherwise prints "FRACTALUS UP38 NEEDS 320K RAMBO, 576K OR 1MB RAM".
The intro runs once in the cartridge layout (its decompressor writes `$3600-$6BFF` straight across `$4000`):
bank 15 and bank 4 sit in main RAM, its four bank switches copy 8 KB from PORTB bank 7, and at `$A155` the code
switches to the relocated layout.

Relocation is binary (no full source exists). Instruction map: profiler coverage of many sessions
(`tools/covmap.py`, needs a bridge with the PROFILE_DUMP cap raised above 4096) plus static extension
(`reloc.extend`). Absolute operands are moved mechanically; everything else is a decision in
`xex/decisions.json`: address high bytes in immediates (`hi`), bank numbers (`bank`), word tables (`wordtab`),
high-byte tables (`hitab`), raw patches (`patch`). `tools/autodec.py` generates the heuristic part, the
`manual` part was found one by one.

Verification: `tools/xexrun.py` runs two 6502 simulators in lockstep (`tools/xexsim.py`): A = cartridge, B =
relocated, from the state right after the resident copy, with VCOUNT/RANDOM from cycles, VBI every frame and
ANTIC walking the display list line by line for DLIs. After every instruction PC_B must equal M(PC_A), every
write must go to the mapped address with an equal (or mapped) value, hardware writes must be equal.
60 million instructions (over 5000 frames, over 30000 DLIs) on two seeds without a difference.
`tools/xexcheck.py` plays the .xex in Altirra and stops at the first PC outside the instruction map.
Not covered dynamically: rare scenes (landing, pilot rescue, alien, game over); there only static analysis.

## 8. Ideas not done

- Sky step: the per-pixel boundary check is the main remaining overhead; a margin under the boundary or
  checking per subtree instead of per pixel could remove most of it.
- The `$87D3` prolog rewrites the `$3900` column table every image (about 1.3k cycles).
- Division by tables at `$8224` was analysed and does not win against the inlined shift-subtract.
- In the .xex (all code in RAM) self-modifying code becomes possible in the hot loops (for example `sta abs,y` with
  a patched high byte instead of `sta (zp),y`), a larger PORTB window allows fewer bank switches. Not measured.

## 9. Package map

- `bin/` cartridge (`.car`, `.rom`), `.xex`, IPS patch from v10.1.
- `src/` all assembler sources (MADS, `opt h-`, `org` = CPU address).
- `tools/` build, generators, simulator, verification and measurement tools (one-line description at the top of
  each file, most comments in Polish).
- `xex/decisions.json` relocation decisions for the .xex.
- `work/` starting content of the work dir: `cov/all.json` (instruction map), `xex/run.*`, `xex/post.*`
  (machine states for `xexrun.py`).
- `results/` raw measurements and summaries. `report/` offline copy of the results page.
- `docs/worklog_pl.md` our working log (Polish).
