import cv2
import numpy as np

CAM_INDEX = 1
WARP = 800

cap = cv2.VideoCapture(CAM_INDEX)

points = []
H = None
sqdict = {}

before_frame = None
prev_board = None
awaiting_after = False


# -----------------------
# MOUSE INPUT
# -----------------------
def mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
        points.append((x, y))
        print("point", len(points), x, y)


cv2.namedWindow("camera")
cv2.setMouseCallback("camera", mouse)


# -----------------------
# BUILD BOARD GRID
# -----------------------
def build_sqdict():
    files = "abcdefgh"
    ranks = "87654321"
    cell = WARP // 8

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
            sqdict[name] = poly


def draw_grid(img):
    cell = WARP // 8
    for i in range(1, 8):
        cv2.line(img, (0, i * cell), (WARP, i * cell), (0, 255, 0), 1)
        cv2.line(img, (i * cell, 0), (i * cell, WARP), (0, 255, 0), 1)


# -----------------------
# HELPER
# -----------------------
def square_mean(img, poly):
    mask = np.zeros(img.shape, np.uint8)
    cv2.fillPoly(mask, [np.array(poly, np.int32)], 255)
    return cv2.mean(img, mask=mask)[0]


# -----------------------
# BOARD STATE DETECTION
# -----------------------
def detect_board_state(gray):

    board_state = {}

    for sq, poly in sqdict.items():

        val = square_mean(gray, poly)

        # YOU MUST TUNE THIS
        if val < 100:
            board_state[sq] = 1  # occupied
        else:
            board_state[sq] = 0  # empty

    return board_state


# -----------------------
# MOVE EXTRACTION
# -----------------------
def get_move(prev_board, curr_board):

    changed = []

    for sq in prev_board:
        if prev_board[sq] != curr_board[sq]:
            changed.append(sq)

    print("\nChanged squares:", changed)

    # -----------------------
    # NORMAL MOVE / CAPTURE
    # -----------------------
    if len(changed) == 2:

        sq1, sq2 = changed

        if prev_board[sq1] == 1 and curr_board[sq1] == 0:
            return sq1, sq2

        elif prev_board[sq2] == 1 and curr_board[sq2] == 0:
            return sq2, sq1

    # -----------------------
    # CASTLING
    # -----------------------
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

    print("Invalid detection")
    return None, None


# -----------------------
# MAIN LOOP
# -----------------------
while True:

    ret, frame = cap.read()
    if not ret:
        continue

    vis = frame.copy()

    for p in points:
        cv2.circle(vis, p, 5, (0, 0, 255), -1)

    # -----------------------
    # LOCK BOARD
    # -----------------------
    if len(points) == 4 and H is None:

        src = np.float32(points)
        dst = np.float32([
            [0, 0],
            [WARP, 0],
            [WARP, WARP],
            [0, WARP]
        ])

        H = cv2.getPerspectiveTransform(src, dst)
        build_sqdict()

        print("\nBoard locked")
        print("Press 'd' → capture BEFORE")
        print("Make move")
        print("Press 'd' → capture AFTER\n")

    if H is None:
        cv2.imshow("camera", vis)
        if cv2.waitKey(1) == 27:
            break
        continue

    board = cv2.warpPerspective(frame, H, (WARP, WARP))

    gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    draw_grid(board)

    cv2.imshow("board", board)

    key = cv2.waitKey(1)

    # -----------------------
    # D KEY LOGIC
    # -----------------------
    if key == ord('d'):

        if not awaiting_after:

            before_frame = gray.copy()
            prev_board = detect_board_state(before_frame)

            awaiting_after = True
            print("\nCaptured BEFORE")

        else:

            after_frame = gray.copy()
            curr_board = detect_board_state(after_frame)

            from_sq, to_sq = get_move(prev_board, curr_board)

            if from_sq and to_sq:
                print("\nDetected move:", from_sq, "->", to_sq)

            else:
                print("Move detection failed")

            awaiting_after = False

    if key == 27:
        break


cap.release()
cv2.destroyAllWindows()