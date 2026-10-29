# v13 sound and geometry banking repair

Updated in place on 2026-10-29. The version remains **v13**, and all existing CAR/ROM/XEX download names are retained. IPS patches, build manifests and expected hashes were regenerated. The geometry experiment is not part of this update.

## Cause and repair

The compiled-tree fallback installed `STA $D500` at bank 2 `$9E50`, overwriting three bytes of the existing mixer helper:

```asm
; Correct mixer code
$9E4E CMP $0716
$9E51 BCS $9E5E
```

The overwrite changed the comparison to `CMP $8D16` and the branch to `BRK`. It becomes executable when virtual channel 11 is occupied (`$0710 != 0`), disrupting sound-channel selection and pilot audio.

An initial unpublished repair restored the mixer but placed the fallback trampoline at `$9875`, overwriting live geometry dispatch. A turn crash was reproduced in Altirra on 130XE PAL with 1088 KB RAM. Actual CPU history showed `$835E -> $9863 -> $9867 BEQ $9876 -> BRK`, followed by execution of ROM padding and zero-page memory. That candidate was rejected.

The corrected v13 preserves both the mixer and geometry. Fallback now switches banks at **bank 2 `$9FEF`**, then executes its continuation at **bank 5 `$9FF2`**. The generator checks both destinations for unused padding and guards the mixer and geometry regions. XEX applies equivalent relocation and PORTB switching. Each repaired ROM differs from the initial published v13 by 14 bytes; compiled terrain workers are unchanged.

## Validation

- Full source rebuild with MADS: both ROM/CAR pairs, the XEX and both IPS patches match the repaired distribution byte-for-byte.
- Fixture-free `scripts/test_v13_sound_fix.py`: all 256 dispatcher inputs and 1024 randomized mixer cases per CAR, compared with the original game's mixer, plus the occupied-channel-11 regression.
- Its `--native` mode passed four unchanged-map cold boots: both CAR sizes, PAL/NTSC, 130XE with 1088 KB RAM, sustained turns and real clock/render-presentation checks.
- Earlier repaired-image validation covered 16 additional cold boots of these two CAR variants: PAL/NTSC, 64/1088 KB, two menu delays, at least 2738 flight frames per case, repeated 400-frame turns and pause/resume.
- Two additional CAR tests used S, B and PLUS with channel 11 allocated, followed by sustained turns. Two extended XEX tests covered PAL/NTSC, steering/fire, repeated turns, completed images and pause/resume.
- CPU-model replay additionally checked 4096 mixer inputs, 320 captured VBI inputs, eight queued-tone inputs and 40 render pipelines per ROM. Renderer RAM, registers and CPU cycles matched before/after repair; these captured fixtures are not required by the public regression script or rebuild.
- The user confirmed the corrected 1 MB CAR works in their emulator.

Native checks verify elapsed machine ticks, actual direction changes and completed image presentations. A successful FRAME response or a flight-mode flag alone is insufficient: the flag can remain set after a crash.

[Current validation records](../../results/v13/validation/sound-fix/) · [Rebuild](../REBUILD.md)

No new FPS benchmark was run. Existing tables, plots and raw measurements describe the images before this banking repair. No new numerical FPS claim is made for the replacement binaries. A complete controlled comparison of beep intervals against actual pilot distance has not been performed; mixer/POKEY regression and functional tests establish the scopes described above, not every gameplay state or physical-hardware compatibility.
