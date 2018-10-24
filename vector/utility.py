import math

G = -650
DRAG = -(3/100)
BALL_RADIUS = 92.75

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


class obj:
    def __init__(self):
        self.pos = Vector3([0, 0, 0])
        self.velocity = Vector3([0, 0, 0])
        self.rotation = Vector3([0, 0, 0])
        self.rvelocity = Vector3([0, 0, 0])

        self.lpos = Vector3([0, 0, 0])


def time_to_ground(ball):
    u = ball.velocity.data[2]
    s = ball.pos.data[2] - BALL_RADIUS
    root = u**2 - 2*G*s

    if root < 0:
        return 0
    else:
        return (-u-math.sqrt(root))/G


def pos_at_time(ball, t):
    vx = ball.velocity.data[0]
    vy = ball.velocity.data[1]

    return [(vx*t + 0.5*DRAG*vx*t**2) + ball.pos.data[0],
            (vy*t + 0.5*DRAG*vx*t**2) + ball.pos.data[1],
            0]
