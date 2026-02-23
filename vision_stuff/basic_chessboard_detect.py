import cv2
import numpy as np

# -----------------------------
# PARAMETERS
# -----------------------------
PATTERN_SIZE = (7, 7)   # internal corners for 8x8 board
BOARD_SIZE = 800        # warped board size (pixels)

# -----------------------------
# Initialize webcam
# -----------------------------
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Cannot open webcam")
    exit()

homography_computed = False
M = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if not homography_computed:
        ret_cb, corners = cv2.findChessboardCorners(gray, PATTERN_SIZE)

        if ret_cb:
            corners = cv2.cornerSubPix(
                gray,
                corners,
                winSize=(11, 11),
                zeroZone=(-1, -1),
                criteria=(
                    cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER,
                    30,
                    0.001
                )
            )

            corners = corners.reshape(7, 7, 2)

            # Get inner extreme corners
            tl = corners[0, 0]
            tr = corners[0, 6]
            bl = corners[6, 0]
            br = corners[6, 6]

            # Compute one square vector horizontally and vertically
            vec_h = (corners[0, 1] - corners[0, 0])
            vec_v = (corners[1, 0] - corners[0, 0])

            # Expand outward
            top_left = tl - vec_h - vec_v
            top_right = tr + vec_h - vec_v
            bottom_left = bl - vec_h + vec_v
            bottom_right = br + vec_h + vec_v

            src_pts = np.array([
                top_left,
                top_right,
                bottom_left,
                bottom_right
            ], dtype="float32")

            dst_pts = np.array([
                [0, 0],
                [BOARD_SIZE - 1, 0],
                [0, BOARD_SIZE - 1],
                [BOARD_SIZE - 1, BOARD_SIZE - 1]
            ], dtype="float32")

            M = cv2.getPerspectiveTransform(src_pts, dst_pts)
            homography_computed = True
            print("Homography locked. Press 'r' to reset.")

        cv2.imshow("Live Feed - Searching Board", frame)

    else:
        warped = cv2.warpPerspective(frame, M, (BOARD_SIZE, BOARD_SIZE))

        square_size = BOARD_SIZE // 8

        # Draw grid
        for i in range(9):
            # Vertical lines
            cv2.line(
                warped,
                (i * square_size, 0),
                (i * square_size, BOARD_SIZE),
                (0, 255, 0),
                2
            )

            # Horizontal lines
            cv2.line(
                warped,
                (0, i * square_size),
                (BOARD_SIZE, i * square_size),
                (0, 255, 0),
                2
            )

        cv2.imshow("Warped Board with Grid", warped)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    if key == ord('r'):
        homography_computed = False
        print("Resetting homography...")

cap.release()
cv2.destroyAllWindows()