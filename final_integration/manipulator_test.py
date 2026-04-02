from manipulator import Manipulator
import serial.tools.list_ports


# -----------------------
# AUTO-DETECT ARDUINO PORT
# -----------------------
def find_arduino_port():
    ports = list(serial.tools.list_ports.comports())

    for port in ports:
        # Detect common Arduino identifiers
        if (
            "Arduino" in port.description
            or "ttyACM" in port.device
            or "ttyUSB" in port.device
        ):
            print(f"Auto-detected Arduino on {port.device}")
            return port.device

    return None


# -----------------------
# MANUAL PORT SELECTION
# -----------------------
def choose_port():
    ports = list(serial.tools.list_ports.comports())

    if not ports:
        raise Exception("No serial ports found. Is Arduino connected?")

    print("\nAvailable ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} ({port.description})")

    idx = int(input("Select port number: "))
    return ports[idx].device


# -----------------------
# MAIN PROGRAM
# -----------------------
def main():

    # Try auto-detection first
    port = find_arduino_port()

    # If not found, ask user
    if port is None:
        print("Arduino not auto-detected.")
        port = choose_port()

    robot = Manipulator(port=port)

    print("\nControls:")
    print("1 → Go HOME")
    print("2 → Move to square")
    print("3 → Pick from square")
    print("4 → Place to square")
    print("5 → Full move (from → to)")
    print("6 → Capture test")
    print("q → Quit")

    while True:

        cmd = input("\nEnter command: ").strip()

        try:
            # -----------------------
            # HOME
            # -----------------------
            if cmd == "1":
                robot.go_home()

            # -----------------------
            # MOVE TO SQUARE
            # -----------------------
            elif cmd == "2":
                sq = input("Square: ").strip()
                robot.move_to(sq)

            # -----------------------
            # PICK
            # -----------------------
            elif cmd == "3":
                sq = input("Pick from: ").strip()
                robot.pick(sq)

            # -----------------------
            # PLACE
            # -----------------------
            elif cmd == "4":
                sq = input("Place to: ").strip()
                robot.place(sq)

            # -----------------------
            # FULL MOVE
            # -----------------------
            elif cmd == "5":
                from_sq = input("From: ").strip()
                to_sq = input("To: ").strip()
                robot.execute_move(from_sq, to_sq)

            # -----------------------
            # CAPTURE TEST
            # -----------------------
            elif cmd == "6":
                sq = input("Capture square: ").strip()
                robot.capture_piece(sq)

            elif cmd.lower() == "q":
                print("Exiting...")
                break

            else:
                print("Invalid command")

        except Exception as e:
            print(f"Error: {e}")

    robot.close()


# -----------------------
# ENTRY POINT
# -----------------------
if __name__ == "__main__":
    main()