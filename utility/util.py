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


def rotator_to_matrix(obj):
    r = obj.rotation
    CR = math.cos(r.z)
    SR = math.sin(r.z)
    CP = math.cos(r.x)
    SP = math.sin(r.x)
    CY = math.cos(r.y)
    SY = math.sin(r.y)

    matrix = list()
    matrix.append(Vector3(CP*CY, CP*SY, SP))
    matrix.append(Vector3(CY*SP*SR - CR*SY, SY*SP*SR + CR*CY, -CP*SR))
    matrix.append(Vector3(-CR*CY*SP - SR*SY, -CR*SY*SP + SR*CY, CP*CR))

    return matrix