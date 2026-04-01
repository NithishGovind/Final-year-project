# Chess Vision System (Hardware Testing Only)

## What this is

This project detects **physical chess piece movement** using a camera and basic image differencing.

It does **not** validate chess rules.  
It does **not** use any chess engine.  
It only tells you: *something moved from square A to square B.*

Use this to test your manipulator, not your logic.

---

## What you should use

Use:

new_app.py

Ignore:

new_app_digital.py

Unless you want a UI, which you don’t need right now.

---

## Requirements

Install the bare minimum:

pip install opencv-python numpy

That’s it.

If you try running the digital version, that’s your problem—you’ll need:

pip install pygame chess

And Stockfish if you want engine integration.

---

## Hardware Setup

- Camera mounted above chessboard
- Entire board visible
- No garbage lighting (shadows will affect detection)
- Stable camera

---

## How to Run

python new_app.py

---

## Calibration (Important)

1. Click **4 corners of the chessboard** in this order:
   - Top-left
   - Top-right
   - Bottom-right
   - Bottom-left

2. Once done, system locks perspective.

If you click wrong, restart.

---

## Workflow

### Step 1 — Capture BEFORE move

Press:

d

This stores baseline frame.

---

### Step 2 — Move piece

Physically move piece using manipulator or hand.

---

### Step 3 — Capture AFTER move

Press:

d

Now system computes movement.

---

## Output

You’ll see:

Movement ranking:
('e2', 523)
('e4', 498)

Detected move: e2 -> e4

Top two squares = most change.

---

## How it works

- Perspective warp → square grid
- Grayscale + blur
- Frame difference
- Threshold
- Morphological cleanup
- Count changed pixels per square

---

## Limitations

- Lighting changes = false positives
- Motion blur = poor results
- Piece occlusion = confusion
- No chess rule validation
- Assumes only ONE move between snapshots

---

## Common Mistakes

- Clicking wrong board corners → wrong mapping
- Moving multiple pieces → undefined output
- Changing lighting between frames → false detection
- Camera auto-exposure shifting → inconsistent diff

---

## Notes on Digital Version (Optional)

new_app_digital.py adds:
- Pygame UI
- Chess rule validation

If you want to use it:

### Install dependencies

pip install pygame chess

### Optional engine

Install Stockfish and configure path manually (especially on Windows).

---

## Bottom line

This is a **vision trigger system**, not a chess engine.
