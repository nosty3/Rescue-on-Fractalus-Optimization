# v13 FPS methodology

Each cartridge variant has 155 independent PAL cold boots and 155 NTSC: 78 straight and 77 descent flights per system. Both variants run concurrently with two workers each, four isolated emulators total. Stock 800XL/64 KB, history disabled, unlimited host pacing. The same frozen start/scenario assignment as v12 is retained.

After 170 warmup video frames, count full B516 terrain-presentation intervals for a nominal 60 s window, using the Atari clock. Natural early ends remain. Descent is joystick up for 1 s followed by 3 s neutral. Cycle deadlines are exact. Bounded command packets preserve events and the RAM snapshot at the chosen endpoint. No cross-ROM state transfer, outlier rejection or retries of valid inconvenient results.

Combined FPS = 0.5 * mean(straight FPS) + 0.5 * mean(descent FPS). Gain is a ratio of combined means. The original reference retains 155+155 historical flights per system; v12 and both v13 variants have the same selected 155 start plans, and initial maps match.

95% intervals: 20,000 percentile-bootstrap replicates, seed 2026102913; resample starts within the 78/77 groups, pairing both v13 variants and preserving original-descent dependence. Historical original straight uses an independent plan and is resampled independently.

Data: results/v13/512KB and results/v13/1024KB, plus results/v12 and original historical references. Analysis: scripts/report_v13.py. XEX functional checks are separate; the FPS series measures CAR. The emulator binary was not patched. New measurements must use fresh output directories.

Current tables compare v13 only with the original and v11. The v11 reference uses all 155 straight and 155 descent flights per system from results/v11/summary.json. Gain over v11 is calculated from unrounded 50/50 means; no confidence interval is reported for that ratio. Archived analysis plans and raw data retain the original calculation history.
