import math

G = -650
DRAG = -(3/100)
BALL_RADIUS = 92.75
CAR_HEIGHT = 16.5

def time_to_ground(obj):
    u = obj.velocity.z

    if obj.isBall:
        offset = -BALL_RADIUS
    else:
        offset = -CAR_HEIGHT

    s = obj.pos.z + offset
    root = u**2 - 2*G*s

    if root < 0:
        return 0
    else:
        return (-u-math.sqrt(root))/G


def pos_at_time(obj, t):
    vx = obj.velocity.x
    vy = obj.velocity.y
    vz = obj.velocity.z

    return [(vx*t + 0.5*DRAG*vx*t**2) + obj.pos.x,
            (vy*t + 0.5*DRAG*vx*t**2) + obj.pos.y,
            (vz*t + 0.5*G*t**2) + obj.pos.z]
