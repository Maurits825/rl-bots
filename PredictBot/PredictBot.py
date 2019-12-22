import math
import time
import sys
import os

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator, GameInfoState

# in order to access utility folder
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from utility.util import *
from utility.prediction import *


class PredictBot(BaseAgent):

    def initialize_agent(self):
        # This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        self.ball = Obj()
        self.me = Obj()

        self.last_time = 0
        self.timeout = 20
        self.shoot_enabled = False

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # pre-process ball
        self.ball = pre_process(packet, -1)

        if self.shoot_enabled and packet.game_cars[1].jumped and time.time() > (self.last_time + self.timeout):
            self.last_time = time.time()
            self.shoot_ball()

        # render stuff
        self.draw_curve(self.ball)
        return self.controller_state

    def shoot_ball(self):
        ball_state = BallState(Physics(location=Vector3(2500, -4500, 100),
                                       velocity=Vector3(0, 1000, 1500),
                                       angular_velocity=Vector3(0, -10, 0)))
        game_state = GameState(ball=ball_state)
        self.set_game_state(game_state)

    def draw_curve(self, obj):
        initial_physics = Physics(location=obj.pos, velocity=obj.velocity, angular_velocity=obj.rvel)  # TODO better way?
        times, positions, velocitys, angulars = get_bounces(initial_physics, 5, 30, 'drag')

        self.renderer.begin_rendering()
        list_size = len(positions)
        for i in range(list_size):
            # skip first
            if i == 0:
                pass
            else:
                prev_pos = [positions[i - 1].x, positions[i - 1].y, positions[i - 1].z]
                curr_pos = [positions[i].x, positions[i].y, positions[i].z]
                self.renderer.draw_line_3d(prev_pos, curr_pos, self.renderer.red())

        self.renderer.end_rendering()
