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
        t = time_to_ground(self.ball)
        self.ball_ground_pos = ground_pos(self.ball)
        # render stuff
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(0, 0, 5, 5, str(self.ball.pos.data[2]),
                                     self.renderer.black())
        self.renderer.draw_line_3d((self.ball.pos.data[0], self.ball.pos.data[1], self.ball.pos.data[2]), self.ball_ground_pos,
                                   self.renderer.black())
        self.renderer.draw_rect_3d(self.ball_ground_pos, 20, 20, True, self.renderer.black())


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
