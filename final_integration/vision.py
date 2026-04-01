import cv2
import numpy as np
import time


class VisionSystem:

    def __init__(self, cam_index=1, warp=800):

        self.cap = cv2.VideoCapture(cam_index)
        self.WARP = warp

        self.points = []
        self.H = None
        self.sqdict = {}

        cv2.namedWindow("camera")
        cv2.setMouseCallback("camera", self.mouse)

    # -----------------------
    # MOUSE INPUT (CALIBRATION)
    # -----------------------
    def mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(self.points) < 4:
            self.points.append((x, y))
            print("point", len(self.points), x, y)

    # -----------------------
    # BUILD GRID
    # -----------------------
    def build_sqdict(self):

        files = "abcdefgh"
        ranks = "87654321"
        cell = self.WARP // 8

        for r in range(8):
            for c in range(8):

                x = c * cell
                y = r * cell

                poly = [
                    (x, y),
                    (x + cell, y),
                    (x + cell, y + cell),
                    (x, y + cell)
                ]

                name = files[c] + ranks[r]
                self.sqdict[name] = poly

    # -----------------------
    # CALIBRATION LOOP
    # -----------------------
    def calibrate(self):

        print("Click 4 corners of the board")

        while True:

            ret, frame = self.cap.read()
            if not ret:
                continue

            vis = frame.copy()

            for p in self.points:
                cv2.circle(vis, p, 5, (0, 0, 255), -1)

            if len(self.points) == 4:

                src = np.float32(self.points)
                dst = np.float32([
                    [0, 0],
                    [self.WARP, 0],
                    [self.WARP, self.WARP],
                    [0, self.WARP]
                ])

                self.H = cv2.getPerspectiveTransform(src, dst)
                self.build_sqdict()

                print("Board locked")
                break

            cv2.imshow("camera", vis)

            if cv2.waitKey(1) == 27:
                break

        cv2.destroyWindow("camera")

    # -----------------------
    # HELPER
    # -----------------------
    def square_mean(self, img, poly):
        mask = np.zeros(img.shape, np.uint8)
        cv2.fillPoly(mask, [np.array(poly, np.int32)], 255)
        return cv2.mean(img, mask=mask)[0]

    # -----------------------
    # BOARD STATE DETECTION
    # -----------------------
    def detect_board_state(self, gray):

        board_state = {}

        for sq, poly in self.sqdict.items():

            val = self.square_mean(gray, poly)

            # YOU MUST TUNE THIS
            if val < 100:
                board_state[sq] = 1  # occupied
            else:
                board_state[sq] = 0  # empty

        return board_state

    # -----------------------
    # MOVE EXTRACTION
    # -----------------------
    def get_move(self, prev_board, curr_board):

        changed = []

        for sq in prev_board:
            if prev_board[sq] != curr_board[sq]:
                changed.append(sq)

        print("Changed squares:", changed)

        # NORMAL MOVE / CAPTURE
        if len(changed) == 2:

            sq1, sq2 = changed

            if prev_board[sq1] == 1 and curr_board[sq1] == 0:
                return sq1, sq2

            elif prev_board[sq2] == 1 and curr_board[sq2] == 0:
                return sq2, sq1

        # CASTLING
        if len(changed) == 4:

            sources = []
            destinations = []

            for sq in changed:
                if prev_board[sq] == 1 and curr_board[sq] == 0:
                    sources.append(sq)
                else:
                    destinations.append(sq)

            best = None
            max_dist = -1

            for s in sources:
                for d in destinations:
                    dist = abs(ord(s[0]) - ord(d[0]))
                    if dist > max_dist:
                        max_dist = dist
                        best = (s, d)

            print("Castling detected")
            return best

        return None, None

    # -----------------------
    # CAPTURE BOARD SNAPSHOT
    # -----------------------
    def capture_board(self):

        time.sleep(1.5)  # allow robot to move away

        ret, frame = self.cap.read()
        if not ret:
            return None

        board = cv2.warpPerspective(frame, self.H, (self.WARP, self.WARP))

        gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        return self.detect_board_state(gray)

    # -----------------------
    # VERIFY MOVE
    # -----------------------
    def verify_move(self, prev_board, curr_board, expected_from, expected_to):

        from_sq, to_sq = self.get_move(prev_board, curr_board)

        if from_sq is None:
            print("No valid move detected")
            return False

        if from_sq == expected_from and to_sq == expected_to:
            print("Move verified")
            return True

        print("Mismatch")
        print("Expected:", expected_from, "->", expected_to)
        print("Got:", from_sq, "->", to_sq)

        return False

    # -----------------------
    # CLEANUP
    # -----------------------
    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()