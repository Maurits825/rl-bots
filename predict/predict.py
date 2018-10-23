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

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # preprocess game data variables
        self.preprocess(packet)

        # render stuff
        t = time_to_ground(self.ball)
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(0, 0, 5, 5, str(t),
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
        prev_pos = ball.pos.data

        ground_pos = pos_at_time(ball, t)
        self.renderer.draw_rect_3d(ground_pos, 20, 20, True,
                                   self.renderer.red())

        samples = 8
        for i in range(1, samples+1):
            j = t*i/samples
            pos = pos_at_time(ball, j)
            pos[2] = (ball.velocity.data[2]*j + 0.5*G*j**2) + ball.pos.data[2]
            self.renderer.draw_line_3d(prev_pos, pos, self.renderer.red())
            prev_pos = pos
