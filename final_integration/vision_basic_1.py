
#source/destination classification

import cv2
import numpy as np

CAM_INDEX = 0
WARP = 800
THRESH_DELTA = 15

cap = cv2.VideoCapture(CAM_INDEX)

points = []
H = None
sqdict = {}

before_frame = None
awaiting_after = False
move_index = 0


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
# MOVE DETECTION (FIXED)
# -----------------------
def detect_move(before_frame, after_frame):

    sources = []
    destinations = []

    for sq, poly in sqdict.items():

        before = square_mean(before_frame, poly)
        after = square_mean(after_frame, poly)

        delta = after - before

        # ignore noise
        if abs(delta) < THRESH_DELTA:
            continue

        if delta > 0:
            sources.append((sq, delta))       # piece removed
        else:
            destinations.append((sq, delta))  # piece placed

    print("\nSources:", sources)
    print("Destinations:", destinations)

    # -----------------------
    # NORMAL MOVE / CAPTURE
    # -----------------------
    if len(sources) == 1 and len(destinations) == 1:
        return sources[0][0], destinations[0][0]

    # -----------------------
    # CASTLING
    # -----------------------
    if len(sources) == 2 and len(destinations) == 2:

        pairs = []

        for s, _ in sources:
            for d, _ in destinations:
                dist = abs(ord(s[0]) - ord(d[0]))
                pairs.append((dist, s, d))

        pairs.sort(reverse=True)

        king_move = pairs[0]
        rook_move = pairs[1]

        print("Castling detected")
        print("King:", king_move[1], "->", king_move[2])
        print("Rook:", rook_move[1], "->", rook_move[2])

        return king_move[1], king_move[2]

    print("Detection failed / noisy frame")
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

    # LOCK BOARD
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
        print("Press 'd' -> BEFORE move")
        print("Make move")
        print("Press 'd' -> AFTER move\n")

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
            awaiting_after = True
            print("\nCaptured BEFORE")

        else:
            after_frame = gray.copy()

            from_sq, to_sq = detect_move(before_frame, after_frame)

            if from_sq and to_sq:
                print("\nDetected move:", from_sq, "->", to_sq)

            before_frame = after_frame
            awaiting_after = False

    if key == 27:
        break


cap.release()
cv2.destroyAllWindows()