import cv2
import numpy as np


class VisionSystem:

    def __init__(self, move_callback):

        self.move_callback = move_callback

        self.CAM_INDEX = 0
        self.WARP = 800
        self.THRESH = 25

        self.cap = cv2.VideoCapture(self.CAM_INDEX)

        self.points = []
        self.H = None
        self.sqdict = {}

        self.before_frame = None
        self.awaiting_after = False
        self.move_index = 0

        cv2.namedWindow("camera")
        cv2.setMouseCallback("camera", self.mouse)
    def reset_snapshot(self):
        self.before_frame = None
        self.awaiting_after = False
    # -----------------------
    # MOUSE INPUT
    # -----------------------
    def mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(self.points) < 4:
            self.points.append((x, y))
            print("point", len(self.points), x, y)

    # -----------------------
    # BUILD BOARD GRID (UNCHANGED)
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

    def draw_grid(self, img):

        cell = self.WARP // 8

        for i in range(1, 8):
            cv2.line(img, (0, i * cell), (self.WARP, i * cell), (0, 255, 0), 1)
            cv2.line(img, (i * cell, 0), (i * cell, self.WARP), (0, 255, 0), 1)

    # -----------------------
    # MAIN LOOP (UNCHANGED LOGIC)
    # -----------------------
    def run(self):

        while True:

            ret, frame = self.cap.read()
            if not ret:
                continue

            vis = frame.copy()

            for p in self.points:
                cv2.circle(vis, p, 5, (0, 0, 255), -1)

            # LOCK BOARD
            if len(self.points) == 4 and self.H is None:

                src = np.float32(self.points)

                dst = np.float32([
                    [0, 0],
                    [self.WARP, 0],
                    [self.WARP, self.WARP],
                    [0, self.WARP]
                ])

                self.H = cv2.getPerspectiveTransform(src, dst)

                self.build_sqdict()

                print("\nboard locked")
                print("press 'd' -> snapshot BEFORE move")
                print("move piece")
                print("press 'd' again -> detect move\n")

            if self.H is None:

                cv2.imshow("camera", vis)

                if cv2.waitKey(1) == 27:
                    break

                continue

            board = cv2.warpPerspective(frame, self.H, (self.WARP, self.WARP))

            gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)

            self.draw_grid(board)

            cv2.imshow("board", board)

            key = cv2.waitKey(1)

            # -----------------------
            # D KEY LOGIC (UNCHANGED)
            # -----------------------
            if key == ord('d'):

                if not self.awaiting_after:

                    self.before_frame = gray.copy()
                    self.awaiting_after = True
                    print("\nSnapshot BEFORE move")

                else:

                    after_frame = gray.copy()

                    diff = cv2.absdiff(self.before_frame, after_frame)
                    _, diff = cv2.threshold(diff, self.THRESH, 255, cv2.THRESH_BINARY)
                    diff = cv2.medianBlur(diff, 5)
                    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, np.ones((5, 5)))

                    results = []

                    for sq, poly in self.sqdict.items():

                        mask = np.zeros(diff.shape, np.uint8)
                        cv2.fillPoly(mask, [np.array(poly, np.int32)], 255)

                        val = cv2.countNonZero(cv2.bitwise_and(diff, mask))
                        results.append((sq, val))

                    results.sort(key=lambda x: x[1], reverse=True)

                    print("\nMovement ranking:")
                    for r in results[:6]:
                        print(r)

                    sq1 = results[0][0]
                    sq2 = results[1][0]

                    if self.move_index % 2 == 0:
                        from_sq = sq1
                        to_sq = sq2
                    else:
                        from_sq = sq1
                        to_sq = sq2

                    print("\nDetected move:", from_sq, "->", to_sq)

                    self.move_index += 1

                    cv2.imshow("diff", diff)

                    self.before_frame = after_frame
                    self.awaiting_after = False

                    # 🔥 Only this line added
                    success = self.move_callback(from_sq, to_sq)

                    if not success:
                        print("Resetting vision snapshot.")
                        self.awaiting_after = False

            if key == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()