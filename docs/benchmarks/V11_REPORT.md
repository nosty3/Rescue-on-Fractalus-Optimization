# v11 final report

[English](V11_REPORT.md) · [Polski](V11_REPORT_PL.md)

v11 is exactly the sentinel_depth_lazy_scan_fill candidate from the full study. Renaming the release does not change the ROM. The music-pointer fix affects XEX only.

Original versus latest candidate comparison

New measurements: 155 original-game descent flights in PAL and 155 in NTSC. Four isolated emulators, native cold boot per trial, 800XL/64K, 170 warmup frames, up to 60 seconds measured flight. Input: 1 s joystick up, 3 s neutral. Same start schedule as candidate. B516 counter and emulated Atari clock; natural early ends retained, no outlier removal.

Straight flight: previously measured results, not rerun. Historical original straight flights used an independently sampled start schedule, so straight-flight comparison is not paired. Descent uses a shared schedule. Combined FPS = 50/50 mean of the two scenarios; gain = ratio of means minus 1. Each flight has equal weight.

PAL

| Scenario | Original FPS | Candidate FPS | Delta FPS | Gain |
|---|---:|---:|---:|---:|
| Straight flight | 6.4421 | 9.0779 | +2.6358 | +40.91% |
| Descent pulses | 6.1013 | 8.4879 | +2.3866 | +39.12% |
| 50/50 mean | 6.2717 | 8.7829 | +2.5112 | +40.04% |

Early ends: original_straight 3/155, original_steering 4/155, candidate_straight 5/155, candidate_steering 3/155

NTSC

| Scenario | Original FPS | Candidate FPS | Delta FPS | Gain |
|---|---:|---:|---:|---:|
| Straight flight | 5.8043 | 8.3120 | +2.5077 | +43.20% |
| Descent pulses | 5.3787 | 7.6942 | +2.3155 | +43.05% |
| 50/50 mean | 5.5915 | 8.0031 | +2.4116 | +43.13% |

Early ends: original_straight 1/155, original_steering 4/155, candidate_straight 2/155, candidate_steering 5/155

Candidate ROM SHA256: ec01982121b70baca35f04568617965c3164e716e0a5eb3c6ebcbb123566a868
Original ROM SHA256: 1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68


Full up38 vs candidate benchmark: straight and controlled flight

Completed 1240 flights: 4 arms × 2 video standards × 155 trials. Pilot and transport-validation runs are excluded.

METHOD
Every flight uses a fresh Altirra process, native cold ROM boot, Atari 800XL/64 KB and no accelerator. The same frozen 155-start schedule (v9 schedule, seed 2026102303), 170 video frames of warmup, and up to 60 seconds of emulated time are used. Configured for four isolated emulators in parallel in 31 closed blocks. An additional-runner incident is documented below. Arms share start delays; entry RAM equivalence was verified across all four arms within each video/trial pair, with a documented exception for unread bytes $0270–$0277.

Straight flight: centered joystick throughout. Controlled flight: centered warmup, then repeat 1 second joystick up (descent), 3 seconds centered from measurement time zero; no turning or firing. Inputs follow emulated Atari ticks, not rendered-image counts or host time.

Presentation counter: B516, counting complete intervals between ready images. The first complete interval crossing 60 seconds closes the window. Natural early ends remain in the sample, measured through the last completed flight image. No outliers were removed. The primary mean weights each flight equally; pooled time-weighted FPS is also reported.

RESULTS

PAL
straight: up38 8.936562 FPS; candidate 9.077906 FPS; delta +0.141345 FPS; gain +1.5816%.
95% interval for FPS difference: [+0.095330, +0.189203]; for gain: [+1.0637%, +2.1236%].
  up38: SD=0.531235; median=8.890032; mean CI95=[8.864113, 9.009909]; early ends=3/155; seconds=[24.889, 60.127]; pooled FPS=8.946967.
  candidate: SD=0.525716; median=9.048928; mean CI95=[9.006947, 9.148909]; early ends=5/155; seconds=[26.935, 60.168]; pooled FPS=9.088176.
steering: up38 8.086260 FPS; candidate 8.487950 FPS; delta +0.401690 FPS; gain +4.9676%.
95% interval for FPS difference: [+0.369812, +0.433109]; for gain: [+4.5688%, +5.3620%].
  up38: SD=0.446394; median=8.140872; mean CI95=[8.026410, 8.144654]; early ends=6/155; seconds=[41.917, 60.168]; pooled FPS=8.089162.
  candidate: SD=0.480476; median=8.476662; mean CI95=[8.422715, 8.552225]; early ends=3/155; seconds=[29.723, 60.127]; pooled FPS=8.490533.
