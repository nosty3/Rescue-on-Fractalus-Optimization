# v13 compiled subdivision trees

Ilmenit's generator precomputes midpoint-X positions and traversal order for a known segment width. Height perturbations, seeds, rounding, clipping and pixel resolution remain exact. Unsupported widths use the exact v12 fallback. Left clipping has separate workers because its rounding differs.

512 KB has 46 specializations in 47 extra 8 KB banks; 1 MB has 86 in 111 banks. The nested selections come from an independent earlier 40-scene profile, not the full v13 measurement. This is a heuristic, not proof of an optimal bank allocation.

Dispatch runs once per segment: tables in unused old bank-2 fill space, selector at $9C42, entry through $9858, fallback through $9E50. Fable's projection at $984F is preserved. Larger workers span banks with A/P preserved. Every accepted pixel respects the v12 HD/lazy-clear cache; helpers and row tables are local to each chunk. Buffer synchronization and beam-aware waiting remain.

The generator's `source()` body is unchanged from ilmenit's AI-assisted package; project-root handling and import-time directory creation were adapted. Astra prepared integration with v12 and the extended XEX. See `src/v13/provenance.json`.

## 512 KB XEX

62 extended 16 KB pages hold an 8 KB bank plus an 8 KB fixed-code copy. Requires a 1 MB expansion, 1088 KB total. PB1/2/3/5/6/7 select pages; PB0 keeps the OS enabled. BASIC and self-test are disabled before banking; the compatible expansion latches their control state. The loader checks 64 distinct pages.

Some valid new PORTB values are below $80. The VBI guard therefore accepts every nonzero marker; zero falls back to bank 2. Nine-byte Esc stack handling and both fixed music pointers are retained. PAL/NTSC boot/control/pause, four controlled level transitions, 160 CAR/XEX comparisons, all 58 VBI banks and rejection at 320/576 KB passed.

The 1 MB cartridge would need 126 pages with this layout, beyond its 64-page limit. Its XEX needs a separate packing/mapping design; this is not a proof of general impossibility. Both cartridges themselves require only 64 KB RAM.
