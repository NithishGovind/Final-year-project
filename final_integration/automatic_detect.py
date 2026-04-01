import cv2
import numpy as np
import time

CAM_INDEX = 1
WARP = 800

STABLE_FRAMES = 10
FRAME_DELAY = 0.03

cap = cv2.VideoCapture(CAM_INDEX)

points = []
H = None
sqdict = {}

last_board = None
candidate_board = None
stable_count = 0


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

        if val < 100:
            board_state[sq] = 1
        else:
            board_state[sq] = 0

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

    if len(changed) == 2:

        sq1, sq2 = changed

        if prev_board[sq1] == 1 and curr_board[sq1] == 0:
            return sq1, sq2

        elif prev_board[sq2] == 1 and curr_board[sq2] == 0:
            return sq2, sq1

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
# MAIN LOOP (AUTO)
# -----------------------
while True:

    ret, frame = cap.read()
    if not ret:
        continue

    vis = frame.copy()

    for p in points:
        cv2.circle(vis, p, 5, (0, 0, 255), -1)

    # -----------------------
    # CALIBRATION
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

        print("\nBoard locked. Automatic detection started.")

    if H is None:
        cv2.imshow("camera", vis)
        if cv2.waitKey(1) == 27:
            break
        continue

    # -----------------------
    # PROCESS FRAME
    # -----------------------
    board = cv2.warpPerspective(frame, H, (WARP, WARP))

    gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    current_board = detect_board_state(gray)

    # -----------------------
    # INIT STATE
    # -----------------------
    if last_board is None:
        last_board = current_board
        continue

    # -----------------------
    # CHANGE DETECTION
    # -----------------------
    if current_board != last_board:

        if candidate_board is None:
            candidate_board = current_board
            stable_count = 1

        elif current_board == candidate_board:
            stable_count += 1
        else:
            candidate_board = current_board
            stable_count = 1

        # -----------------------
        # CONFIRM MOVE
        # -----------------------
        if stable_count >= STABLE_FRAMES:

            print("\nStable board detected")

            from_sq, to_sq = get_move(last_board, candidate_board)

            if from_sq and to_sq:
                print("Detected move:", from_sq, "->", to_sq)
                last_board = candidate_board
            else:
                print("Invalid / noisy detection")

            candidate_board = None
            stable_count = 0

    else:
        candidate_board = None
        stable_count = 0

    draw_grid(board)
    cv2.imshow("board", board)

    if cv2.waitKey(1) == 27:
        break

    time.sleep(FRAME_DELAY)


cap.release()
cv2.destroyAllWindows()