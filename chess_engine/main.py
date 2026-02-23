from game_logic import ChessGame
from gui_chess import ChessGUI
from llm_feedback import LLMFeedback
from feedback_window import FeedbackWindow

import threading

ENGINE_PATH = "/usr/games/stockfish"

game = ChessGame(ENGINE_PATH)
llm = LLMFeedback()
feedback_window = FeedbackWindow()

# Run pygame in separate thread
def run_pygame():
    gui = ChessGUI(game, llm, feedback_window)
    gui.run()

pygame_thread = threading.Thread(target=run_pygame, daemon=True)
pygame_thread.start()

# Run Tkinter in main thread
feedback_window.run()


#  ollama run llama3.2:1b
