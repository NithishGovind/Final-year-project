import serial
import time


class Manipulator:

    def __init__(self, port="COM3", baud=9600):

        self.ser = serial.Serial(port, baud)
        time.sleep(2)

        # HOME position
        self.HOME = (90, 120, 140)

        # Chessboard angle map
        self.chess_map = [
            [(130,72,135),(120,75,145),(110,80,150),(98,84,152),(85,82,152),(70,80,148),(55,76,145),(42,72,140)],
            [(123,67,128),(115,73,135),(105,74,140),(95,75,140),(85,75,140),(70,72,138),(60,68,138),(50,68,138)],
            [(118,60,115),(110,64,120),(100,66,128),(95,68,130),(85,67,128),(75,68,128),(65,66,125),(58,60,120)],
            [(115,55,108),(110,60,112),(100,60,118),(95,62,118),(85,63,118),(75,63,118),(68,60,115),(58,58,110)],
            [(114,43,90),(105,56,105),(99,55,105),(92,56,105),(85,55,105),(79,55,102),(70,50,100),(65,50,95)],
            [(110,50,95),(105,45,82),(100,45,83),(90,48,90),(84,48,86),(78,48,88),(70,45,85),(65,45,80)],
            [(108,36,55),(102,40,65),(96,40,65),(90,42,72),(84,42,72),(79,42,72),(75,40,65),(68,38,60)],
            [(108,26,30),(105,24,25),(98,26,25),(93,32,40),(88,35,50),(80,40,50),(78,35,50),(70,32,50)]
        ]

    # -----------------------
    # LOW LEVEL SEND
    # -----------------------
    def send(self, cmd):
        self.ser.write((cmd + "\n").encode())
        time.sleep(0.05)

    # -----------------------
    # MOTION LOGIC
    # -----------------------
    def move_normal(self, s0, s1, s2):

        self.send(f"0,{s0}")
        time.sleep(2)

        self.send(f"2,{s2}")
        time.sleep(2)

        self.send(f"1,{s1}")
        time.sleep(2)

    def move_lift(self, s0, s1, s2):

        self.send(f"1,{s1}")
        time.sleep(2)

        self.send(f"2,{s2}")
        time.sleep(2)

        self.send(f"0,{s0}")
        time.sleep(2)

    # -----------------------
    # HELPERS
    # -----------------------
    def square_to_index(self, square):
        col = ord(square[0]) - ord('a')
        row = int(square[1]) - 1
        return row, col

    def get_angles(self, square):
        r, c = self.square_to_index(square)
        return self.chess_map[r][c]

    # -----------------------
    # BASIC ACTIONS
    # -----------------------
    def go_home(self):
        self.move_lift(*self.HOME)

    def move_to(self, square):
        angles = self.get_angles(square)
        self.move_normal(*angles)

    def magnet_on(self):
        self.send("on")
        time.sleep(1)

    def magnet_off(self):
        self.send("off")
        time.sleep(1)

    # -----------------------
    # HIGH LEVEL ACTIONS
    # -----------------------
    def pick(self, square):

        self.move_to(square)
        self.magnet_on()
        self.go_home()

    def place(self, square):

        self.move_to(square)
        self.magnet_off()
        self.go_home()

    def execute_move(self, from_sq, to_sq):

        print(f"Executing move: {from_sq} -> {to_sq}")

        self.pick(from_sq)
        self.place(to_sq)

    # -----------------------
    # OPTIONAL: CAPTURE HANDLING
    # -----------------------
    def capture_piece(self, square, dump_square="h8"):

        # remove opponent piece first
        self.pick(square)
        self.place(dump_square)

    # -----------------------
    # CLEANUP
    # -----------------------
    def close(self):
        self.ser.close()