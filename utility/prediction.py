import math
from utility.myVec3 import MyVec3
from rlbot.utils.game_state_util import Physics

# ref: https://github.com/RLBot/RLBot/wiki/Useful-Game-Values
G = -650
DRAG = 3/100
BALL_RADIUS = 92.75
CAR_HEIGHT = 17.01  # octane
BOOST_ACC = 430 #TODO fix this
FPS = 60

# TODO rename these?
A = G/DRAG
DECAY = -DRAG/FPS
B = math.log(1-DRAG) / FPS

Y = 2.0
mu = 0.285
C_R = 0.6
F = 0.0003


# Following functions are based on frame number (f)
def d_get_vel_z(f, initial_velocity_z):
    return ((initial_velocity_z - A) * math.e**(DECAY*f)) + A


def d_get_pos_z(f, initial_velocity_z, initial_pos_z):
    c = (initial_velocity_z - A) / -DECAY
    return initial_pos_z + (((((initial_velocity_z - A) * math.e**(DECAY*f)) / DECAY) + A*f + c) / FPS)


def d_get_vel_x(f, initial_velocity_x):
    return initial_velocity_x * (1-DRAG)**(f / FPS)


def d_get_vel_y(f, initial_velocity_y):
    return d_get_vel_x(f, initial_velocity_y)


def d_get_pos_x(f, initial_velocity_x, initial_pos_x):
    return initial_pos_x + ((((initial_velocity_x * (1 - DRAG)**(f/FPS)) / B) - (initial_velocity_x / B)) / FPS)


def d_get_pos_y(f, initial_velocity_y, initial_pos_y):
    return d_get_pos_x(f, initial_velocity_y, initial_pos_y)


def time_to_ground(velocity: MyVec3, position: MyVec3, is_ball=True):
    u = velocity.z

    if is_ball:
        offset = -BALL_RADIUS
    else:
        offset = -CAR_HEIGHT

    s = position.z + offset
    root = u**2 - 2*G*s

    if root < 0:
        return 0
    else:
        return (-u - math.sqrt(root)) / G


def get_pos_at_time(velocity: MyVec3, position: MyVec3, t):
    vx = velocity.x
    vy = velocity.y
    vz = velocity.z

    x = position.x
    y = position.y
    z = position.z

    return MyVec3((vx*t + 0.5*vx*t**2) + x,
            (vy*t + 0.5*vx*t**2) + y,
            (vz*t + 0.5*G*t**2) + z)


def get_vel_z(t, initial_velocity_z):
    return initial_velocity_z + G*t


def update_physics_after_bounce(physics: Physics, time_ground, ground_pos):
    ret_physics = Physics()

    vz = get_vel_z(time_ground, physics.velocity.z)
    ground_velocity = MyVec3(physics.velocity.x,
                             physics.velocity.y,
                             vz)

    normal = MyVec3(0, 0, 1)  # TODO assume ground bounces for now
    vel_perp = normal.dot(ground_velocity) * normal  # velocity projection on normal vector
    vel_para = ground_velocity - vel_perp  # vector subtraction to get parallel vector
    vel_spin = BALL_RADIUS * normal.cross(physics.angular_velocity)  # spin velocity is perp to normal and axis of ang v
    vel_slip = vel_para + vel_spin

    ratio = vel_perp.mag() / vel_slip.mag()

    delta_vel_perp = - (1 + C_R) * vel_perp
    delta_vel_para = - min(1, Y * ratio) * mu * vel_slip

    ret_physics.location = ground_pos
    ret_physics.velocity = ground_velocity + delta_vel_perp + delta_vel_para
    ret_physics.angular_velocity = physics.angular_velocity + (F * BALL_RADIUS * delta_vel_para.cross(normal))

    return ret_physics


def get_bounces(physics: Physics, bounce_num=5, samples=15):
    positions = []
    times = []
    current_physics = physics
    initial_velocity = current_physics.velocity
    initial_position = current_physics.location
    last_time = 0
    for b in range(bounce_num):
        time_ground = time_to_ground(initial_velocity, initial_position)
        time_interval = (time_ground / samples)
        current_pos = None

        for s in range(0, samples + 1):
            t = s * time_interval
            current_pos = get_pos_at_time(initial_velocity, initial_position, t)
            positions.append(current_pos)
            times.append(last_time + t)

        new_physics = update_physics_after_bounce(current_physics, time_ground, current_pos)

        initial_velocity = new_physics.velocity
        initial_position = new_physics.location
        current_physics = new_physics
        last_time = last_time + t

    return positions, times


def burn_time(obj, target_height): # TODO rename to like suicide burn
    u = obj.velocity.z
    s = obj.pos.z - target_height
    a = BOOST_ACC

    return (u - G*u/a + (math.sqrt(-2*a*G*s + a*u**2 + 2*s*G**2 - G*u**2)
            / math.sqrt(a))) / ((G**2)/a - G)


def burn_to_height(obj, target_height):
    u = obj.velocity.z
    s = obj.pos.z

    max_height = s - (u**2) / (2 * G)  # was G
    #print('max:' + str(max_height))

    return max_height < target_height
