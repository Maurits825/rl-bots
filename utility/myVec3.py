import math


class myVec3:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    # TODO double check funcs
    def __sub__(self, vector):
        return myVec3(self.x - vector.x, self.y - vector.y, self.z - vector.z)

    def __add__(self, vector):
        return myVec3(self.x + vector.x, self.y + vector.y, self.z + vector.z)

    def __mul__(self, vector):
        return myVec3(self.x * vector.x, self.y * vector.y, self.z * vector.z)

    def dot(self, vector):
        return (self.x * vector.x) + (self.y * vector.y) + (self.z * vector.z)

    def cross(self, vector):
        return myVec3(self.y*vector.z - self.z*vector.y, self.z*vector.x - self.x*vector.z, self.x*vector.y - self.y*vector.x)

    def mag(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def angle(self, vector):
        return math.acos(self.dot(vector) / (self.mag() * vector.mag()))
