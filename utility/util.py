import math

from utility.myVec3 import *


class Obj:
    # TODO clean up class/improve
    def __init__(self):
        self.pos = myVec3(0, 0, 0)
        self.velocity = myVec3(0, 0, 0)
        self.rotation = myVec3(0, 0, 0)
        self.rvel = myVec3(0, 0, 0)

        self.lpos = myVec3(0, 0, 0)

        self.isBall = False


def pre_process(packet, index):

    ret_obj = Obj()

    if index == -1:
        ret_obj.pos.x = packet.game_ball.physics.location.x
        ret_obj.pos.y = packet.game_ball.physics.location.y
        ret_obj.pos.z = packet.game_ball.physics.location.z

        ret_obj.velocity.x = packet.game_ball.physics.velocity.x
        ret_obj.velocity.y = packet.game_ball.physics.velocity.y
        ret_obj.velocity.z = packet.game_ball.physics.velocity.z

        ret_obj.rotation.x = packet.game_ball.physics.rotation.pitch
        ret_obj.rotation.y = packet.game_ball.physics.rotation.yaw
        ret_obj.rotation.z = packet.game_ball.physics.rotation.roll

        ret_obj.rvel.x = packet.game_ball.physics.angular_velocity.x
        ret_obj.rvel.y = packet.game_ball.physics.angular_velocity.y
        ret_obj.rvel.z = packet.game_ball.physics.angular_velocity.z
    else:
        ret_obj.pos.x = packet.game_cars[index].physics.location.x
        ret_obj.pos.y = packet.game_cars[index].physics.location.y
        ret_obj.pos.z = packet.game_cars[index].physics.location.z

        ret_obj.velocity.x = packet.game_cars[index].physics.velocity.x
        ret_obj.velocity.y = packet.game_cars[index].physics.velocity.y
        ret_obj.velocity.z = packet.game_cars[index].physics.velocity.z

        ret_obj.rotation.x = packet.game_cars[index].physics.rotation.pitch
        ret_obj.rotation.y = packet.game_cars[index].physics.rotation.yaw
        ret_obj.rotation.z = packet.game_cars[index].physics.rotation.roll

        ret_obj.rvel.x = packet.game_cars[index].physics.angular_velocity.x
        ret_obj.rvel.y = packet.game_cars[index].physics.angular_velocity.y
        ret_obj.rvel.z = packet.game_cars[index].physics.angular_velocity.z

    return ret_obj


# todo move to orinetation file
# TODO fix this ...
def to_local(our_obj, target_pos):
    x = (target_pos - our_obj.pos) * our_obj.matrix[0]
    y = (target_pos - our_obj.pos) * our_obj.matrix[1]
    z = (target_pos - our_obj.pos) * our_obj.matrix[2]
    return [x, y, z]


def vector_to_local(matrix, vector):
    return myVec3(vector.x*matrix[0].x + vector.y*matrix[1].x + vector.z*matrix[2].x,
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
    pitch_kp = 0.8
    pitch_kd = 20

    yaw_kp = 0.8
    yaw_kd = 20

    # error is angle between x-axis (front of car) and target vector
    angle_error = local_matrix[0].angle(target_vector)

    local_target = vector_to_local(local_matrix, target_vector)
    # yaw component, removing z-axis
    yaw_angle = myVec3(local_matrix[0].x, local_matrix[0].y, 0).angle(myVector3(local_target.x, local_target.y, 0))

    # pitch component, removing y-axis
    pitch_angle = myVec3(local_matrix[0].x, 0, local_matrix[0].z).angle(myVector3(local_target.x, 0, local_target.z))

    # yaw
    yaw = (yaw_kp * angle_error) + (yaw_kd * (angle_error - aim_to_vector.prev_yaw_error))
    aim_to_vector.prev_yaw_error = angle_error

    # pitch
    pitch = (pitch_kp * angle_error) + (pitch_kd * (angle_error - aim_to_vector.prev_pitch_error))
    aim_to_vector.prev_pitch_error = angle_error

    #cross_vec = local_matrix[0].cross(target_vector)
    cross_vec = local_matrix[0].cross(local_target)  # TODO test with pitch

    # inverse yaw if needed TODO test, make better
    if (cross_vec.z <= 0 and local_matrix[2].z <= 0) or (cross_vec.z >= 0 and local_matrix[2].z >= 0):
        yaw = yaw
    else:
        yaw = -yaw

    # inverse pitch if needed
    if (cross_vec.y <= 0 and local_matrix[1].y <= 0) or (cross_vec.y >= 0 and local_matrix[1].y >= 0):
        pitch = -pitch

    if yaw > 1:
        yaw = 1
    elif yaw < -1:
        yaw = -1

    if pitch > 1:
        pitch = 1
    elif pitch < -1:
        pitch = -1

    return yaw, pitch


aim_to_vector.prev_yaw_error = 0
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
        yaw, pitch = aim_to_vector(local_matrix, myVector3(0, 0, 1))
    elif total_error < 0:  # TODO threshold for just aim to 0,0,1?
        yaw, pitch = aim_to_vector(local_matrix, myVector3(-1, 0, 2))  # TODO vector target
        print('Right')
    else:
        yaw, pitch = aim_to_vector(local_matrix, myVector3(1, 0, 2))  # TODO vector target
        print('Left')

    return yaw, pitch


move_to_pos.sas_pos_prev_error = 0
