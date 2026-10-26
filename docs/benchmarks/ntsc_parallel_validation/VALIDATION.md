# Validation of four isolated emulators

[English](VALIDATION.md) · [Polski](VALIDATION_PL.md)

The user authorized four parallel processes after confirming agreement with sequential measurement. The ongoing measurement was stopped after 86 completed trials; the unfinished trial is rerun with the same input.

Four existing pilot references were selected: the minimum and maximum 60 s FPS separately for original and v9. They were launched simultaneously from native BOOT, without loading states. Each emulator had a separate process, system-assigned port, token, controller, and output files.

All four trials matched exactly in:

- image counts and ticks for 15, 30, and 60 s;
- complete lists of image intervals;
- full 32 KB RAM at flight entry, after warm-up, and at measurement end.

Machine-readable results: `validation.json`. Procedure: `scripts/validate_ntsc_parallel.py`. This validates these four scenarios; it does not prove emulator correctness in every situation.

Main-study continuation: `scripts/benchmark_ntsc_parallel.py`. Up to four emulators, each block finishing before the next begins, one thread saving the aggregate in plan order, and atomic file replacement. Sample size, planned START timings, and the FPS counting method remain unchanged. Actual PC execution time is not part of FPS calculations: emulated Atari ticks are used.
