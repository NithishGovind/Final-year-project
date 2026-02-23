# ♟️ AI Chess Engine with LLM Feedback

A modular chess application built using:

-   python-chess for board logic
-   Stockfish for engine evaluation
-   pygame for chess GUI
-   LLaMA 3 (via Ollama) for natural-language move feedback
-   Tkinter for feedback display window

This project separates deterministic chess logic from AI commentary
generation.

------------------------------------------------------------------------

## 🚀 Features Implemented

### ✅ Chess Engine

-   Legal move validation using python-chess
-   Stockfish integration for:
    -   Best move calculation
    -   Position evaluation
    -   Evaluation delta tracking

### ✅ GUI

-   Interactive chessboard using pygame
-   Click-to-move piece interaction
-   Engine automatically responds as Black
-   White = Human player

### ✅ LLM Feedback

-   Uses open-source LLaMA 3 via Ollama
-   Generates short natural-language coaching feedback
-   Feedback based on:
    -   Played move
    -   Evaluation change
    -   Engine best move
-   Displayed in a separate Tkinter window

------------------------------------------------------------------------

## 📂 Project Structure

    chess_engine/
    │
    ├── main.py
    ├── gui_chess.py
    ├── game_logic.py
    ├── llm_feedback.py
    ├── feedback_window.py
    └── README.md

------------------------------------------------------------------------

## 🧠 Architecture

    Player Move
        ↓
    Stockfish Analysis
        ↓
    Structured Evaluation Data
        ↓
    LLaMA 3 (Natural Language Feedback)
        ↓
    Tkinter Feedback Window

Chess correctness is handled by Stockfish. Language generation is
handled by LLaMA.

------------------------------------------------------------------------

## 🔧 Requirements

Install required Python packages:

    pip install pygame python-chess requests

Tkinter is usually pre-installed with Python.

------------------------------------------------------------------------

## ♟️ Install Stockfish

Ubuntu:

    sudo apt install stockfish

Verify installation:

    which stockfish

Update ENGINE_PATH in main.py if necessary.

------------------------------------------------------------------------

## 🧠 Install Ollama (For LLaMA 3)

Install Ollama:

    curl -fsSL https://ollama.com/install.sh | sh

Pull model:

    ollama pull llama3.2:1b

Check installed models:

    ollama list

Ensure the model name matches what is used in llm_feedback.py.

------------------------------------------------------------------------

## ▶️ How To Run

From the project root:

    python3 main.py

What happens:

-   Pygame window opens → Chess board
-   Tkinter window opens → Feedback display
-   Play as White
-   Engine plays as Black
-   LLaMA generates feedback after each move

------------------------------------------------------------------------

## ⚙️ Configuration

Inside llm_feedback.py, you can change:

    model="llama3.2:1b"

You may switch to:

-   llama3:8b
-   mistral
-   Any installed Ollama model

Lower temperature → more deterministic output.

------------------------------------------------------------------------

## 🧪 Current Capabilities

-   Detects move quality based on evaluation delta
-   Classifies mistakes/blunders
-   Provides concise coaching-style feedback
-   Runs LLM asynchronously (no GUI freeze)

------------------------------------------------------------------------

## 📌 Current Limitations

-   No move highlighting
-   No evaluation bar
-   No PGN export
-   No promotion UI
-   No move history panel
-   LLM feedback depends on evaluation delta (not deep tactical
    reasoning)

------------------------------------------------------------------------

## 🧩 Future Improvements

-   Evaluation bar visualization
-   Move history tracking
-   Color-coded mistake detection
-   Voice feedback (Text-to-Speech)
-   Adaptive coaching level (Beginner / Advanced)
-   Post-game analysis summary

------------------------------------------------------------------------

## 🎯 Design Philosophy

-   Deterministic systems handle correctness (Stockfish).
-   LLM handles explanation only.
-   Modular architecture for easy robotics integration.
-   Thread-safe LLM feedback system.

------------------------------------------------------------------------

## 🛠 Tested Environment

-   Ubuntu 22.04
-   Python 3.10+
-   pygame 2.6+
-   Ollama (local LLaMA 3)

------------------------------------------------------------------------

## 📖 Summary

This project combines classical chess engine computation with modern
open-source LLM commentary, demonstrating integration between symbolic
reasoning (Stockfish) and generative AI (LLaMA).
