from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import math
import time
from utility.util import *
from utility.predict import *
from rlbot.utils.game_state_util import GameState, CarState, Rotator, Physics
from rlbot.utils.game_state_util import Vector3 as V3


class SpaceX(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()
        self.ball = Obj()
        self.me = Obj()

        self.t = 0
        self.timeout = 3

        self.tR = 0
        self.timeoutR = 2

        self.second_jump_time = 0
        self.second_timeout = 2.1

        # Contants
        self.DODGE_TIME = 0.2

        self.current_state = 'Idle'
        self.next_state = 'Idle'

        self.start = time.time()
        self.delay = 3

        self.launch_time = 0
        self.time_burn = 0

        self.land_height = 0

        # PID stuff
        self.prev_pitch_error = math.pi/2

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # preprocess game data variables
        self.preprocess(packet)

        # hel_jump
        if packet.game_cars[0].jumped and time.time() > self.t+self.timeout:
            self.t = time.time()
            self.current_state = 'Reset'

        self.space_x()

        #render stuff
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(0, 0, 5, 5, self.current_state,
                                     self.renderer.black())
        #self.renderer.draw_string_2d(0, 100, 5, 5, str(accel),
         #                            self.renderer.black())
        self.renderer.end_rendering()
        return self.controller

    def preprocess(self, game):
        index = self.index
        self.me.pos.x = game.game_cars[index].physics.location.x
        self.me.pos.y = game.game_cars[index].physics.location.y
        self.me.pos.z = game.game_cars[index].physics.location.z

        self.me.velocity.x = game.game_cars[index].physics.velocity.x
        self.me.velocity.y = game.game_cars[index].physics.velocity.y
        self.me.velocity.z = game.game_cars[index].physics.velocity.z

        self.me.rotation.x = game.game_cars[index].physics.rotation.pitch
        self.me.rotation.y = game.game_cars[index].physics.rotation.yaw
        self.me.rotation.z = game.game_cars[index].physics.rotation.roll

        self.me.rvel.x = game.game_cars[index].physics.angular_velocity.x
        self.me.rvel.y = game.game_cars[index].physics.angular_velocity.y
        self.me.rvel.z = game.game_cars[index].physics.angular_velocity.z

        self.ball.pos.x = game.game_ball.physics.location.x
        self.ball.pos.y = game.game_ball.physics.location.y
        self.ball.pos.z = game.game_ball.physics.location.z

        self.ball.velocity.x = game.game_ball.physics.velocity.x
        self.ball.velocity.y = game.game_ball.physics.velocity.y
        self.ball.velocity.z = game.game_ball.physics.velocity.z

        self.ball.rotation.x = game.game_ball.physics.rotation.pitch
        self.ball.rotation.y = game.game_ball.physics.rotation.yaw
        self.ball.rotation.z = game.game_ball.physics.rotation.roll

        self.ball.rvel.x = game.game_ball.physics.angular_velocity.x
        self.ball.rvel.y = game.game_ball.physics.angular_velocity.y
        self.ball.rvel.z = game.game_ball.physics.angular_velocity.z

        self.me.matrix = rotator_to_matrix(self.me)

        self.ball.isBall = True

    def space_x(self):
        if self.current_state == 'Reset':
            self.controller.jump = 0
            self.controller.pitch = 0
            self.controller.boost = 0
            car_state = CarState(physics=Physics(velocity=V3(0, 0, 0),
                                                 rotation=Rotator(math.pi/2, 0, 0),
                                                 angular_velocity=V3(0, 0, 0),
                                                 location=V3(0, 0, 50)))
            game_state = GameState(cars={self.index: car_state})
            self.set_game_state(game_state)

            self.tR = time.time()
            self.next_state = 'Boost'

        elif self.current_state == 'Timeout':

            if time.time() > self.tR+self.timeoutR:
                self.next_state = 'Jump'

        elif self.current_state == 'Jump':
            self.sas()
            self.controller.jump = 1

            if self.me.rotation.x > (math.pi/2 - 0.05):
                self.next_state = 'Boost'

        elif self.current_state == 'Boost':
            self.sas()
            self.controller.boost = 1

            if self.me.pos.z > 800:
                self.launch_time = time.time()
                self.next_state = 'Falling'

        elif self.current_state == 'Falling':
            self.sas()
            self.controller.boost = 0
            self.time_burn = burn_time(self.me, self.land_height)

            if self.time_burn < 0:
                self.next_state = 'Suicide_burn'

        elif self.current_state == 'Suicide_burn':
            self.sas()
            self.controller.boost = 1

            if self.me.pos.z < 48+self.land_height:
                self.next_state = 'Land'

        elif self.current_state == 'Land':
            self.sas()
            self.controller.boost = 0

        elif self.current_state == 'Idle':
            self.controller.jump = 0
            self.controller.pitch = 0
            self.controller.boost = 0
            self.next_state = 'Idle'

        self.current_state = self.next_state

    def sas(self):
        kp = 0.8
        kd = 20
        pitch_error = (math.pi/2) - self.me.rotation.x

        # P and D
        if abs(self.me.rotation.y) > math.pi/2:
            p = kp * -pitch_error
            d = kd * (-pitch_error - self.prev_pitch_error)
            self.prev_pitch_error = -pitch_error
        else:
            p = kp * pitch_error
            d = kd * (pitch_error - self.prev_pitch_error)
            self.prev_pitch_error = pitch_error

        # normalize
        #p = p/(math.pi/2)
        #d = d/(math.pi/2)

        pitch = p + d

        if pitch > 1:
            pitch = 1
        elif pitch < -1:
            pitch = -1

        self.controller.pitch = pitch
