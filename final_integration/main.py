from vision import VisionSystem
from manipulator import Manipulator
from engine import ChessEngine, ChessBoardUI
import time


ENGINE_PATH = "/usr/games/stockfish"   # change if needed


def main():

    # -----------------------
    # INIT SYSTEMS
    # -----------------------
    vision = VisionSystem()
    robot = Manipulator(port="COM3")
    engine = ChessEngine(ENGINE_PATH)

    ui = ChessBoardUI(engine)

    # -----------------------
    # CALIBRATE VISION
    # -----------------------
    vision.calibrate()

    print("\nSystem Ready")

    # -----------------------
    # MAIN LOOP
    # -----------------------
    while True:

        # -----------------------
        # UI EVENTS
        # -----------------------
        if not ui.handle_events():
            break

        ui.update()

        # =====================
        # HUMAN MOVE
        # =====================
        print("\nWaiting for human move...")

        prev_board = vision.capture_board()

        while True:

            if not ui.handle_events():
                break

            ui.update()

            curr_board = vision.capture_board()

            if curr_board != prev_board:
                break

        from_sq, to_sq = vision.get_move(prev_board, curr_board)

        if from_sq is None:
            print("Vision failed. Retry.")
            continue

        print("Human move:", from_sq, "->", to_sq)

        # validate move
        if not engine.apply_move_uci(from_sq, to_sq):
            print("Illegal move. Fix board.")
            continue

        engine.print_pretty_board()

        if engine.is_game_over():
            print("Game Over:", engine.get_result())
            break

        # =====================
        # ENGINE MOVE
        # =====================
        print("\nEngine thinking...")

        move = engine.get_best_move()
        from_sq, to_sq = engine.move_to_squares(move)

        print("Engine move:", from_sq, "->", to_sq)

        # ---------------------
        # HANDLE CAPTURE
        # ---------------------
        if engine.is_capture(move):
            print("Capture detected")
            robot.capture_piece(to_sq)

        # ---------------------
        # ROBOT MOVE
        # ---------------------
        prev_board = vision.capture_board()

        robot.execute_move(from_sq, to_sq)

        # IMPORTANT: wait for robot to clear frame
        time.sleep(2)

        curr_board = vision.capture_board()

        # ---------------------
        # VERIFY MOVE
        # ---------------------
        if vision.verify_move(prev_board, curr_board, from_sq, to_sq):

            engine.apply_engine_move(move)
            engine.print_pretty_board()

        else:
            print("Robot failed. Fix manually.")
            continue

        if engine.is_game_over():
            print("Game Over:", engine.get_result())
            break

    # -----------------------
    # CLEANUP
    # -----------------------
    engine.close()
    robot.close()
    vision.release()


if __name__ == "__main__":
    main()