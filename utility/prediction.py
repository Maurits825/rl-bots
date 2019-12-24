import math
import os
import sys
import copy
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
ROOF = 2044
SIDE_WALL = 4096
BACK_WALL = 5120

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
def update_physics_after_bounce(physics: Physics, time_ground, ground_pos, physics_flag, normal):
    ret_physics = Physics()

    collision_vel = None

    if physics_flag == 'no_drag':
        collision_vel = get_vel_at_time(time_ground, physics.velocity)

    elif physics_flag == 'drag':
        frame = time_ground * FPS
        collision_vel = d_get_vel(frame, physics.velocity)

    elif physics_flag == 'engine_sim':
        collision_vel = physics.velocity

    else:
        return

    vel_perp = collision_vel.dot(normal) * normal  # velocity projection on normal vector
    vel_para = collision_vel - vel_perp  # vector subtraction to get parallel vector
    vel_spin = BALL_RADIUS * normal.cross(physics.angular_velocity)  # spin velocity is perp to normal and axis of ang v
    vel_slip = vel_para + vel_spin

    try:
        ratio = vel_perp.mag() / vel_slip.mag()
    except ZeroDivisionError:
        ratio = 0

    delta_vel_perp = - (1 + C_R) * vel_perp
    delta_vel_para = -1 * (min(1, Y * ratio) * mu * vel_slip)

    delta_vel_perp_m = (-mass * (1 + C_R) * vel_perp) * (1/FPS)
    delta_vel_para_m = (-mass * (min(1, Y * ratio) * mu * vel_slip)) * (1/FPS)

    ret_physics.location = ground_pos
    ret_physics.velocity = collision_vel + delta_vel_perp + delta_vel_para
    new_angular = physics.angular_velocity + (F * BALL_RADIUS * delta_vel_para.cross(normal))

    # catch angular being zero
    if new_angular.mag() > omega_max:
        ret_physics.angular_velocity = new_angular.rescale(omega_max)
    else:
        ret_physics.angular_velocity = new_angular

    #ret_physics.angular_velocity = physics.angular_velocity + ((BALL_RADIUS / moment_of_inertia) * delta_vel_para_m.cross(normal))

    return ret_physics


def get_bounces(physics: Physics, bounce_num=5, base_samples=15, physics_flag='no_drag'):
    positions = []
    velocitys = []
    angulars = []
    times = []

    current_physics = copy.deepcopy(physics)
    initial_velocity = current_physics.velocity
    initial_position = current_physics.location

    normal = MyVec3(0, 0, 1)  # TODO assume ground only bounces
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

        # if ball on ground TODO fix this?
        try:
            samples = int(base_samples * time_ground)
        except ValueError:
            time_ground = 1
            samples = int(base_samples * time_ground)

        try:
            time_interval = (time_ground / samples)
        except RuntimeWarning:
            time_ground = 1
            samples = FPS
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

        new_physics = update_physics_after_bounce(current_physics, time_ground, current_pos, physics_flag, normal)

        initial_velocity = new_physics.velocity
        initial_position = new_physics.location
        current_physics = new_physics
        last_time = last_time + t

    return times, positions, velocitys, angulars


