from vision import VisionSystem
from manipulator import Manipulator
from engine import ChessEngine, ChessBoardUI
import serial.tools.list_ports
import cv2
import time


ENGINE_PATH = "/usr/games/stockfish"


# -----------------------
# PORT DETECTION
# -----------------------
def find_arduino_port():
    ports = list(serial.tools.list_ports.comports())

    for port in ports:
        if (
            "Arduino" in port.description
            or "ttyACM" in port.device
            or "ttyUSB" in port.device
        ):
            print(f"Auto-detected Arduino on {port.device}")
            return port.device

    return None


def choose_port():
    ports = list(serial.tools.list_ports.comports())

    if not ports:
        raise Exception("No serial ports found.")

    print("\nAvailable ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} ({port.description})")

    idx = int(input("Select port number: "))
    return ports[idx].device


# -----------------------
# MAIN
# -----------------------
def main():

    vision = VisionSystem()

    port = find_arduino_port()
    if port is None:
        port = choose_port()

    robot = Manipulator(port=port)
    engine = ChessEngine(ENGINE_PATH)
    ui = ChessBoardUI(engine)

    vision.calibrate()

    print("\nSystem Ready")
    print("Robot = WHITE, You = BLACK")
    print("Press 'd' for capture")

    turn = "engine"   # engine starts

    awaiting_after = False
    before = None

    while True:

        # -----------------------
        # UI
        # -----------------------
        if not ui.handle_events():
            break
        ui.update()

        # -----------------------
        # CAMERA VIEW
        # -----------------------
        board, _ = vision.get_board_frame()
        if board is not None:
            cv2.imshow("board", board)

        key = cv2.waitKey(1)

        # =====================
        # ENGINE MOVE (WHITE)
        # =====================
        if turn == "engine":

            print("\nEngine (White) thinking...")

            move = engine.get_best_move()
            from_sq, to_sq = engine.move_to_squares(move)

            print("Engine:", from_sq, "->", to_sq)

            # capture handling
            if engine.is_capture(move):
                robot.capture_piece(to_sq)

            # BEFORE snapshot
            print("Press 'd' BEFORE robot move")
            while True:
                if cv2.waitKey(1) == ord('d'):
                    before = vision.capture_frame()
                    print("Captured BEFORE (robot)")
                    break
                time.sleep(0.01)

            robot.execute_move(from_sq, to_sq)
            time.sleep(2)

            # AFTER snapshot
            print("Press 'd' AFTER robot move")
            while True:
                if cv2.waitKey(1) == ord('d'):
                    after = vision.capture_frame()
                    print("Captured AFTER (robot)")
                    break

            # VERIFY (non-blocking logic)
            verified = vision.verify_move(before, after, from_sq, to_sq)

            if verified:
                print("Robot move verified")
            else:
                print("⚠️ Vision failed — forcing sync")

            # 🔥 ALWAYS APPLY MOVE (CRITICAL FIX)
            engine.apply_engine_move(move)
            engine.print_pretty_board()

            turn = "human"

        # =====================
        # HUMAN MOVE (BLACK)
        # =====================
        if key == ord('d') and turn == "human":

            # BEFORE
            if not awaiting_after:
                before = vision.capture_frame()
                awaiting_after = True
                print("\nCaptured BEFORE (human)")

            # AFTER
            else:
                after = vision.capture_frame()

                from_sq, to_sq = vision.detect_move(before, after)

                if from_sq is None:
                    print("Vision failed. Retry.")
                    awaiting_after = False
                    continue

                print("Human (Black):", from_sq, "->", to_sq)

                # validate
                if not engine.apply_move_uci(from_sq, to_sq):
                    print("Illegal move")
                    awaiting_after = False
                    continue

                engine.print_pretty_board()

                awaiting_after = False
                turn = "engine"

        if key == 27:
            break

    # -----------------------
    # CLEANUP
    # -----------------------
    engine.close()
    robot.close()
    vision.release()


if __name__ == "__main__":
    main()