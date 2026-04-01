import chess
from game_logic import ChessGame
from llm_feedback import LLMFeedback
from tts_engine import TTSEngine
from vision_system import VisionSystem

ENGINE_PATH = "/usr/games/stockfish"

game = ChessGame(ENGINE_PATH)
llm = LLMFeedback()
tts = TTSEngine()

last_valid_fen = game.get_board().fen()


def on_move_detected(from_sq, to_sq):

    global last_valid_fen

    board = game.get_board()

    move = chess.Move.from_uci(from_sq + to_sq)

    # Try auto queen promotion
    if move not in board.legal_moves:
        try:
            move = chess.Move.from_uci(from_sq + to_sq + "q")
        except:
            pass

    if move in board.legal_moves:

        print("Legal move detected")

        # Analyze BEFORE push
        analysis = game.analyze_move(move)

        # Push move
        board.push(move)

        # Save state
        last_valid_fen = board.fen()

        # LLM feedback
        feedback = llm.generate_feedback(analysis)
        print("LLM:", feedback)
        tts.speak_async(feedback)

        # Engine move
        engine_move = game.make_engine_move()

        if engine_move:
            last_valid_fen = board.fen()
            print("Engine move:", engine_move)
            print("Now physically execute engine move.")

        return True

    else:
        print("Illegal move detected — restoring previous state")

        board.set_fen(last_valid_fen)

        warning = "Illegal move detected. Reset the board."
        print(warning)
        tts.speak_async(warning)

        return False


vision = VisionSystem(on_move_detected)
vision.run()