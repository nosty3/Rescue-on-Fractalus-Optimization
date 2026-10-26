# Protocol addendum: natural flight ending before 60 s

[English](PROTOCOL_ADDENDUM.md) · [Polski](PROTOCOL_ADDENDUM_PL.md)

This rule was added after 47 completed trials, when scenario 48 (v9, trial 24, START after 3357 menu frames) ended its flight before one minute. This changes event handling during the study; it was not part of the original plan. The sample size of 155 per version, schedule, and input selection are unchanged.

Reproduction showed game mode changing from 2 to 0 at instruction $B3C4 (STA $4A), about 32.2484 s into measurement. It follows the standard $A444 → $B3B6 path after flag $063A is set, then proceeds to a fading/end-of-game sequence. This study did not identify which specific object or gameplay event set the flag. This observation alone should not be presented as a v9 bug.

## Applicable rule

- Measure FPS during flight for up to 60 seconds, or until the first exit from flight mode if earlier.
- Retain every such trial in the mean; do not draw a replacement map.
- Compute FPS from complete intervals between completed images, through the last completed image in flight mode. The ending animation and time without new terrain images are excluded from the denominator.
- Record the exact mode-change time, image count, last completed image time, and `complete_window=false` for windows not fully completed.
- Every 15/30/60 s checkpoint not reached receives the result from the entire available flight segment and an explicit shortened-window marker. This is not a result for a full window of that duration.
- No measurable interval, or a stopped renderer while mode 2 remains active, is still an error requiring separate diagnosis; it is not automatically removed.
- Report the number of shortened flights and their duration range. The result is mean FPS for flights lasting UP TO 60 s, not just mean FPS of complete minutes.

Other conditions, the original game code, and the 170-frame warm-up remain unchanged. Monitoring the mode write is a debugger checkpoint, not a game-memory modification. The 47 previously completed trials remain valid observations under this rule.

This addendum must be disclosed when interpreting results. From this point, the study is not fully preregistered for the new outcome definition. Confidence intervals describe the amended scenario; they do not resolve the issue of choosing a scenario definition after the study began. Analyzing only flights that survived a minute would introduce gameplay-dependent selection, so that is not done.
