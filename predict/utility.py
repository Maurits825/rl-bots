import math

G = -650
DRAG = -(3/100)
BALL_RADIUS = 92.75
CAR_HEIGHT = 16.5

class Vector3:
    def __init__(self, data):
        self.data = data

    def __sub__(self, value):
        return Vector3([self.data[0]-value.data[0],
                        self.data[1]-value.data[1],
                        self.data[2]-value.data[2]])

    def __mul__(self, value):
        return (self.data[0]*value.data[0] +
                self.data[1]*value.data[1] +
                self.data[2]*value.data[2])


class Obj:
    def __init__(self):
        self.pos = Vector3([0, 0, 0])
        self.velocity = Vector3([0, 0, 0])
        self.rotation = Vector3([0, 0, 0])
        self.rvel = Vector3([0, 0, 0])

        self.lpos = Vector3([0, 0, 0])

        self.isBall = False


def time_to_ground(obj):
    u = obj.velocity.data[2]

    if obj.isBall:
        offset = -BALL_RADIUS
    else:
        offset = -CAR_HEIGHT

    s = obj.pos.data[2] + offset
    root = u**2 - 2*G*s

    if root < 0:
        return 0
    else:
        return (-u-math.sqrt(root))/G


def pos_at_time(obj, t):
    vx = obj.velocity.data[0]
    vy = obj.velocity.data[1]
    vz = obj.velocity.data[2]

    return [(vx*t + 0.5*DRAG*vx*t**2) + obj.pos.data[0],
            (vy*t + 0.5*DRAG*vx*t**2) + obj.pos.data[1],
            (vz*t + 0.5*G*t**2) + obj.pos.data[2]]
