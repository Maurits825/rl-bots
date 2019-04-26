import math


class myVector3:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __sub__(self, vector):
        return myVector3(self.x - vector.x, self.y - vector.y, self.z - vector.z)

    def __add__(self, vector):
        return myVector3(self.x + vector.x, self.y + vector.y, self.z + vector.z)

    def __mul__(self, vector):
        return myVector3(self.x * vector.x, self.y * vector.y, self.z * vector.z)

    def dot(self, vector):
        return (self.x * vector.x) + (self.y * vector.y) + (self.z * vector.z)

    def cross(self, vector):
        return myVector3(self.y*vector.z - self.z*vector.y, self.z*vector.x - self.x*vector.z, self.x*vector.y - self.y*vector.x)

    def mag(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def angle(self, vector):
        return math.acos(self.dot(vector) / (self.mag() * vector.mag()))


class Obj:
    def __init__(self):
        self.pos = myVector3(0, 0, 0)
        self.velocity = myVector3(0, 0, 0)
        self.rotation = myVector3(0, 0, 0)
        self.rvel = myVector3(0, 0, 0)

        self.lpos = myVector3(0, 0, 0)

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
    matrix.append(myVector3(CP*CY, CP*SY, SP))
    matrix.append(myVector3(CY*SP*SR - CR*SY, SY*SP*SR + CR*CY, -CP*SR))
    matrix.append(myVector3(-CR*CY*SP - SR*SY, -CR*SY*SP + SR*CY, CP*CR))

    return matrix

# TODO fix this ...
def to_local(our_obj, target_pos):
    x = (target_pos - our_obj.pos) * our_obj.matrix[0]
    y = (target_pos - our_obj.pos) * our_obj.matrix[1]
    z = (target_pos - our_obj.pos) * our_obj.matrix[2]
    return [x, y, z]


def vector_to_local(matrix, vector):
    return myVector3(vector.x*matrix[0].x + vector.y*matrix[1].x + vector.z*matrix[2].x,
                     vector.x*matrix[0].y + vector.y*matrix[1].y + vector.z*matrix[2].y,
                     vector.x*matrix[0].z + vector.y*matrix[1].z + vector.z*matrix[2].z)


def aim_front(our_obj, target_pos):
    #local_target = to_local(our_obj, target_pos)
    #angle = math.atan2(local_target[0].y, local_target[0].x)

    angle = math.atan2(target_pos.y - our_obj.pos.y,
                       target_pos.x - our_obj.pos.x)

    angle = angle - our_obj.rotation.y

    # steering
    sensitivity = 5
    if angle < math.radians(-sensitivity):
        steer = -1
    elif angle > math.radians(sensitivity):
        steer = 1
    else:
        steer = 0

    return steer



# TODO make this a class? handle init of prev error
def aim_to_vector(local_matrix, target_vector):  #TODO only implement pitch for now
    kp = 0.8
    kd = 20

    # error is angle between x-axis and target vector
    pitch_error = local_matrix[0].angle(target_vector)

    # P and D
    p = kp * pitch_error
    d = kd * (pitch_error - aim_to_vector.prev_pitch_error)
    aim_to_vector.prev_pitch_error = pitch_error

    pitch = p + d
    # inverse pitch if needed
    cross_vec = local_matrix[0].cross(target_vector)
    if (cross_vec.y <= 0 and local_matrix[1].y <= 0) or (cross_vec.y >= 0 and local_matrix[1].y >= 0):
        pitch = -pitch

    if pitch > 1:
        pitch = 1
    elif pitch < -1:
        pitch = -1

    return pitch


aim_to_vector.prev_pitch_error = 0


def move_to_pos(local_matrix, car, target_pos):  # TODO only implement pitch for now, add matrix to Obj class?
    kp = 0.5
    kd = 70
    pos_error = target_pos.x - car.pos.x
    #print(pos_error)

    # P and D
    p = kp * pos_error
    d = kd * (pos_error - move_to_pos.sas_pos_prev_error)
    move_to_pos.sas_pos_prev_error = pos_error

    total_error = p + d
    err_threshold = 50
    if False and abs(total_error) < err_threshold:  # TODO error threshold
        pitch = aim_to_vector(local_matrix, myVector3(0, 0, 1))
    elif total_error < 0:  # TODO threshold for just aim to 0,0,1?
        pitch = aim_to_vector(local_matrix, myVector3(-1, 0, 2))  # TODO vector target
    else:
        pitch = aim_to_vector(local_matrix, myVector3(1, 0, 2))  # TODO vector target

    return pitch


move_to_pos.sas_pos_prev_error = 0
