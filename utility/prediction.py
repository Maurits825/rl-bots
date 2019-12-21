import math
from utility.myVec3 import MyVec3

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


# Following functions are based on frame number (f)
def get_vel_z(f, initial_velocity_z):
    return ((initial_velocity_z - A) * math.e**(DECAY*f)) + A


def get_pos_z(f, initial_velocity_z, initial_pos_z):
    c = (initial_velocity_z - A) / -DECAY
    return initial_pos_z + (((((initial_velocity_z - A) * math.e**(DECAY*f)) / DECAY) + A*f + c) / FPS)


def get_vel_x(f, initial_velocity_x):
    return initial_velocity_x * (1-DRAG)**(f / FPS)


def get_vel_y(f, initial_velocity_y):
    return get_vel_x(f, initial_velocity_y)


def get_pos_x(f, initial_velocity_x, initial_pos_x):
    return initial_pos_x + ((((initial_velocity_x * (1 - DRAG)**(f/FPS)) / B) - (initial_velocity_x / B)) / FPS)


def get_pos_y(f, initial_velocity_y, initial_pos_y):
    return get_pos_x(f, initial_velocity_y, initial_pos_y)


def time_to_ground(obj):
    u = obj.velocity.z

    if obj.isBall:
        offset = -BALL_RADIUS
    else:
        offset = -CAR_HEIGHT

    s = obj.pos.z + offset
    root = u**2 - 2*G*s

    if root < 0:
        return 0
    else:
        return (-u - math.sqrt(root)) / G


def get_pos_at_time(velocity: MyVec3, position: MyVec3, t):  # TODO for bounce, make the velocity arguments?
    vx = velocity.x
    vy = velocity.y
    vz = velocity.z

    x = position.x
    y = position.y
    z = position.z

    return [(vx*t + 0.5*vx*t**2) + x,
            (vy*t + 0.5*vx*t**2) + y,
            (vz*t + 0.5*G*t**2) + z]


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
