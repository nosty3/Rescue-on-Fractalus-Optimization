Historical research document. Old paths and results refer to the experiment described; the current implementation is documented in docs/OPTIMIZATIONS.md and aggregate results in docs/benchmarks/METHOD.md (paths from the repository root).

[English](PMG_AUDIT.md) · [Polski](PMG_AUDIT_PL.md)

# Audit of PMG routines in v8

2026-10-21. Study of code, write counts, and loop organization. No game changes, new release, or estimate of FPS impact.

v8 ROM: `02da0221c95fc8896720a7ca17181bbb1c3c7502dadf62d933d1ba0c341347bd`.

## Scope and method

Inspected fixed-bank ROM code and RAM code from a retained flight state. Selected ROM routines are byte-identical to the original. Listing from known entry points: `PMG_ROUTINES.txt`. Complete linear disassembly is only a search aid: it may show apparent instructions in data tables and does not prove code use.

In the v8 emulator, collected 8 actual entries each to $A527, $A55C, $A94D, and $A8DE. Inputs were replayed in a CPU model, counting stores and instructions. These are input samples, not a frequency profile or whole-game timing measurement. $A71E was also reached in retained higher-level states, but with argument $7F and an empty previous drawing. Active $710D was not reached in the examined windows; it was checked statically and on a controlled synthetic input. No full test of all animations, pilot-rescue phases, or alien encounters is claimed.

Results: `live-input-observations.json`, `special-paths.json`, `cpu-observations.json`. Cycles in the last file are CPU cycles without DMA or interrupts. Replaying hardware registers as fixed values does not exactly reproduce POKEY RANDOM. Raw memory states are local material.

## Memory map and schedule

The emulator confirmed PMBASE=$08 and DMACTL=$3F. Missile memory is at $0B00–$0BFF, and players P0/P1/P2/P3 at $0C00/$0D00/$0E00/$0F00. In this mode, $0800–$0AFF should not automatically be treated as PMG image memory: the game also stores other systems' data there.

PMG also handles the cockpit, not just objects against the mountains. The game reuses the same players at different screen heights, changing GTIA registers in DLI. Position, width, and color stores at $AE96..$AF41 and in VBI are not simply redundant repetition of constants. Removing them requires accounting for other screen regions and DLI timing.

$A527, $A55C, and $A94D are called in the VBI branch at $B68E..$B69A. Counter $0640 divides work between two branches, setting value 2 at $B5C0. Do not assume each renderer runs for every new terrain image, or that all run in every VBI.

## Routines and findings

| Address | Operation | Assessment |
|---|---|---|
| $A527–$A55A | Select pattern and write 21 P2 rows plus two edge bytes | Compares $291C/$291D with retained $2872/$2874. No changes means zero stores. Fixed 21-iteration loop with DEC $BD counter. |
| $A55C–$A57B | P0 bar at $0C97–$0CCF | Skips unchanged values, but every change causes 57 stores: clear one part and fill the other with $FF. Most obvious redundant work. |
| $A57C–$A5A6 | Two-row M3 marker | Only on change. Two AND #$3F and two ORA #$C0 operations. Preserves other missiles' bits. Already unrolled. |
| $A632/$A65B/$A65F | P1 bar, range starting at $0D98 | Updates the boundary with one store; does not rewrite the entire bar. No basis for the same criticism as $A55C. |
| $A71E–$A83D | P3 object, regions $0F1E+X and $0F71+X | Retains start $286F and length $2835. Clears the previous range, selects shape, clips both regions. Rows use mask $2826 or a RANDOM read. |
| $A8DE–$A93D | Five-row P3 object/marker at $0F98+Y | Skips unchanged position. On change, clears 5 bytes and, if active, draws 5 new ones; three pattern variants. |
| $A94D–$A993 | Three-row M2 marker | Compares old/new position. Clears 3 bytes with AND #$CF and sets 3 with ORA #$30, preserving other missiles. |
| $710D–$7269, RAM | P2 object: clearing, position, pattern, row repetition | Clears only previous length $2866 from position $2865. Clearing uses DEC $BD; vertical row repetition uses DEC $BE. Scale and animation-phase selection must not be skipped. |
| $4FC2–$5013, RAM | Shift four planes P0–P3 by one row and add a new row | 89 iterations, each copying 4 bytes, followed by 4 new bytes. 356 shift stores + 4 new-row stores. Path controlled by $89 and dispatcher $B7EE; its cost was not assigned to normal flight. |
| $AA65–$AA7C | Initialize three 8-byte ranges | Copies fixed tables to P0, P1, and missiles. Not the main flight loop. |

