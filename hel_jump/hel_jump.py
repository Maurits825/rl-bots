import math
import time
import sys
import os
from enum import Enum

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator, GameInfoState

# in order to access utility folder
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from utility.util import *


class HelJump(BaseAgent):
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

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # preprocess game data variables
        self.me = pre_process(packet, self.index)
        my_car = packet.game_cars[self.index]

        # hel_jump
        if packet.game_cars[1].jumped and time.time() > self.t+self.timeout:
            self.t = time.time()
            self.current_state = 'Reset'

        self.hel_jump()

        #render stuff
        self.renderer.begin_rendering()
        self.renderer.draw_string_3d(my_car.physics.location, 2, 2, str(self.current_state), self.renderer.white())
        self.renderer.end_rendering()

        return self.controller

    def hel_jump(self):
        if self.current_state == 'Jump':
            self.controller.throttle = 0
            self.controller.jump = 1
            self.next_state = 'Tilt'

        elif self.current_state == 'Tilt':
            self.controller.jump = 0
            self.controller.handbrake = 1
            self.controller.pitch = -0.3
            #self.controller.boost = 1

            if self.me.rotation.x < -math.pi/6:
                self.next_state = 'WaitJump2'

        elif self.current_state == 'WaitJump2':
            self.controller.pitch = 0
            self.controller.boost = 1

            if self.me.rotation.x > -0.35:
                self.next_state = 'Jump2'

        elif self.current_state == 'Jump2':
            self.controller.jump = 1

            self.second_jump_time = time.time()
            self.next_state = 'Boost'

        elif self.current_state == 'Boost':
            self.controller.boost = 1

            if self.me.pos.z > 500:
                self.controller.boost = 0

            if self.me.rotation.x < (math.pi/2 - 0.5):
                self.controller.pitch = 0.2
            else:
                self.controller.pitch = 0

            if time.time() > self.second_jump_time+self.second_timeout:
                self.next_state = 'SecondJump'

        elif self.current_state == 'SecondJump':
            self.controller.boost = 0
            self.controller.jump = 1
            self.controller.pitch = 1

            self.next_state = 'Idle'

        elif self.current_state == 'Reset':
            self.controller.jump = 0
            self.controller.handbrake = 0
            self.controller.pitch = 0
            self.controller.boost = 0
            car_state = CarState(physics=Physics(velocity=Vector3(0, 0, 0),
                                                 rotation=Rotator(0, 0, 0),
                                                 angular_velocity=Vector3(0, 0, 0),
                                                 location=Vector3(0, 0, 16.6)))
            game_state = GameState(cars={self.index: car_state})
            self.set_game_state(game_state)

            self.tR = time.time()
            self.next_state = 'Timeout'

        elif self.current_state == 'Timeout':

            if time.time() > self.tR+self.timeoutR:
                self.next_state = 'Jump'

        elif self.current_state == 'Idle':
            self.controller.jump = 0
            self.controller.handbrake = 0
            self.controller.pitch = 0
            self.controller.boost = 0
            self.next_state = 'Idle'

        self.current_state = self.next_state
