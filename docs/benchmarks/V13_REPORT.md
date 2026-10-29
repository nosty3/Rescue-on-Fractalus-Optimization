# Full v13 measurements

**FPS status:** the table and chart retain measurements made before the 2026-10-29 banking repair. The repaired images have not undergone a new full FPS series.

The 50/50 result is half of the straight-flight mean and half of the descent mean. Each v13 variant: 155 PAL cold boots and 155 NTSC, with 78 straight and 77 descent, nominally 60 s. Total: 620 new flights in four isolated emulators. Same plan as v12; all initial maps match. Original retains the full historical 155+155 reference per system. Natural early ends remain in the data. FPS measures CAR; XEX passed separate functional validation.

| System | Variant | FPS | Gain over original | Gain over v11 |
|---|---|---:|---:|---:|
| PAL | 512 KB | **9.2791** | **+47.95%** | **+5.65%** |
| PAL | 1 MB | **9.3856** | **+49.65%** | **+6.86%** |
| NTSC | 512 KB | **8.4698** | **+51.48%** | **+5.83%** |
| NTSC | 1 MB | **8.5354** | **+52.65%** | **+6.65%** |

### PAL

Original: 6.271731 FPS; v11: 8.782928 FPS.

- 512 KB: 9.279064 FPS, 95% [9.197611, 9.360884]; v11 +5.6489%; early ends 9/155.
- 1 MB: 9.385565 FPS, 95% [9.311797, 9.459674]; v11 +6.8615%; early ends 7/155.

### NTSC

Original: 5.591516 FPS; v11: 8.003108 FPS.

- 512 KB: 8.469807 FPS, 95% [8.399788, 8.540815]; v11 +5.8315%; early ends 8/155.
- 1 MB: 8.535392 FPS, 95% [8.463765, 8.607318]; v11 +6.6510%; early ends 5/155.

20,000 bootstrap replicates, seed 2026102913. Shared start indices retain pairing between both v13 variants; resample within 78/77 groups. Preserve dependence with original descent; independently resample historical original straight. No outlier rejection or state transfer. All initial map hashes match. The v11 reference uses the full historical series of 155 straight and 155 descent flights per system. Gain over v11 is a ratio of 50/50 means; no confidence interval is reported for that ratio. The study describes two automatic scenarios, not every gameplay situation.

512 KB: 39.12 min wall time; series concurrent, two workers each.
1 MB: 39.17 min wall time; series concurrent, two workers each.

[Data](../../results/v13/) · [Method](METHOD.md) · [Validation](../../results/v13/validation/)

Validation: 80 scenes per variant, 1500 randomized segments, 24 short v12/v13 control flights with pause, turns and firing. XEX: PAL/NTSC, 4 controlled level transitions, 160 relocation comparisons, 58 VBI banks and rejection on 320/576 KB. Emulator and CPU-model tests, not hardware certification.
