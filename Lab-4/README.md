# Lab-4 — Bubble Bobble Repair Lab (AI-assisted debugging)

**Course:** Software Engineering · PES University, Dept. of CSE
**Project:** #26 — `26_bubbleBobble` (Pygame Bubble Bobble-lite clone)
**Name:** Pramiti Ragavendra Udupa  **SRN:** PES1UG24CS331

The provided game had one deliberate bug and three unimplemented hook functions.
All four tasks were completed by working with an LLM (Claude) as a debugging and
pair-programming partner, then reviewing and testing the result.

## Contents

| File | Deliverable |
|---|---|
| `Before_Changes.mp4` | 10-second gameplay video **before** the changes — bubbles pass through enemies without trapping them |
| `After_Changes.mp4` | 10-second gameplay video **after** the changes — enemies are trapped, bubble colours change, fruit is collected and counted |
| `game.py` | Final game with the bug fix and all three features |
| `changes.diff` | Diff of `game.py` against the original provided code |
| `Chat_History.pdf` | Chat history with Claude (LLM): reviewing, re-testing, documenting and submitting the work. The fixes and videos were first produced in an earlier Claude chat. |

## Changes

| Task | Function | Change |
|---|---|---|
| 1 — Bug fix | `Game.trap_enemies` | The squared distance was compared against `24 * 2` (= 48) instead of `24 ** 2` (= 576), so trapping needed a near pixel-perfect overlap. Threshold is now `24 ** 2`. |
| 2 — Bubble tint | `bubble_tint(bubble)` | Empty bubbles fade from bright cyan to pale blue as they age. Bubbles holding an enemy shift pink → yellow → red as `bubble.life` runs out, and flash white in the last 1.5 s before the enemy escapes. |
| 3 — Fruit pickup | `on_fruit_collected(fruit)` | Burst of gold sparkle particles (outward velocity, gravity, fade-out) and a **Fruits** counter in the HUD. Both reset on `R`. |
| 4 — Bonus life | `bonus_life_threshold()` | Returns `5000`: an extra life every 5000 points. HUD shows `Next life @ <score>`. |

## Verification

- Ran the game headless for 20,000 frames with random inputs — no crashes.
- Set the score to 5000 and confirmed lives go from 3 to 4.
- Confirmed in the after video that touching bubbles trap enemies.

## How to run

```bash
pip install pygame
python game.py
```

**Controls:** Arrow keys to move, Up to jump, Space to blow a bubble, `R` to reset.
