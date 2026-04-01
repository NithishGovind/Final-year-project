import math

# -----------------------------
# ROBOT PARAMETERS
# -----------------------------
a2 = 12
a3 = 9
d1 = 2

# -----------------------------
# BOARD PARAMETERS (TUNE THESE)
# -----------------------------
SQUARE = 2.5  # cm

x0 = 12.0     # a1 position
y0 = 8.0
theta = 0.1   # radians

# OPTIONAL: global correction (you WILL need this)
x_offset = 0.0
y_offset = 0.0

# -----------------------------
# CHESS MAP
# -----------------------------
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

# -----------------------------
# FORWARD KINEMATICS
# -----------------------------
def fk(theta1, theta2, theta3):
    t1 = math.radians(theta1)
    t2 = math.radians(theta2)
    t3 = math.radians(theta3)

    r = a2 * math.cos(t2) + a3 * math.cos(t2 + t3)

    x = math.cos(t1) * r
    y = math.sin(t1) * r
    z = d1 + a2 * math.sin(t2) + a3 * math.sin(t2 + t3)

    return x, y, z

# -----------------------------
# IDEAL BOARD POSITION
# -----------------------------
def square_to_xy(row, col):
    xr = col * SQUARE
    yr = row * SQUARE

    x = x0 + xr * math.cos(theta) - yr * math.sin(theta)
    y = y0 + xr * math.sin(theta) + yr * math.cos(theta)

    return x, y

# -----------------------------
# ANALYSIS
# -----------------------------
errors = []

print("\n===== DETAILED ANALYSIS =====\n")

for r in range(8):
    for c in range(8):
        t1, t2, t3 = chess_map[r][c]

        # FK
        x_fk, y_fk, z_fk = fk(t1, t2, t3)

        # Apply global offset correction
        x_fk += x_offset
        y_fk += y_offset

        # Ideal
        x_id, y_id = square_to_xy(r, c)

        # Error
        err = math.hypot(x_fk - x_id, y_fk - y_id)
        errors.append(err)

        print(f"[{r},{c}] FK=({x_fk:6.2f},{y_fk:6.2f}) | "
              f"ID=({x_id:6.2f},{y_id:6.2f}) | ERR={err:5.2f}")

# -----------------------------
# SUMMARY
# -----------------------------
avg_error = sum(errors) / len(errors)
max_error = max(errors)

print("\n===== SUMMARY =====")
print(f"Average error : {avg_error:.2f} cm")
print(f"Max error     : {max_error:.2f} cm")