import math
import time
import sys
import os
import numpy as np
from enum import Enum
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator, GameInfoState

# in order to access utility folder
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from utility.util import *
from utility.prediction import *


class Logger(Enum):
    idle = 1
    setup = 2
    logging = 3
    saving = 4


class PredictBot(BaseAgent):

    def initialize_agent(self):
        # This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        self.ball = Obj()
        self.me = Obj()

        self.logger_state = Logger.idle

        self.velocity = []
        self.position = []

        self.last_time = 0
        self.timeout = 5

        self.log_timer = 5
        self.log_start = 0

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # pre-process ball
        self.ball = pre_process(packet, -1)

        if packet.game_cars[1].jumped and time.time() > (self.last_time + self.timeout):
            self.last_time = time.time()
            self.logger_state = Logger.setup

        my_car = packet.game_cars[self.index]
        self.renderer.begin_rendering()
        self.renderer.draw_string_3d(my_car.physics.location, 2, 2, str(self.logger_state), self.renderer.white())
        self.renderer.end_rendering()

        self.logger_bot()

        return self.controller_state

    def logger_bot(self):
        if self.logger_state is Logger.idle:
            pass

        elif self.logger_state is Logger.setup:
            ball_state = BallState(Physics(location=Vector3(2000, -5100, 100),
                                           velocity=Vector3(0, 2500, 1500),
                                           angular_velocity=Vector3(0, 0, 0)))
            game_state = GameState(ball=ball_state)
            self.set_game_state(game_state)
            self.logger_state = Logger.logging
            self.log_start = time.time()

        elif self.logger_state is Logger.logging:

            if (time.time() - self.log_start) < self.log_timer:
                self.velocity.append(self.ball.velocity)
                self.position.append(self.ball.pos)
            else:
                self.logger_state = Logger.saving

        elif self.logger_state is Logger.saving:
            list_size = len(self.velocity)
            vel = np.zeros((list_size, 3))
            pos = np.zeros((list_size, 3))

            for i in range(list_size):
                vel[i, 0] = self.velocity[i].x
                vel[i, 1] = self.velocity[i].y
                vel[i, 2] = self.velocity[i].z

                pos[i, 0] = self.position[i].x
                pos[i, 1] = self.position[i].y
                pos[i, 2] = self.position[i].z

            # TODO hard-coded dir path
            np.savetxt('./rl-bots/Logger/velocity.csv', vel, delimiter=',', fmt='%f')
            np.savetxt('./rl-bots/Logger/position.csv', pos, delimiter=',', fmt='%f')

            self.logger_state = Logger.idle

        else:
            return
