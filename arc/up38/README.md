> ARCHIVE: up38 is superseded by v11. This original XEX has a confirmed level-completion stall caused by unrelocated music pointers. Use the fixed v11 XEX in ../../optimized%20version/. The original authors' historical description follows.

# Rescue on Fractalus! up38

[English](README.md) · [Polski](README_PL.md)

up38 is a faster build of Rescue on Fractalus! for Atari XL/XE, made on top of **v10.1 by nosty3**
(github.com/nosty3/Rescue-on-Fractalus-Optimization). It draws the fractal mountains about 38% faster than
the original game in PAL and about 41% faster in NTSC. The picture is the same, byte for byte.

The work was done by Claude Opus 5.5 (Anthropic) with a small team of AI agents, for Solo. Thanks to nosty3:
his v10.1, his measurement method and his published results were the starting point and the ruler.

## Results

Measured with nosty3's own method: 155 automatic flights of 60 seconds per version and TV system, the same
start moments, the same emulator setup.

| System | Original | v10.1 (nosty3) | up38 | up38 vs original |
|---|---:|---:|---:|---:|
| PAL | 6.44 FPS | 7.64 FPS (+18.5%) | **8.94 FPS** | **+38.7%** |
| NTSC | 5.80 FPS | 6.94 FPS (+19.5%) | **8.17 FPS** | **+40.7%** |

FPS here means finished terrain images per second. Before measuring up38 we re-ran the original and v10.1:
all 620 of those flights came out identical to the numbers nosty3 published.

**Does the game get harder?** No. The game logic (energy, enemies, pilots) runs on its own 25 Hz timer, not on
the number of images. We measured the energy routine: about 25 calls per second in both the original and up38.
You see the same game, drawn more often.

## Files

- `bin/fractalus_up38.car` - the cartridge (XEGS 128 KB, CART type 14). Works in Altirra and on flash carts that
  load `.car` files (SIDE3, Ultimate Cart, AVG Cart, The!Cart).
- `bin/fractalus_up38.rom` - the same as a raw ROM (choose XEGS 128 KB).
- `bin/up38_from_v10.1.ips` - patch from nosty3's v10.1 ROM.
- `bin/fractalus_up38_320k-1mb.xex` - a version for Atari with extended memory (320K Rambo, 576K or 1 MB),
  for people who load files over SIO2SD or FujiNet. Same speed as the cartridge. On a machine without enough
  memory it shows a message instead of crashing. Rare game scenes (landing, pilot rescue, the alien, game over)
  were checked only by analysis so far: if anything breaks there, please report the scene.

## What changed, in plain words

1. **Clearing starts earlier.** The game waited for the next frame before clearing the hidden buffer. It now
   starts as soon as the TV beam has passed the mountains. (+2.1%)
2. **Hidden mountain parts are skipped.** Mountains are built by splitting lines again and again. If a whole
   branch of that splitting would end up behind mountains already drawn, it is skipped. (+4.0%)
3. **Shorter interrupt.** Sound channels that are silent are skipped quickly, the cockpit gauge is drawn without
   a loop. (+0.8%)
4. **The sky is never cleared.** Each column remembers where clean sky ends. Only the part below is cleared and
   only the band that changed gets repainted. (+4.5%)
5. **Projection without calls.** The 3D projection now does its divisions inline, with a faster edge loop.
   This step was done by the agent Fable. (+4.6%)

The detailed technical description, with addresses, is in `TECHNICAL_NOTES.md`.

## Rebuilding and continuing

Everything needed to rebuild up38 from v10.1 and to keep working on it is here: all assembler sources, the
generators, a 6502 simulator, the equality test that checks the image byte for byte, and the measurement tools
that reproduce nosty3's protocol. Start with `TECHNICAL_NOTES.md`, sections 2 and 5.

Tested in Altirra (emulation). Not tested on physical hardware by us.
