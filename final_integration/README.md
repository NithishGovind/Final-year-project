# Chess Playing Manipulator System

This project implements an end-to-end robotic chess system integrating:
- Computer Vision
- Robotic Manipulator
- Chess Engine (AI)

The system allows a human to play chess against a robotic arm, with vision-based move detection and physical execution.

---

## 1. Vision Module (`vision.py`)

### Purpose
Handles board perception using a camera.

### Features
- Perspective calibration using 4-point selection
- Chessboard grid mapping (a1–h8)
- Square-wise intensity analysis
- Board state detection (occupied / empty)
- Move extraction by comparing states
- Move verification after robot execution

### Key Functions
- `calibrate()` → initializes board transform  
- `detect_board_state()` → returns occupancy map  
- `get_move(prev, curr)` → extracts move  
- `capture_board()` → snapshot of current board  
- `verify_move()` → confirms expected move  

### Role in System
- Detects human moves
- Verifies robot execution

---

## 2. Manipulator Module (`manipulator.py`)

### Purpose
Controls the robotic arm using serial communication.

### Features
- Predefined joint angle mapping for all 64 squares
- Smooth motion sequencing (base, shoulder, elbow)
- Electromagnet control (pick/place)
- Capture handling (removal of opponent pieces)

### Key Functions
- `move_to(square)` → move arm to position  
- `pick(square)` → pick piece  
- `place(square)` → place piece  
- `execute_move(from, to)` → full move execution  
- `capture_piece(square)` → remove captured piece  

### Role in System
- Executes engine moves physically
- Acts deterministically (no sensing)

---

## 3. Engine Module (`engine.py`)

### Purpose
Maintains game logic and decision making.

### Powered by
- python-chess
- Stockfish

### Features
- Legal move validation
- AI move generation
- Board state tracking
- Capture detection
- Game termination detection
- Pygame-based board visualization

### Key Functions
- `apply_move_uci()` → applies human move  
- `get_best_move()` → AI move generation  
- `apply_engine_move()` → update board  
- `is_capture()` → detect captures  
- `print_pretty_board()` → console board  
- `ChessBoardUI` → graphical board display  

### Role in System
- Acts as single source of truth
- Prevents invalid moves from corrupting state

---

## System Workflow

Human Move → Vision Detection → Engine Validation  
Engine Computes Move → Robot Executes → Vision Verifies  
Board State Updated

---

## Key Design Principle

Vision → Observes  
Engine → Decides  
Manipulator → Executes  

---

## Known Limitations

- Lighting sensitivity in vision
- No piece color detection from vision
- No promotion handling (yet)
- Requires stable camera setup

---

## Future Improvements

- Adaptive vision thresholds
- Automatic human move detection
- GUI enhancements (highlight moves)
- Error recovery and retry logic
