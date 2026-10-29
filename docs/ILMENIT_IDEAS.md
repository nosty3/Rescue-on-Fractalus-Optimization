# Ilmenit ideas — implementation status

The FPS table shows the cumulative effect of changes implemented in v12 and v13, compared only with the original and v11. The total gain is not attributed independently to each small change. Ilmenit's original package started from our v10.1, not v11.

| Idea | Status / version | Effect or decision reason |
|---|---|---|
| Width-specific compiled subdivision trees | **v13: 512 KB and 1 MB** | Removes midpoint-X arithmetic and tree traversal; exact fallback. FPS: table below. |
| Selective occlusion tests inside trees | **v13** | Rejects hidden fragments before drawing; included in the combined v13 result. |
| Exact `$AA` fill shortcut | **v12** | Shortens repeated-pattern fill; no isolated full FPS study of this shortcut. |
| Further Y bookkeeping removal | Partly v11, extended in **v12** | d0–d4 without redundant operations, Y=5 before fallback; included in the combined result for each version. |
| Grouped geometry classification 33–44 | **v12** | Less geometry-preparation work; no isolated full FPS study of this change. |
| Empty-view / sky-reuse adaptation | **Tested adaptation excluded** | Our variant increased renderer cost and was removed; this does not assess every cache in the package. |
| Banked division tree | **Not ported** | A simple bank-switch wrapper consumes the expected saving over v11 inline code; a future inline variant remains a possibility. |
| GTIA / GR.10 | **Outside this GR.7 line** | Changes graphics and sampling; not a visually transparent GR.7 optimization. |
| Earlier PMG, sound, interpolation, geometry, clipping | Already in our **≤v10.1/v11** base | Inherited from our project; not counted as new work or another gain. |

| System | Version / cartridge | FPS | Gain over original | Gain over v11 |
|---|---|---:|---:|---:|
| PAL | v12 / 128 KB | **8.9329** | **+42.43%** | **+1.71%** |
| PAL | v13 / 512 KB | **9.2791** | **+47.95%** | **+5.65%** |
| PAL | v13 / 1 MB | **9.3856** | **+49.65%** | **+6.86%** |
| NTSC | v12 / 128 KB | **8.1499** | **+45.75%** | **+1.83%** |
| NTSC | v13 / 512 KB | **8.4698** | **+51.48%** | **+5.83%** |
| NTSC | v13 / 1 MB | **8.5354** | **+52.65%** | **+6.65%** |

References: PAL: original **6.2717 FPS**, v11 **8.7829 FPS**; NTSC: original **5.5915 FPS**, v11 **8.0031 FPS**.

FPS is the 50/50 weighted result for straight flight and descent. Original and v11: full historical series of 155 flights per scenario and video system; v12 and each v13 variant: 155 flights per video system, split into 78 straight and 77 descent. Gain = (version FPS / reference FPS − 1) × 100%, calculated from unrounded means. Percentages from individual stages are not added together.

512 KB also has an XEX for 1 MB RAM. The 1 MB CAR layout would need 126 pages of 16 KB while this loader supports 64; its XEX is therefore not supplied. Both cartridges require only 64 KB RAM.

[Full measurements](benchmarks/V13_REPORT.md) · [Technical description](terrain/COMPILED_TREES.md)