Initialization at $A02A sets up $0B00–$0FFF and uses general memory fill $A0A1. This is 1280 bytes; the routine updates a 16-bit pointer and counter for every byte. Specialization is possible, but this is initialization, not clearing all PMG memory each frame. Additional loops $443F, $45A0/$45BB, $4D52, $4EE6, $5018, $588E, $58B3, $58CE, and $A3FD/$A405 handle screen preparation/transitions and selected PMG ranges. They were not automatically counted as recurring flight cost.

## Specific opportunities, without implementation or FPS prediction

### 1. Differential update of bar $A55C

With a valid previous image, moving 20→21 or 21→20 changes exactly one byte, but the original makes 57 stores. Execution of the original code confirmed that 56 stores rewrite the same value. Only the interval between old and new boundaries needs writing: |d| bytes instead of 57 for a change of d steps. No change already means no writes.

Condition: old value $2875 must match actual PMG contents. Initialization, restart, and screen transitions must establish this condition or force a one-time full redraw. Replacing the loop without analyzing other writers to the region is insufficient.

### 2. Unroll short fixed-length loops

Clearest candidates: 21-row copy $A54A, five-row clearing/copying $A8EA/$A91E, and the two three-row loops $A965/$A975. Some counters and branches can be removed while preserving masks and final registers, flags, and scratch memory. At $A91E, the counter is in ZP ($BB) even though the size is always 5. This is a concrete low-level simplification independent of game-logic changes.

### 3. Counters and specialization of RAM renderer $710D

Clear loop $7119: STA abs,Y / INY / DEC zp / BNE. DEC zp costs more than decrementing a register. However, X is a live argument not saved until $712A, so using X requires earlier saving and correct restoration. This is not an unconditional instruction substitution. Unrolling clearing blocks reduces branches.

Loop $71D5 checks X<$56 on every repetition of the same row and counts down $BE. Separate paths for the screen interior, edge, and common small repeat factors could be considered. It must also preserve the fact that X stops increasing at the boundary.

Because the code is in RAM, self-modifying address/end-of-loop operands are possible. Setup has a cost; there is no basis for assuming SMC is always better. The routine runs in interrupt context, so DLI and shared operands must remain safe.

### 4. Separate P3 object paths at $A71E

Drawing loop $A7F3 reads and tests $2826 each time. Separate fixed-mask and RANDOM paths could reduce this selection overhead. The RANDOM path must retain a hardware read for every row. Faster execution changes RANDOM read timing, so preserving the number of reads alone does not produce an identical random sequence to the original.

Clearing at $A77B checks Y<$4F each iteration. The range could be split before/after that threshold. Drawing also has several X thresholds ($14/$2E/$4F/$73). Specialization must preserve exact source-data consumption, terminators, and indices; removing all checks for one example is insufficient.

### 5. PMG scrolling in RAM at $4FC4

Code is already unrolled across four channels but shares an 89-row loop. Partial/full unrolling could reduce INY/CPY/BNE and use fixed addresses instead of abs,Y. Being in RAM does not require SMC: these shift addresses are fixed. Full unrolling needs much more space and a separate decision about code placement.

The copy overlaps and proceeds from lower to higher addresses, with the source one byte higher. Do not reverse its direction. The new row is generated from RANDOM, so its semantics remain a separate condition.

## Conclusions

PMG was not implemented naively throughout the game: previous-range tracking, unchanged-data skipping, and small boundary updates already exist. The clearest confirmed redundant work is full redrawing of bar $A55C. The most straightforward assembly-level opportunities are the fixed 3/5/21-row loops and the RAM renderer's counters and row repetition.

No ROM was changed, no release generated, and no FPS impact estimated. Nor was every option shown to pay off after integration overhead. If pursued, the next stage should begin with memory contracts and comparison tests, not automatic implementation of every proposal.
