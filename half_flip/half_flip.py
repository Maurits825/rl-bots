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


class States(Enum):
    idle = 1
    reset = 2
    start = 3
    first_jump = 4
    wait_jump = 5
    second_jump = 6
    cancel = 7
    roll = 8


class HalfFlip(BaseAgent):

    def initialize_agent(self):
        self.controller = SimpleControllerState()

        # Contants
        self.DODGE_TIME = 0.2
        self.timeout = 3
        self.t = 0

        self.me = Obj()

        self.current_state = States.idle
        self.next_state = States.idle
        self.jump_start = 0

    def half_flip(self):
        if self.current_state is States.idle:
            self.controller.throttle = 0
            self.controller.jump = 0
            self.controller.roll = 0
            self.controller.pitch = 0
            self.controller.boost = 0
            self.next_state = States.idle

        elif self.current_state is States.reset:
            self.controller.throttle = 0
            self.controller.jump = 0
            self.controller.roll = 0
            self.controller.pitch = 0
            self.controller.boost = 0
            car_state = CarState(physics=Physics(velocity=Vector3(0, 0, 0),
                                                 rotation=Rotator(0, 0, 0),
                                                 angular_velocity=Vector3(0, 0, 0),
                                                 location=Vector3(0, 0, 16.6)))
            game_state = GameState(cars={self.index: car_state})
            self.set_game_state(game_state)
            self.next_state = States.start

        elif self.current_state is States.start:
            self.controller.jump = 1
            self.controller.pitch = 1
            self.controller.throttle = -1
            self.jump_start = time.time()
            self.next_state = States.wait_jump

        elif self.current_state is States.wait_jump:
            self.controller.jump = 0
            if (time.time()-self.jump_start) > self.DODGE_TIME:
                self.next_state = States.second_jump
            else:
                self.next_state = States.wait_jump

        elif self.current_state is States.second_jump:
            self.controller.jump = 1
            self.controller.pitch = 1
            if self.me.rotation.x > 1.4:
                self.next_state = States.cancel
            else:
                self.next_state = States.second_jump

        elif self.current_state is States.cancel:
            self.controller.pitch = -1
            if self.me.rotation.x < 0.3:
                self.next_state = States.roll
            else:
                self.next_state = States.cancel

        elif self.current_state is States.roll:
            self.controller.boost = 1
            self.controller.roll = 1
            if -0.1 < self.me.rotation.z < 0.1:
                self.next_state = States.idle
            else:
                self.next_state = States.roll

        else:
            self.next_state = States.idle

        self.current_state = self.next_state

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Update game data variables
        self.me = pre_process(packet, self.index)
        my_car = packet.game_cars[self.index]

        if packet.game_cars[1].jumped and time.time() > self.t+self.timeout:
            self.t = time.time()
            self.current_state = States.reset

        self.renderer.begin_rendering()
        self.renderer.draw_string_3d(my_car.physics.location, 2, 2, str(self.current_state), self.renderer.white())
        self.renderer.end_rendering()

        self.half_flip()

        return self.controller
