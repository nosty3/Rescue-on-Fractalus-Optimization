# Full v13 measurements

The 50/50 result is half of the straight-flight mean and half of the descent mean. Each v13 variant: 155 PAL cold boots and 155 NTSC, with 78 straight and 77 descent, nominally 60 s. Total: 620 new flights in four isolated emulators. Same plan as v12; all initial maps match. Original retains the full historical 155+155 reference per system. Natural early ends remain in the data. FPS measures CAR; XEX passed separate functional validation.

| System | Variant | FPS | Gain over original | Gain over v12 |
|---|---|---:|---:|---:|
| PAL | 512 KB | **9.2791** | **+47.95%** | **+3.87%** |
| PAL | 1 MB | **9.3856** | **+49.65%** | **+5.07%** |
| NTSC | 512 KB | **8.4698** | **+51.48%** | **+3.93%** |
| NTSC | 1 MB | **8.5354** | **+52.65%** | **+4.73%** |

### PAL

Original: 6.271731 FPS; v12: 8.932929 FPS.

- 512 KB: 9.279064 FPS, 95% [9.197611, 9.360884]; v12 +3.8748%, 95% [+3.2950%, +4.4871%]; early ends 9/155.
- 1 MB: 9.385565 FPS, 95% [9.311797, 9.459674]; v12 +5.0670%, 95% [+4.5302%, +5.5941%]; early ends 7/155.

1 MB / 512 KB: +0.106501 FPS; +1.1478%, 95% [+0.4920%, +1.7715%].

### NTSC

Original: 5.591516 FPS; v12: 8.149851 FPS.

- 512 KB: 8.469807 FPS, 95% [8.399788, 8.540815]; v12 +3.9259%, 95% [+3.3758%, +4.4819%]; early ends 8/155.
- 1 MB: 8.535392 FPS, 95% [8.463765, 8.607318]; v12 +4.7306%, 95% [+4.2554%, +5.2194%]; early ends 5/155.

1 MB / 512 KB: +0.065585 FPS; +0.7743%, 95% [+0.2748%, +1.2909%].

20,000 bootstrap replicates, seed 2026102913. Shared start indices retain pairing between v12 and both v13 variants; resample within 78/77 groups. Preserve dependence with original descent; independently resample historical original straight. No outlier rejection or state transfer. All initial map hashes match. The study describes two automatic scenarios, not every gameplay situation.

512 KB: 39.12 min wall time; series concurrent, two workers each.
1 MB: 39.17 min wall time; series concurrent, two workers each.

[Data](../../results/v13/) · [Method](METHOD.md) · [Validation](../../results/v13/validation/)

Validation: 80 scenes per variant, 1500 randomized segments, 24 short v12/v13 control flights with pause, turns and firing. XEX: PAL/NTSC, 4 controlled level transitions, 160 relocation comparisons, 58 VBI banks and rejection on 320/576 KB. Emulator and CPU-model tests, not hardware certification.
