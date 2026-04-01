from manipulator import Manipulator


def main():

    robot = Manipulator(port="COM3")

    print("\nControls:")
    print("1 → Go HOME")
    print("2 → Move to square")
    print("3 → Pick from square")
    print("4 → Place to square")
    print("5 → Full move (from → to)")
    print("6 → Capture test")
    print("q → Quit")

    while True:

        cmd = input("\nEnter command: ")

        # -----------------------
        # HOME
        # -----------------------
        if cmd == "1":
            robot.go_home()

        # -----------------------
        # MOVE TO SQUARE
        # -----------------------
        elif cmd == "2":
            sq = input("Square: ")
            robot.move_to(sq)

        # -----------------------
        # PICK
        # -----------------------
        elif cmd == "3":
            sq = input("Pick from: ")
            robot.pick(sq)

        # -----------------------
        # PLACE
        # -----------------------
        elif cmd == "4":
            sq = input("Place to: ")
            robot.place(sq)

        # -----------------------
        # FULL MOVE
        # -----------------------
        elif cmd == "5":
            from_sq = input("From: ")
            to_sq = input("To: ")
            robot.execute_move(from_sq, to_sq)

        # -----------------------
        # CAPTURE TEST
        # -----------------------
        elif cmd == "6":
            sq = input("Capture square: ")
            robot.capture_piece(sq)

        elif cmd == "q":
            break

        else:
            print("Invalid command")

    robot.close()


if __name__ == "__main__":
    main()