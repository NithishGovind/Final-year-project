import cv2
import numpy as np


class VisionSystem:

    def __init__(self, cam_index=0, warp=800, thresh_delta=15):

        self.cap = cv2.VideoCapture(cam_index)
        self.WARP = warp
        self.THRESH_DELTA = thresh_delta

        self.points = []
        self.H = None
        self.sqdict = {}

        cv2.namedWindow("camera")
        cv2.setMouseCallback("camera", self.mouse)

    # -----------------------
    # MOUSE INPUT
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
    # CALIBRATION
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
    # GET BOARD FRAME
    # -----------------------
    def get_board_frame(self):

        ret, frame = self.cap.read()
        if not ret:
            return None, None

        board = cv2.warpPerspective(frame, self.H, (self.WARP, self.WARP))

        gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        return board, gray

    # -----------------------
    # HELPER
    # -----------------------
    def square_mean(self, img, poly):
        mask = np.zeros(img.shape, np.uint8)
        cv2.fillPoly(mask, [np.array(poly, np.int32)], 255)
        return cv2.mean(img, mask=mask)[0]

    # -----------------------
    # MOVE DETECTION (CORE)
    # -----------------------
    def detect_move(self, before_frame, after_frame):

        sources = []
        destinations = []

        for sq, poly in self.sqdict.items():

            before = self.square_mean(before_frame, poly)
            after = self.square_mean(after_frame, poly)

            delta = after - before

            if abs(delta) < self.THRESH_DELTA:
                continue

            if delta > 0:
                sources.append((sq, delta))
            else:
                destinations.append((sq, delta))

        print("\nSources:", sources)
        print("Destinations:", destinations)

        # NORMAL MOVE / CAPTURE
        if len(sources) == 1 and len(destinations) == 1:
            return sources[0][0], destinations[0][0]

        # CASTLING
        if len(sources) == 2 and len(destinations) == 2:

            pairs = []

            for s, _ in sources:
                for d, _ in destinations:
                    dist = abs(ord(s[0]) - ord(d[0]))
                    pairs.append((dist, s, d))

            pairs.sort(reverse=True)

            king_move = pairs[0]
            print("Castling detected")

            return king_move[1], king_move[2]

        print("Detection failed")
        return None, None

    # -----------------------
    # SNAPSHOT
    # -----------------------
    def capture_frame(self):

        _, gray = self.get_board_frame()

        if gray is None:
            return None

        return gray.copy()

    # -----------------------
    # VERIFY MOVE
    # -----------------------
    def verify_move(self, before, after, expected_from, expected_to):

        from_sq, to_sq = self.detect_move(before, after)

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