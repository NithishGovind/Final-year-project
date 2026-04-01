import chess
import chess.engine

# Create board
board = chess.Board()

# Start Stockfish
engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")  
# Change path if needed

print(board)

while not board.is_game_over():

    # ---- USER MOVE ----
    user_move = input("Your move (in UCI format, e2e4): ")

    try:
        move = chess.Move.from_uci(user_move)

        if move in board.legal_moves:
            board.push(move)
        else:
            print("Illegal move.")
            continue

    except:
        print("Invalid format.")
        continue

    print("\nBoard after your move:")
    print(board)

    if board.is_game_over():
        break

    # ---- ENGINE MOVE ----
    result = engine.play(board, chess.engine.Limit(time=0.5))
    board.push(result.move)

    print("\nEngine move:", result.move)
    print(board.unicode())

engine.quit()

print("\nGame Over:", board.result())