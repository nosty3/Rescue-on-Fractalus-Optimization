# v12 FPS methodology

155 independent cold boots per system: 78 straight flights and 77 descent flights. Four isolated Altirra processes, 800XL/64 KB, PAL or NTSC, CPU history off and unlimited host pacing. 170 warmup video frames, then a nominal 60 s window closed at a B516 presentation interval. Use the emulated Atari clock, not host time. Descent: joystick up for 1 s every 4 s, otherwise neutral.

Start/scenario assignments were frozen before the series. Result = 0.5 * mean straight-flight FPS + 0.5 * mean descent-flight FPS. This is not a simple average of 155 samples with unequal scenario counts. Retain natural ends, without outlier removal or cross-ROM save-state transfer.

The transport queues bounded command packets, retains every presentation and joystick deadline, and selects RAM at the correct endpoint. The emulator was not modified. Original/v11 retain full historical data of 155 flights per scenario/system. Original straight flight uses an independent start plan; do not invent pairs by trial number.

95% bootstrap: 20,000 replicates, seed 2026102912; resample whole starts within the 78/77 groups, retaining dependence with v11 and original descent; independently resample original straight. Data: results/v12/plan.json, flights.jsonl, summary.json and analysis-plan.json. Report: V12_REPORT.md.

Use a fresh output directory for a new measurement; do not overwrite published observations. New runner: scripts/benchmark_current.py --help. Install the bridge under tools/bridge or set FRACTALUS_BRIDGE_DIR. XEX has separate functional validation; published FPS measures CAR.
