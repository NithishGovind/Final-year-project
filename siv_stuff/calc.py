import math

a2 = 12
a3 = 9
d1 = 2

def ik(x, y, z):
    theta1 = math.atan2(y, x)

    r = math.sqrt(x**2 + y**2)
    z_ = z - d1

    D = (r**2 + z_**2 - a2**2 - a3**2) / (2*a2*a3)

    theta3 = math.acos(D)

    theta2 = math.atan2(z_, r) - math.atan2(
        a3 * math.sin(theta3),
        a2 + a3 * math.cos(theta3)
    )

    return (
        math.degrees(theta1),
        math.degrees(theta2),
        math.degrees(theta3)
    )