Additional relative gain under controlled flight vs straight flight: +3.3859 percentage points; CI95=[+2.7171, +4.0260].
Additional absolute FPS gain: +0.260346; CI95=[+0.202767, +0.315505].
In this test controlled flight increased the candidate relative advantage; the interval excludes zero.

NTSC
straight: up38 8.167030 FPS; candidate 8.312030 FPS; delta +0.145000 FPS; gain +1.7754%.
95% interval for FPS difference: [+0.097869, +0.191921]; for gain: [+1.1935%, +2.3582%].
  up38: SD=0.517654; median=8.075168; mean CI95=[8.093205, 8.241723]; early ends=0/155; seconds=[60.011, 60.144]; pooled FPS=8.166987.
  candidate: SD=0.504864; median=8.203808; mean CI95=[8.242746, 8.381982]; early ends=2/155; seconds=[51.199, 60.161]; pooled FPS=8.313216.
steering: up38 7.309115 FPS; candidate 7.694186 FPS; delta +0.385071 FPS; gain +5.2684%.
95% interval for FPS difference: [+0.359168, +0.411162]; for gain: [+4.9142%, +5.6275%].
  up38: SD=0.361053; median=7.321857; mean CI95=[7.257190, 7.361106]; early ends=10/155; seconds=[44.374, 60.311]; pooled FPS=7.311214.
  candidate: SD=0.408361; median=7.752359; mean CI95=[7.634656, 7.752224]; early ends=5/155; seconds=[48.446, 60.144]; pooled FPS=7.698062.
Additional relative gain under controlled flight vs straight flight: +3.4929 percentage points; CI95=[+2.8247, +4.1513].
Additional absolute FPS gain: +0.240071; CI95=[+0.187409, +0.292126].
In this test controlled flight increased the candidate relative advantage; the interval excludes zero.

Execution note: after the transport change, a process-name filter failed to stop the old runner. Two sets of four emulators overlapped for part of the series, redundantly computing some flights. The old runner and its children were identified and stopped. Analysis includes exactly one record per arm/video/trial. See runtime_notes.json. This changed host load, not Atari clock frequency; reproducibility checks assess equivalence.

UNCERTAINTY AND INTERPRETATION
50,000 bootstrap replicates of whole matched flights within 31 blocks; seed 2026103001. All four arms retain joint resampling indices. Percentile 95% intervals, without finite-population correction for 600 possible start delays or multiple-comparison adjustment. These approximate intervals concern this schedule and flight protocol, not every gameplay situation. The 15/30/60-second checkpoints are dependent windows of the same flights.

Shared entry state and control schedule do not guarantee identical subsequent geometry, events or flight-ending time across versions with different execution timing. Descent changes more than visible sky coverage. This tests practical FPS for a fixed scenario; it does not causally isolate mountain coverage. Different early-ending rates matter when interpreting means; these flights were not excluded after inspecting results.

VALIDATION AND ACCELERATION
TCP_NODELAY is enabled. Step, PC/mode read and clock commands are sent together, preserving ordering and emulator barriers. Eight checks matched ordinary transport in events, joystick timing and final RAM. Four straight-flight checks matched the original counter; four sequential steering checks matched parallel execution. Completed results were retained across the transport change, and interrupted flights were restarted from boot. An alternative profiler counter was rejected due to its 4096-record limit; none of its results entered the series.

Historical up38 straight-flight FPS/count exact matches: 310/310. Maximum input timing rounding: 0.5 Atari ticks.

FILES
plan.json; validation.json; transport-validation.json; integrity.json; summary.json; entry-equivalence.json; entry-diagnostic/read-watch.json; entry-diagnostic/read-watch-steering.json; benchmark.json; main/*.json; FPS_GAIN.png/svg; FPS_DISTRIBUTION_PAL.png/svg; FPS_DISTRIBUTION_NTSC.png/svg; ALL_FLIGHTS_PAL.png; ALL_FLIGHTS_NTSC.png.
scripts/benchmark_up38_full.py; scripts/summarize_up38_full.py; scripts/report_up38_full.py.

ROM versions were neither modified nor published as part of this measurement.

Final checks: all 310 straight up38 flights reproduced historical FPS and presentation counts. Four independent candidate repetitions (PAL/NTSC, straight/controlled) exactly matched every presentation timestamp, results, controls and full entry/end RAM. See post-validation.json. Eight start groups had different raw RAM hashes; offline comparisons restricted all differences to $0270–$0277 (0 or 228). Eight additional 60-second read-watch observations, covering both versions and both flight modes for PAL trials 11 and 13, found no reads of these bytes. Measurement-flight memory was never modified.



Local filenames above refer to the research archive. Published observations are consolidated into results/v11/flights.jsonl; plans, validation and summaries are alongside it. RAM dumps are not published.
