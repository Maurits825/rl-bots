import math
import os
import sys
from utility.myVec3 import MyVec3

try:
    from scipy.special import lambertw
except ImportError:
    sys.path.insert(1, os.path.join(sys.path[0], r"C:\Users\Maurits\AppData\Local\Programs\Python\Python38\Lib\site-packages\scipy"))
    from scipy.special import lambertw

try:
    from rlbot.utils.game_state_util import Physics
except ModuleNotFoundError:
    sys.path.insert(1, os.path.join(sys.path[0], r"C:\Users\Maurits\AppData\Local\RLBotGUI\Python\Lib\site-packages"))
    from rlbot.utils.game_state_util import Physics

# TODO problems with sci py lib, this cmd worked for rl bot env:
# "C:\Users\Maurits\AppData\Local\RLBotGUI\Python\python.exe" -m pip install --target="C:\Users\Maurits\AppData\Local\RLBotGUI\Python\Lib\site-packages" scipy
# it defauls try to use that sci py, when running in diff env like when running rl-bot-sim
# is this messy?


# ref: https://github.com/RLBot/RLBot/wiki/Useful-Game-Values
G = -650
DRAG = 0.030500000342726707
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
C_R = 0.6000000238418579
F = 0.0003

moment_of_inertia = 99918.75
mass = 30
omega_max = 6

# Following functions are based on frame number (f), TODO change based on time?
def d_get_vel(f, initial_velocity):
    c = (initial_velocity.z - A) / -DECAY

    return MyVec3(initial_velocity.x * (1-DRAG)**(f / FPS),
                  initial_velocity.y * (1-DRAG)**(f / FPS),
                  ((initial_velocity.z - A) * math.e ** (DECAY * f)) + A)


def d_get_pos(f, initial_velocity, initial_position):
    c = (initial_velocity.z - A) / -DECAY

    return MyVec3(initial_position.x + ((((initial_velocity.x * (1 - DRAG)**(f/FPS)) / B) - (initial_velocity.x / B)) / FPS),
                  initial_position.y + ((((initial_velocity.y * (1 - DRAG)**(f/FPS)) / B) - (initial_velocity.y / B)) / FPS),
                  initial_position.z + (((((initial_velocity.z - A) * math.e ** (DECAY * f)) / DECAY) + A * f + c) / FPS))


def d_time_to_ground(initial_velocity, initial_position):
    K = (initial_velocity.z - A) / DECAY
    const_A = (K - FPS*(initial_position.z - BALL_RADIUS)) / A
    W = lambertw((DECAY*K * math.e**(DECAY * const_A)) / A)

    ret = const_A - (W / DECAY)
    return ret.real / FPS


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

    return MyVec3((vx*t) + x,
                  (vy*t) + y,
                  (vz*t + 0.5*G*t**2) + z)


def get_vel_at_time(t, initial_velocity):
    return MyVec3(initial_velocity.x,
                  initial_velocity.y,
                  initial_velocity.z + G*t)


# ref: https://samuelpmish.github.io/notes/RocketLeague/ball_bouncing/
def update_physics_after_bounce(physics: Physics, time_ground, ground_pos, physics_flag):
    ret_physics = Physics()

    ground_velocity = None

    if physics_flag == 'no_drag':
        ground_velocity = get_vel_at_time(time_ground, physics.velocity)

    elif physics_flag == 'drag':
        frame = time_ground * FPS
        ground_velocity = d_get_vel(frame, physics.velocity)

    elif physics_flag == 'engine_sim':
        pass

    else:
        return

    normal = MyVec3(0, 0, 1)  # TODO assume ground bounces for now
    vel_perp = ground_velocity.dot(normal) * normal  # velocity projection on normal vector
    vel_para = ground_velocity - vel_perp  # vector subtraction to get parallel vector
    vel_spin = BALL_RADIUS * normal.cross(physics.angular_velocity)  # spin velocity is perp to normal and axis of ang v
    vel_slip = vel_para + vel_spin

    ratio = vel_perp.mag() / vel_slip.mag()

    delta_vel_perp = - (1 + C_R) * vel_perp
    delta_vel_para = -1 * (min(1, Y * ratio) * mu * vel_slip)

    delta_vel_perp_m = (-mass * (1 + C_R) * vel_perp) * (1/FPS)
    delta_vel_para_m = (-mass * (min(1, Y * ratio) * mu * vel_slip)) * (1/FPS)

    ret_physics.location = ground_pos
    ret_physics.velocity = ground_velocity + delta_vel_perp + delta_vel_para
    new_angular = physics.angular_velocity + (F * BALL_RADIUS * delta_vel_para.cross(normal))
    ret_physics.angular_velocity = new_angular.rescale(omega_max)

    #ret_physics.angular_velocity = physics.angular_velocity + ((BALL_RADIUS / moment_of_inertia) * delta_vel_para_m.cross(normal))

    return ret_physics


def get_bounces(physics: Physics, bounce_num=5, base_samples=15, physics_flag='no_drag'):
    positions = []
    velocitys = []
    angulars = []
    times = []

    current_physics = physics
    initial_velocity = current_physics.velocity
    initial_position = current_physics.location
    last_time = 0
    for b in range(bounce_num):
        time_ground = 0
        if physics_flag == 'no_drag':
            time_ground = time_to_ground(initial_velocity, initial_position)

        elif physics_flag == 'drag':
            time_ground = d_time_to_ground(initial_velocity, initial_position)

        elif physics_flag == 'engine_sim':
            pass

        else:
            return

        samples = int(base_samples * time_ground)
        time_interval = (time_ground / samples)
        t = 0

        current_pos = None
        current_vel = None
        current_ang = None

        for s in range(0, samples + 1):
            t = s * time_interval

            if physics_flag == 'no_drag':
                current_pos = get_pos_at_time(initial_velocity, initial_position, t)
                current_vel = get_vel_at_time(t, initial_velocity)
                current_ang = current_physics.angular_velocity

            elif physics_flag == 'drag':
                frame = t * FPS
                current_pos = d_get_pos(frame, initial_velocity, initial_position)
                current_vel = d_get_vel(frame, initial_velocity)
                current_ang = current_physics.angular_velocity

            elif physics_flag == 'engine_sim':
                pass

            else:
                return

            positions.append(current_pos)
            velocitys.append(current_vel)
            angulars.append(current_ang)
            times.append(last_time + t)

        new_physics = update_physics_after_bounce(current_physics, time_ground, current_pos, physics_flag)

        initial_velocity = new_physics.velocity
        initial_position = new_physics.location
        current_physics = new_physics
        last_time = last_time + t

    return times, positions, velocitys, angulars


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
