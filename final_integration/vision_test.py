from vision import VisionSystem
import cv2


def main():

    vision = VisionSystem()
    vision.calibrate()

    print("\nControls:")
    print("d → detect move (before/after)")
    print("q → quit")

    prev_board = None
    awaiting_after = False

    while True:

        ret, frame = vision.cap.read()
        if not ret:
            continue

        board = cv2.warpPerspective(frame, vision.H, (vision.WARP, vision.WARP))

        gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        cv2.imshow("board", board)

        key = cv2.waitKey(1)

        # -----------------------
        # MANUAL MOVE DETECTION
        # -----------------------
        if key == ord('d'):

            if not awaiting_after:

                prev_board = vision.detect_board_state(gray)
                awaiting_after = True

                print("\nCaptured BEFORE")

            else:

                curr_board = vision.detect_board_state(gray)

                from_sq, to_sq = vision.get_move(prev_board, curr_board)

                if from_sq and to_sq:
                    print("Detected move:", from_sq, "->", to_sq)
                else:
                    print("Detection failed")

                awaiting_after = False

        if key == ord('q'):
            break

    vision.release()


if __name__ == "__main__":
    main()