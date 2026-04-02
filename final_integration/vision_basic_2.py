import cv2
import numpy as np

CAM_INDEX = 0
WARP = 800
THRESH = 25

cap = cv2.VideoCapture(CAM_INDEX)

points = []
H = None
sqdict = {}

before_frame = None
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
# HELPERS
# -----------------------
def square_mean(img, poly):
    mask = np.zeros(img.shape, np.uint8)
    cv2.fillPoly(mask, [np.array(poly, np.int32)], 255)
    return cv2.mean(img, mask=mask)[0]


def blob_to_squares(diff, sqdict, area_thresh=300):

    detected = []

    for sq, poly in sqdict.items():

        mask = np.zeros(diff.shape, np.uint8)
        cv2.fillPoly(mask, [np.array(poly, np.int32)], 255)

        overlap = cv2.countNonZero(cv2.bitwise_and(diff, mask))

        if overlap > area_thresh:
            detected.append((sq, overlap))

    return detected


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

        print("\nboard locked")
        print("press 'd' -> snapshot BEFORE move")
        print("move piece")
        print("press 'd' again -> detect move\n")

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
            print("\nSnapshot BEFORE move")

        else:

            after_frame = gray.copy()

            # DIFF
            diff = cv2.absdiff(before_frame, after_frame)
            _, diff = cv2.threshold(diff, THRESH, 255, cv2.THRESH_BINARY)

            # CLEANUP (fix your weak blobs)
            kernel = np.ones((7, 7), np.uint8)
            diff = cv2.morphologyEx(diff, cv2.MORPH_CLOSE, kernel)
            diff = cv2.dilate(diff, kernel, iterations=1)

            cv2.imshow("diff", diff)

            # -----------------------
            # OVERLAP-BASED DETECTION
            # -----------------------
            detected = blob_to_squares(diff, sqdict, area_thresh=300)

            print("Detected squares (overlap):", detected)

            if len(detected) < 2:
                print("Not enough movement")
                continue

            # sort by strongest overlap
            detected.sort(key=lambda x: x[1], reverse=True)

            # pick top 2
            squares = [detected[0][0], detected[1][0]]

            print("Chosen squares:", squares)

            # -----------------------
            # DIRECTION USING INTENSITY
            # -----------------------
            vals = {}

            for sq in squares:
                poly = sqdict[sq]

                before_mean = square_mean(before_frame, poly)
                after_mean  = square_mean(after_frame, poly)

                delta = after_mean - before_mean
                vals[sq] = delta

            from_sq = max(vals, key=vals.get)   # lighter
            to_sq   = min(vals, key=vals.get)   # darker

            print("\nDetected move:", from_sq, "->", to_sq)

            before_frame = after_frame
            awaiting_after = False

    if key == 27:
        break


cap.release()
cv2.destroyAllWindows()