def physics_engine_sim(physics: Physics, total_time=10):
    current_physics = copy.deepcopy(physics)
    velocity = current_physics.velocity
    position = current_physics.location
    angular = current_physics.angular_velocity

    velocitys = [velocity.copy()]
    positions = [position.copy()]
    angulars = [angular.copy()]
    times = [0]

    total_frames = int(total_time * FPS)
    dt = 1 / FPS

    is_collision = False

    collision_frame = 0
    collision_normal = MyVec3(0, 0, 1)

    for f in range(1, total_frames):

        velocity.z = velocity.z * (1 - DRAG)**dt + (G * dt)
        velocity.x = velocity.x * (1 - DRAG)**dt
        velocity.y = velocity.y * (1 - DRAG)**dt

        position.z = position.z + (velocity.z * dt)
        position.x = position.x + (velocity.x * dt)
        position.y = position.y + (velocity.y * dt)

        dt = 1 / FPS

        # TODO simplify code below? make a function?
        # TODO: IMPORTANT --> need way to handle ball rolling, otherwise if statement below gets called every frame...
        # TODO: related to above, when ball rolling, the velocity is =/= 0 but pos doesnt change
        # collision check, first just ground, check if current frame is valid/not colliding
        if (position.z - BALL_RADIUS) < 0:
            collision_normal = MyVec3(0, 0, 1)
            is_collision = True

            y1 = positions[f - 1].z - BALL_RADIUS
            y2 = position.z - BALL_RADIUS
            m = y2 - y1  # slope denominator always 1, (x2 - x1) = 1
            collision_frame = - (y1 / m)  # frame where ball collides

        # roof check
        elif (position.z + BALL_RADIUS) > ROOF:
            collision_normal = MyVec3(0, 0, -1)
            is_collision = True

            y1 = positions[f - 1].z + BALL_RADIUS
            y2 = position.z + BALL_RADIUS
            m = y2 - y1  # slope denominator always 1, (x2 - x1) = 1
            collision_frame = - ((ROOF - y1) / m)  # frame where ball collides

        #left wall check
        elif (position.x + BALL_RADIUS) > SIDE_WALL:
            collision_normal = MyVec3(-1, 0, 0)
            is_collision = True

            y1 = positions[f - 1].x + BALL_RADIUS
            y2 = position.x + BALL_RADIUS
            m = y2 - y1  # slope denominator always 1, (x2 - x1) = 1
            collision_frame = - ((SIDE_WALL - y1) / m)  # frame where ball collides

        #right wall check
        elif (position.x - BALL_RADIUS) < -SIDE_WALL:
            collision_normal = MyVec3(1, 0, 0)
            is_collision = True

            y1 = positions[f - 1].x - BALL_RADIUS
            y2 = position.x - BALL_RADIUS
            m = y2 - y1  # slope denominator always 1, (x2 - x1) = 1
            collision_frame = - ((-SIDE_WALL - y1) / m)  # frame where ball collides

        #orange wall check
        elif (position.y + BALL_RADIUS) > BACK_WALL:
            collision_normal = MyVec3(0, -1, 0)
            is_collision = True

            y1 = positions[f - 1].y + BALL_RADIUS
            y2 = position.y + BALL_RADIUS
            m = y2 - y1  # slope denominator always 1, (x2 - x1) = 1
            collision_frame = - ((BACK_WALL - y1) / m)  # frame where ball collides

        #blue wall check
        elif (position.y - BALL_RADIUS) < -BACK_WALL:
            collision_normal = MyVec3(0, 1, 0)
            is_collision = True

            y1 = positions[f - 1].y - BALL_RADIUS
            y2 = position.y - BALL_RADIUS
            m = y2 - y1  # slope denominator always 1, (x2 - x1) = 1
            collision_frame = - ((-BACK_WALL - y1) / m)  # frame where ball collides

        else:
            is_collision = False

        if is_collision:
            # approximate linear behaviour, angular doesnt change
            position.z = ((position.z - positions[f - 1].z) * collision_frame) + positions[f - 1].z
            position.x = ((position.x - positions[f - 1].x) * collision_frame) + positions[f - 1].x
            position.y = ((position.y - positions[f - 1].y) * collision_frame) + positions[f - 1].y

            velocity.z = ((velocity.z - velocitys[f - 1].z) * collision_frame) + velocitys[f - 1].z
            velocity.x = ((velocity.x - velocitys[f - 1].x) * collision_frame) + velocitys[f - 1].x
            velocity.y = ((velocity.y - velocitys[f - 1].y) * collision_frame) + velocitys[f - 1].y

            # append these values instead of previously calculated values
            velocitys.append(velocity.copy())
            positions.append(position.copy())
            angulars.append(angular.copy())
            times.append((f - 1 + collision_frame) * dt)

            # update current physics
            current_physics.velocity = velocity.copy()
            current_physics.angular_velocity = angular.copy()
            current_physics.location = position.copy()

            # time to ground argument isnt used for engine sim
            new_physics = update_physics_after_bounce(current_physics, 0, position, 'engine_sim', collision_normal)

            # update values with new physics for next frame
            velocity = new_physics.velocity
            position = new_physics.location
            angular = new_physics.angular_velocity

            # update dt because next frame is a little longer than one frame away
            dt = (1 / FPS) + ((1 - collision_frame) * dt)

        else:
            # no collision, just append values
            velocitys.append(velocity.copy())
            positions.append(position.copy())
            angulars.append(angular.copy())
            times.append(f * dt)

    return times, positions, velocitys, angulars

# TODO:
def basic_collision_check(position):
    if (position.z - BALL_RADIUS) < 0:
        collision_normal = MyVec3(0, 0, 1)
        is_collision = True

        y1 = positions[f - 1].z - BALL_RADIUS
        y2 = position.z - BALL_RADIUS
        m = y2 - y1  # slope denominator always 1, (x2 - x1) = 1
        collision_frame = - (y1 / m)  # frame where ball collides

        # roof check
    elif (position.z + BALL_RADIUS) > ROOF:
        collision_normal = MyVec3(0, 0, -1)
        is_collision = True

        y1 = positions[f - 1].z + BALL_RADIUS
        y2 = position.z + BALL_RADIUS
        m = y2 - y1  # slope denominator always 1, (x2 - x1) = 1
        collision_frame = - ((ROOF - y1) / m)  # frame where ball collides

        # left wall check
    elif (position.x + BALL_RADIUS) > SIDE_WALL:
        collision_normal = MyVec3(-1, 0, 0)
        is_collision = True

        y1 = positions[f - 1].x + BALL_RADIUS
        y2 = position.x + BALL_RADIUS
        m = y2 - y1  # slope denominator always 1, (x2 - x1) = 1
        collision_frame = - ((SIDE_WALL - y1) / m)  # frame where ball collides

        # right wall check
    elif (position.x - BALL_RADIUS) < -SIDE_WALL:
        collision_normal = MyVec3(1, 0, 0)
        is_collision = True

        y1 = positions[f - 1].x - BALL_RADIUS
        y2 = position.x - BALL_RADIUS
        m = y2 - y1  # slope denominator always 1, (x2 - x1) = 1
        collision_frame = - ((-SIDE_WALL - y1) / m)  # frame where ball collides

        # orange wall check
    elif (position.y + BALL_RADIUS) > BACK_WALL:
        collision_normal = MyVec3(0, -1, 0)
        is_collision = True

        y1 = positions[f - 1].y + BALL_RADIUS
        y2 = position.y + BALL_RADIUS
        m = y2 - y1  # slope denominator always 1, (x2 - x1) = 1
        collision_frame = - ((BACK_WALL - y1) / m)  # frame where ball collides

        # blue wall check
    elif (position.y - BALL_RADIUS) < -BACK_WALL:
        collision_normal = MyVec3(0, 1, 0)
        is_collision = True

        y1 = positions[f - 1].y - BALL_RADIUS
        y2 = position.y - BALL_RADIUS
        m = y2 - y1  # slope denominator always 1, (x2 - x1) = 1
        collision_frame = - ((-BACK_WALL - y1) / m)  # frame where ball collides

    else:
        is_collision = False


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
