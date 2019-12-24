import math

from utility.util import *


class Orientation:

    def __init__(self, rotation):
        self.yaw = float(rotation.yaw)
        self.roll = float(rotation.roll)
        self.pitch = float(rotation.pitch)

        cr = math.cos(self.roll)
        sr = math.sin(self.roll)
        cp = math.cos(self.pitch)
        sp = math.sin(self.pitch)
        cy = math.cos(self.yaw)
        sy = math.sin(self.yaw)

        self.forward = MyVec3(cp * cy, cp * sy, sp)  # y axis
        self.right = MyVec3(cy*sp*sr-cr*sy, sy*sp*sr+cr*cy, -cp*sr)  # -x axis
        self.up = MyVec3(-cr*cy*sp-sr*sy, -cr*sy*sp+sr*cy, cp*cr)  # z axis


def relative_location(center: MyVec3, ori: Orientation, target: MyVec3) -> MyVec3:
    # the following code works with the idea of dot product being a projection
    # first take the diff from the target and center
    # that vector dot x,y,z axis is the projection of that vector on that axis
    # in other words, it transforms the vector to the target vector coordinates

    x = (target - center).dot(ori.forward)
    y = (target - center).dot(ori.right)
    z = (target - center).dot(ori.up)
    return MyVec3(x, y, z)
