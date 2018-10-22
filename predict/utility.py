import math


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
        self.location = Vector3([0, 0, 0])
        self.velocity = Vector3([0, 0, 0])
        self.rotation = Vector3([0, 0, 0])
        self.rvelocity = Vector3([0, 0, 0])

        self.local_location = Vector3([0, 0, 0])
