import math
import time
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from utility import *


class Predict(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()
        self.ball = obj()
        self.ball_ground_pos = [0, 0, 0]

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # preprocess game data variables
        self.preprocess(packet)

        # render stuff
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(0, 0, 5, 5, str(self.ball.pos.data[2]),
                                     self.renderer.black())
        self.draw_curve(self.ball)
        self.renderer.end_rendering()

        return self.controller

    def preprocess(self, game):
        self.ball.pos.data = [game.game_ball.physics.location.x,
                              game.game_ball.physics.location.y,
                              game.game_ball.physics.location.z]

        self.ball.velocity.data = [game.game_ball.physics.velocity.x,
                                   game.game_ball.physics.velocity.y,
                                   game.game_ball.physics.velocity.z]

        self.ball.rotation.data = [game.game_ball.physics.rotation.pitch,
                                   game.game_ball.physics.rotation.yaw,
                                   game.game_ball.physics.rotation.roll]

        self.ball.rvelocity.data = [game.game_ball.physics.angular_velocity.x,
                                    game.game_ball.physics.angular_velocity.y,
                                    game.game_ball.physics.angular_velocity.z]

    def draw_curve(self, ball):
        t = time_to_ground(ball)
        pre_pos = pos_at_time(ball, 0)
        pre_pos[2] = (ball.velocity.data[2]*0 - 0.5*650*0**2) + ball.pos.data[2]

        pos = pos_at_time(ball, t)
        self.renderer.draw_rect_3d(pos, 20, 20, True, self.renderer.red())

        samples = 15
        for i in range(1, samples+1):
            j = t*i/samples
            pos = pos_at_time(ball, j)
            pos[2] = (ball.velocity.data[2]*j - 0.5*650*j**2) + ball.pos.data[2]
            self.renderer.draw_line_3d(pre_pos, pos, self.renderer.red())
            pre_pos = pos
