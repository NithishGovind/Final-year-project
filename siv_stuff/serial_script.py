import serial
import time

ser = serial.Serial("COM3", 9600)
time.sleep(2)

# ------------------------
HOME = (90, 120, 140)

holding = False   # 🔥 STATE

# ------------------------
chess_map = [
[(130,72,135),(120,75,145),(110,80,150),(98,84,152),(85,82,152),(70,80,148),(55,76,145),(42,72,140)],
[(123,67,128),(115,73,135),(105,74,140),(95,75,140),(85,75,140),(70,72,138),(60,68,138),(50,68,138)],
[(118,60,115),(110,64,120),(100,66,128),(95,68,130),(85,67,128),(75,68,128),(65,66,125),(58,60,120)],
[(115,55,108),(110,60,112),(100,60,118),(95,62,118),(85,63,118),(75,63,118),(68,60,115),(58,58,110)],
[(114,43,90),(105,56,105),(99,55,105),(92,56,105),(85,55,105),(79,55,102),(70,50,100),(65,50,95)],
[(110,50,95),(105,45,82),(100,45,83),(90,48,90),(84,48,86),(78,48,88),(70,45,85),(65,45,80)],
[(108,36,55),(102,40,65),(96,40,65),(90,42,72),(84,42,72),(79,42,72),(75,40,65),(68,38,60)],
[(108,26,30),(105,24,25),(98,26,25),(93,32,40),(88,35,50),(80,40,50),(78,35,50),(70,32,50)]
]

# ------------------------
def send(cmd):
    ser.write((cmd + "\n").encode())
    time.sleep(0.05)

# ------------------------
# NORMAL MOTION (0 → 2 → 1)
def move_normal(s0, s1, s2):

    print(f"Base → {s0}")
    send(f"0,{s0}")
    time.sleep(2)

    print(f"Elbow → {s2}")
    send(f"2,{s2}")
    time.sleep(2)

    print(f"Shoulder → {s1}")
    send(f"1,{s1}")
    time.sleep(2)

# ------------------------
# LIFT MOTION (1 → 2 → 0)
def move_lift(s0, s1, s2):

    print(f"Shoulder → {s1}")
    send(f"1,{s1}")
    time.sleep(2)

    print(f"Elbow → {s2}")
    send(f"2,{s2}")
    time.sleep(2)

    print(f"Base → {s0}")
    send(f"0,{s0}")
    time.sleep(2)

# ------------------------
def square_to_index(square):
    col = ord(square[0]) - ord('a')
    row = int(square[1]) - 1
    return row, col

# ------------------------
def go_home():
    print("\nGoing HOME")
    move_lift(*HOME)

# ------------------------
def go_to(square):
    r, c = square_to_index(square)
    s0, s1, s2 = chess_map[r][c]

    print(f"\nGoing to {square}")
    move_normal(s0, s1, s2)

# ------------------------
# 🔥 MAIN STATE MACHINE
# ------------------------
def handle_square(square):
    global holding

    if not holding:
        print(f"\nPICK from {square}")

        go_to(square)

        print("Magnet ON")
        send("on")
        time.sleep(1)

        go_home()

        holding = True

    else:
        print(f"\nPLACE at {square}")

        go_to(square)

        print("Magnet OFF")
        send("off")
        time.sleep(1)

        go_home()

        holding = False

# ------------------------
while True:

    cmd = input("\nEnter square: ")

    if cmd == "exit":
        break

    if len(cmd) == 2:
        handle_square(cmd)
    else:
        print("Invalid input")