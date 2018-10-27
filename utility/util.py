import math


class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, value):
        return Vector3(self.x - value.x, self.y - value.y, self.z - value.z)

    def __add__(self, value):
        return Vector3(self.x + value.x, self.y + value.y, self.z + value.z)

    def __mul__(self, value):
        return Vector3(self.x * value.x, self.y * value.y, self.z * value.z)


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


def to_local(target_pos, our_obj):
    x = (target_pos - our_obj.pos) * our_obj.matrix[0]
    y = (target_pos - our_obj.pos) * our_obj.matrix[1]
    z = (target_pos - our_obj.pos) * our_obj.matrix[2]
    return Vector3(x, y, z)


def aim_front(our_obj, target_pos):
    local_target = to_local(target_pos, our_obj)
    angle = math.atan2(local_target.y, local_target.x)

    # steering
    sensitivity = 5
    if angle < math.radians(-sensitivity):
        steer = -1
    elif angle > math.radians(sensitivity):
        steer = 1
    else:
        steer = 0

    return steer
