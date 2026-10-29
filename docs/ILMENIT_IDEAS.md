# Ilmenit ideas — implementation status

FPS gains describe complete builds; they are not attributed independently to each small change. Ilmenit's original package started from our v10.1, not v11.

| Idea | Status / version | Gain or decision reason |
|---|---|---|
| Width-specific compiled subdivision trees | **v13: 512 KB and 1 MB** | Removes midpoint-X arithmetic and tree traversal; exact fallback. FPS: table below. |
| Selective occlusion tests inside trees | **v13** | Part of the same integration; full pipeline on 40 held-out scenes uses 5.48% / 6.59% fewer cycles than v12. These are not FPS percentages. |
| Exact `$AA` fill shortcut | **v12** | Hit: about 3405 → 917 fill cycles; no isolated full FPS study of this shortcut. |
| Further Y bookkeeping removal | Partly v11, extended in **v12** | d0–d4 without redundant operations, Y=5 before fallback; part of the combined v12 gain. |
| Grouped geometry classification 33–44 | **v12** | Average 176.69 fewer geometry-preparation cycles; no separate full FPS estimate. |
| Empty-view / sky-reuse adaptation | **Tested adaptation excluded** | Our variant added about 0.154% renderer cost. Removed; this does not assess every cache in the package. |
| Banked division tree | **Not ported** | About 16 cycles of headroom over Fable inline, versus about 33 for a simple wrapper; a future inline variant remains a possibility. |
| GTIA / GR.10 | **Outside this GR.7 line** | Changes graphics and sampling; not a visually transparent GR.7 optimization. |
| Earlier PMG, sound, interpolation, geometry, clipping | Already in our **≤v10.1/v11** base | Inherited from our project; not counted as new work or another gain. |

| System | Variant | FPS | Gain over original | Gain over v12 |
|---|---|---:|---:|---:|
| PAL | 512 KB | **9.2791** | **+47.95%** | **+3.87%** |
| PAL | 1 MB | **9.3856** | **+49.65%** | **+5.07%** |
| NTSC | 512 KB | **8.4698** | **+51.48%** | **+3.93%** |
| NTSC | 1 MB | **8.5354** | **+52.65%** | **+4.73%** |

The complete v12 package added +1.71% PAL and +1.83% NTSC over the full v11 reference, including Astra's scan improvements. These are not separate gains for each table row. The initial 17.87% described isolated segments versus v11, without full cache integration or an FPS measurement. It is not added to or multiplied by final results.

512 KB also has an XEX for 1 MB RAM. The 1 MB CAR layout would need 126 pages of 16 KB while this loader supports 64; its XEX is therefore not supplied. Both cartridges require only 64 KB RAM.

[Full measurements](benchmarks/V13_REPORT.md) · [Technical description](terrain/COMPILED_TREES.md)
