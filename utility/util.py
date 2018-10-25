import math

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Obj:
    def __init__(self):
        self.pos = Vector3(0, 0, 0)
        self.velocity = Vector3(0, 0, 0)
        self.rotation = Vector3(0, 0, 0)
        self.rvel = Vector3(0, 0, 0)

        self.lpos = Vector3(0, 0, 0)

        self.isBall = False