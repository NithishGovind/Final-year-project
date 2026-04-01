import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# DH PARAMETERS
# -----------------------------
a = [9.5, 12, 9, 3, 6.5]
alpha = [0, -np.pi/2, 0, np.pi/2, -np.pi/2]
d = [0, 2, 2, 1.8, 1]

# -----------------------------
# DH TRANSFORMATION
# -----------------------------
def dh_transform(a, alpha, d, theta):
    return np.array([
        [np.cos(theta), -np.sin(theta)*np.cos(alpha),  np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
        [np.sin(theta),  np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
        [0,              np.sin(alpha),               np.cos(alpha),               d],
        [0,              0,                           0,                           1]
    ])

# -----------------------------
# FORWARD KINEMATICS
# -----------------------------
def forward_kinematics(thetas):
    T = np.eye(4)
    positions = [T[:3, 3]]

    for i in range(5):
        T = T @ dh_transform(a[i], alpha[i], d[i], thetas[i])
        positions.append(T[:3, 3])

    return np.array(positions), T

# -----------------------------
# SIMPLE IK (NUMERICAL)
# -----------------------------
def inverse_kinematics(target, initial_guess):
    theta = initial_guess.copy()

    for _ in range(200):
        pos, _ = forward_kinematics(theta)
        ee = pos[-1]

        error = target - ee
        if np.linalg.norm(error) < 0.01:
            break

        # Jacobian (finite difference)
        J = np.zeros((3, 5))
        delta = 1e-4

        for i in range(5):
            temp = theta.copy()
            temp[i] += delta
            pos_d, _ = forward_kinematics(temp)
            J[:, i] = (pos_d[-1] - ee) / delta

        # Pseudo-inverse update
        theta += np.linalg.pinv(J) @ error

    return theta

# -----------------------------
# STRAIGHT LINE TRAJECTORY
# -----------------------------
start = np.array([10, 5, 5])
end   = np.array([20, 10, 10])

steps = 50
trajectory = np.linspace(start, end, steps)

# -----------------------------
# SIMULATION
# -----------------------------
theta = np.zeros(5)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for point in trajectory:
    theta = inverse_kinematics(point, theta)
    positions, _ = forward_kinematics(theta)

    ax.cla()
    ax.plot(positions[:,0], positions[:,1], positions[:,2], '-o')

    # draw desired path
    ax.plot(trajectory[:,0], trajectory[:,1], trajectory[:,2], 'r--')

    ax.set_xlim([0, 30])
    ax.set_ylim([0, 30])
    ax.set_zlim([0, 30])

    plt.pause(0.05)

plt.show()