import cv2
import numpy as np

CAM_INDEX = 0
WARP = 800
THRESH = 35

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
# MOVE DETECTION
# -----------------------
def detect_move(before, after):

    diff = cv2.absdiff(before, after)

    _, diff = cv2.threshold(diff, THRESH, 255, cv2.THRESH_BINARY)

    diff = cv2.dilate(diff, None, iterations=2)

    results = []

    for sq, poly in sqdict.items():

        mask = np.zeros(diff.shape, np.uint8)
        cv2.fillPoly(mask, [np.array(poly, np.int32)], 255)

        val = cv2.countNonZero(cv2.bitwise_and(diff, mask))

        results.append((sq, val))

    results.sort(key=lambda x: x[1], reverse=True)

    return results[:4], diff


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

            diff = cv2.absdiff(before_frame, after_frame)

            _, diff = cv2.threshold(diff, THRESH, 255, cv2.THRESH_BINARY)

            diff = cv2.medianBlur(diff,5)
            diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, np.ones((5,5)))

            results = []

            for sq, poly in sqdict.items():

                mask = np.zeros(diff.shape,np.uint8)
                cv2.fillPoly(mask,[np.array(poly,np.int32)],255)

                val = cv2.countNonZero(cv2.bitwise_and(diff,mask))

                results.append((sq,val))

            results.sort(key=lambda x:x[1], reverse=True)

            print("\nMovement ranking:")
            for r in results[:6]:
                print(r)

            move = [results[0][0], results[1][0]]

            print("\nDetected move:", move)

            cv2.imshow("diff", diff)

            before_frame = after_frame
            awaiting_after = False


    if key == 27:
        break


cap.release()
cv2.destroyAllWindows()