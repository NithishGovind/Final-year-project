import cv2
import numpy as np
from statistics import median

cap = cv2.VideoCapture(3)

reference = None
prev_board = None


# -----------------------------
# Line preprocessing
# -----------------------------

def prepare(lines, kernel_close, kernel_open):
    _, lines = cv2.threshold(lines, 30, 255, cv2.THRESH_BINARY)
    lines = cv2.morphologyEx(lines, cv2.MORPH_CLOSE, kernel_close)
    lines = cv2.morphologyEx(lines, cv2.MORPH_OPEN, kernel_open)
    return lines


def prepare_vertical(lines):
    return prepare(lines, np.ones((3,1),np.uint8), np.ones((50,1),np.uint8))


def prepare_horizontal(lines):
    return prepare(lines, np.ones((1,3),np.uint8), np.ones((1,50),np.uint8))


# -----------------------------
# Board detection
# -----------------------------

def detect_board(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    kernelH = np.array([[-1,1]])
    kernelV = np.array([[-1],[1]])

    vertical = np.absolute(cv2.filter2D(gray.astype("float"), -1, kernelH))
    horizontal = np.absolute(cv2.filter2D(gray.astype("float"), -1, kernelV))

    vertical = prepare_vertical(vertical)
    horizontal = prepare_horizontal(horizontal)

    v_lines = cv2.HoughLinesP(vertical.astype(np.uint8),1,np.pi/180,100,minLineLength=100,maxLineGap=10)
    h_lines = cv2.HoughLinesP(horizontal.astype(np.uint8),1,np.pi/180,100,minLineLength=100,maxLineGap=10)

    if v_lines is None or h_lines is None:
        return None

    v_count = [0]*len(v_lines)
    h_count = [0]*len(h_lines)

    for i,v in enumerate(v_lines):
        x1,y1,x2,y2 = v[0]
        for j,h in enumerate(h_lines):
            x3,y3,x4,y4 = h[0]

            if ((x3 <= x1 <= x4) or (x4 <= x1 <= x3)) and ((y2 <= y3 <= y1) or (y1 <= y3 <= y2)):
                v_count[i]+=1
                h_count[j]+=1

    v_board = [v_lines[i] for i in range(len(v_lines)) if v_count[i] > 6]
    h_board = [h_lines[i] for i in range(len(h_lines)) if h_count[i] > 6]

    if not v_board or not h_board:
        return None

    y_min = int(median(min(v[0][1],v[0][3]) for v in v_board))
    y_max = int(median(max(v[0][1],v[0][3]) for v in v_board))
    x_min = int(median(min(h[0][0],h[0][2]) for h in h_board))
    x_max = int(median(max(h[0][0],h[0][2]) for h in h_board))

    board = gray[y_min:y_max, x_min:x_max]

    board = cv2.resize(board,(800,800))

    return board


# -----------------------------
# Square extraction
# -----------------------------

def extract_squares(board):

    squares = []

    for r in range(8):
        row = []
        for c in range(8):

            y1 = int(r*800/8)
            y2 = int((r+1)*800/8)

            x1 = int(c*800/8)
            x2 = int((c+1)*800/8)

            roi = board[y1:y2, x1:x2]

            roi = roi[5:-5,5:-5]
            roi = cv2.GaussianBlur(roi,(5,5),0)
            roi = cv2.resize(roi,(40,40))

            row.append(roi)

        squares.append(row)

    return squares


# -----------------------------
# Occupancy
# -----------------------------

def compute_board(curr, ref):

    board = np.zeros((8,8),dtype=int)

    for r in range(8):
        for c in range(8):

            diff = cv2.absdiff(curr[r][c], ref[r][c])
            score = np.mean(diff)

            if score > 20:
                board[r,c] = 1

    return board


# -----------------------------
# Move detection
# -----------------------------

def detect_move(prev, curr):

    src = None
    dst = None

    for r in range(8):
        for c in range(8):

            if prev[r,c]==1 and curr[r,c]==0:
                src=(r,c)

            if prev[r,c]==0 and curr[r,c]==1:
                dst=(r,c)

    return src,dst


# -----------------------------
# Main loop
# -----------------------------

while True:

    ret, frame = cap.read()
    if not ret:
        break

    board_img = detect_board(frame)

    if board_img is not None:

        cv2.imshow("board", board_img)

    cv2.imshow("camera", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    if key == ord('b') and board_img is not None:

        reference = extract_squares(board_img)
        print("Reference captured")

    if key == ord('u') and reference is not None:

        current = extract_squares(board_img)

        curr_board = compute_board(current, reference)

        if prev_board is None:
            prev_board = curr_board

        src,dst = detect_move(prev_board, curr_board)

        print(curr_board)

        if src and dst:
            print("Move:", src, "->", dst)

        prev_board = curr_board


cap.release()
cv2.destroyAllWindows()