# Esc: stack corruption when resuming the game

[English](ESC_DIAGNOSIS.md) · [Polski](ESC_DIAGNOSIS_PL.md)

Reproduced in headless AltirraBridge: the original pauses/resumes correctly; after the second Esc, v10 stops executing game code (PC=$32B5, BRK in the tested run). Also reproduced in v2 (PC=$C1A6, no subsequent images).

## Cause

The original pause is not a simple flag. Code at $AB0A–$AB13 constructs the $B73A loop address on the stack and enters it through RTI, leaving the previous VBI context in place. The next VBI handles the second Esc. Resume at $AB1D removes eight bytes of its context and returns to the earlier call.

Bank protection introduced in v2 redirects VBI entry $B46C to $BFDA. It reads the bank marker at $9FFF and pushes it with PHA. Normal exits through $BFEA pop this extra byte, but the special resume path bypasses that exit. The original LDY #8 at $AB1D was left unchanged. Nine bytes must now be removed: JSR return address (2), bank marker (1), saved A/X/Y registers (3), and interrupt P/PC frame (3). The remaining byte shifts the address read by RTS, sending execution outside the correct code.

## Minimal candidate fix

Change the operand at $AB1E from $08 to $09: LDY #8 -> LDY #9. In a 128 KB ROM, this is offset $1EB1E. The loop ends with Y=0, so the subsequent INY still produces Y=1. There is no need to change the plotter or remove bank protection. Only the resume path changes, not normal flight.

The fix is included in v10.1. The resulting CAR is identical to the tested candidate. Source: `src/pause_resume_stack.asm`; reconstruction: `scripts/rebuild_current.py`.

## Verification

- `scripts/debug_escape.py`: cold boots of original and v10, physical KEYRAW ESC down/up events, registers and stack before pausing and after two Esc presses.
- `scripts/test_escape_fix.py`: reproduction in v2 and 12 PAL plus 12 NTSC pause/resume cycles on the candidate.
- Each of the 24 resumes reached five successive image presentations at $B516 with increasing timestamps. All checks passed.
- Tests cover automatic flight and different intervals between pauses; they are not full validation of every game mode and interrupt phase. No new FPS measurements were made.

The previous performance series used a centered joystick and did not press Esc, so it did not detect this regression.
