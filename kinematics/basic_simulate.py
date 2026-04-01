import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# -----------------------------
# DH Transform
# -----------------------------
def dh(a, alpha, d, theta):
    return np.array([
        [np.cos(theta), -np.sin(theta)*np.cos(alpha),  np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
        [np.sin(theta),  np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
        [0,              np.sin(alpha),               np.cos(alpha),              d],
        [0,              0,                           0,                          1]
    ])

# -----------------------------
# Robot parameters
# -----------------------------
L1 = 0.4
L2 = 0.5
L3 = 0.4
L4 = 0.2
L5 = 0.15

def fk_all(q):
    q1, q2, q3, q4, q5 = q

    T1 = dh(0, np.pi/2, L1, q1)
    T2 = dh(L2, 0, 0, q2)
    T3 = dh(L3, 0, 0, q3)
    T4 = dh(L4, 0, 0, q4)
    T5 = dh(L5, 0, 0, q5)

    T01 = T1
    T02 = T01 @ T2
    T03 = T02 @ T3
    T04 = T03 @ T4
    T05 = T04 @ T5

    pts = np.array([
        [0,0,0],
        T01[:3,3],
        T02[:3,3],
        T03[:3,3],
        T04[:3,3],
        T05[:3,3]
    ])
    return pts

def fk(q):
    return fk_all(q)[-1]

# -----------------------------
# Numerical Jacobian
# -----------------------------
def jacobian(q, eps=1e-6):
    J = np.zeros((3, 5))
    f0 = fk(q)

    for i in range(5):
        dq = np.zeros(5)
        dq[i] = eps
        f1 = fk(q + dq)
        J[:, i] = (f1 - f0) / eps

    return J

# -----------------------------
# IK Line Path
# -----------------------------
def generate_motion(q_init, target, steps=150):
    q = q_init.copy()
    qs = []
    ee_traj = []

    start = fk(q)

    for s in np.linspace(0, 1, steps):
        xd = start + s * (target - start)
        x = fk(q)

        error = xd - x
        J = jacobian(q)

        J_pinv = np.linalg.pinv(J)
        dq = J_pinv @ error

        q += 0.4 * dq  # gain
        qs.append(q.copy())
        ee_traj.append(fk(q))

    return np.array(qs), np.array(ee_traj)
def generate_motion(q_init, target, obstacle_center, obstacle_radius, steps=150):

    q = q_init.copy()
    qs = []
    ee_traj = []

    start = fk(q)

    influence_dist = 0.4
    k_rep = 0.08

    for s in np.linspace(0, 1, steps):

        xd = start + s * (target - start)
        x = fk(q)

        # Straight-line velocity
        v_line = xd - x

        # -------------------------
        # Obstacle Avoidance
        # -------------------------
        vec = x - obstacle_center
        dist = np.linalg.norm(vec)

        v_avoid = np.zeros(3)

        if dist < influence_dist:
            dir_vec = vec / dist
            rep_mag = k_rep * (1/dist - 1/influence_dist) / (dist**2)
            v_avoid = rep_mag * dir_vec

        v_total = v_line + v_avoid

        J = jacobian(q)
        J_pinv = np.linalg.pinv(J)

        dq = J_pinv @ v_total

        q += 0.4 * dq
        qs.append(q.copy())
        ee_traj.append(fk(q))

    return np.array(qs), np.array(ee_traj)
# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":

    q0 = np.deg2rad([20, 30, -20, 10, 0])
    target = np.array([0.4, 0.3, 0.6])

    obstacle_center = np.array([0.3, 0.1, 0.5])
    obstacle_radius = 0.15

    qs, ee_traj = generate_motion(q0, target,
                                  obstacle_center,
                                  obstacle_radius)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(0, 1.5)

    # Draw obstacle
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    xs = obstacle_radius * np.cos(u)*np.sin(v) + obstacle_center[0]
    ys = obstacle_radius * np.sin(u)*np.sin(v) + obstacle_center[1]
    zs = obstacle_radius * np.cos(v) + obstacle_center[2]
    ax.plot_surface(xs, ys, zs, alpha=0.3)

    line, = ax.plot([], [], [], '-o', lw=3)
    path, = ax.plot([], [], [], 'r--', lw=1)

    def update(i):
        pts = fk_all(qs[i])

        line.set_data(pts[:,0], pts[:,1])
        line.set_3d_properties(pts[:,2])

        path.set_data(ee_traj[:i,0], ee_traj[:i,1])
        path.set_3d_properties(ee_traj[:i,2])

        return line, path

    ani = FuncAnimation(fig, update, frames=len(qs), interval=40)

    plt.show()