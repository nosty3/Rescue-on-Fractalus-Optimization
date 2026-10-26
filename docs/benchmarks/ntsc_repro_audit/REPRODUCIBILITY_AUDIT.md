Historical research document. Old paths and results refer to the experiment described; the current implementation is documented in docs/OPTIMIZATIONS.md and aggregate results in docs/benchmarks/METHOD.md (paths from the repository root).

[English](REPRODUCIBILITY_AUDIT.md) · [Polski](REPRODUCIBILITY_AUDIT_PL.md)

# NTSC measurement reproducibility audit

## Scope

Ran 24 control flights of 15 seconds without changing game code:

- 3 BOOT starts in one emulator process per version;
- 3 BOOT starts in 3 fresh processes per version;
- 2 control reloads of each version's own saved state;
- 8 fresh starts reproducing the minimum and maximum of each of the four old 20-trial groups.

Control states were never transferred between versions. State-reload trials were diagnostic only and are excluded from the new normal-start means.

## Results with identical START timing

NTSC, 800XL 64 KB, stock addons, 3300 video frames before START, stop at first entry to $A32E, release START, 170 warm-up frames, straight flight, measurement at $B516 through the first complete image after 15 seconds.

| Version | FPS | Matching runs |
|---|---:|---:|
| Original | 5.5680427349 | 8/8 |
| v9 | 7.5152824655 | 8/8 |

Within each version, every interval between successive images matched, not just mean FPS. All 6 native entries of each version had identical 32 KB RAM at $A32E. Replacing repeated BOOT with a fresh emulator process did not change the result.

The original and v9 generated different terrain. This table must not be used to calculate pure code speedup on the same map.

## Reproducing old extreme results

Selected the minimum and maximum separately per version and old series (8 cases). Each case was restarted in a new emulator process using its old START timing.

All 8 cases matched in:

- SHA-256 of terrain data $0900–$09FF;
- count of completed image intervals;
- complete measurement duration to one emulated Atari tick;
- FPS calculated from those two quantities.

No counter error or dependence of these reproduced results on process history was found. Results are reproducible properties of specific starts. This does not prove reproduction of all 80 old trials or complete emulator correctness.

## Conclusion and next stage

The audit did not support the suspicion that accumulated process state caused the difference between old series. It confirmed dependence on a specific, reproducible starting scenario. It does not prove uniform sampling of all possible maps or matching terrain between ROMs.

Next is a pilot of 20 native starts per version, each in a fresh process, with a 60-second flight. The 15/30/60 s checkpoints belong to the same flight and are not separate independent trials. Version order is randomized in balanced blocks. START timing distribution: uniform selection from menu frames 3000–3599 without repeating a timing within a version. This is an explicitly defined population of emulator scenarios, not the mean of all possible gameplay on hardware.

## Files

- `audit.json`: 16 control runs and metadata.
- `old-extremes.json`: 8 reproduced old results.
- `scripts/ntsc_repro_common.py`: emulator initialization, flight entry, and measurement.
- `scripts/audit_ntsc_repro.py`: comparison of BOOT, new processes, and same-version state reloads.
- `scripts/recheck_ntsc_extremes.py`: reproduction of old extreme trials.

Memory/state files and complete event lists are local diagnostic data, not material for publication in the repository.
