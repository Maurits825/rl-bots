import math
import time
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from utility import *


class Predict(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()
        self.ball = Obj()
        self.me = Obj()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # preprocess game data variables
        self.preprocess(packet)

        # render stuff
        t = time_to_ground(self.ball)
        self.renderer.begin_rendering()
        self.draw_curve(self.ball)
        self.renderer.end_rendering()
        return self.controller

    def preprocess(self, game):
        index = 0
        self.me.pos.data = [game.game_cars[index].physics.location.x,
                            game.game_cars[index].physics.location.y,
                            game.game_cars[index].physics.location.z]

        self.me.velocity.data = [game.game_cars[index].physics.velocity.x,
                                 game.game_cars[index].physics.velocity.y,
                                 game.game_cars[index].physics.velocity.z]

        self.me.rotation.data = [game.game_cars[index].physics.rotation.pitch,
                                 game.game_cars[index].physics.rotation.yaw,
                                 game.game_cars[index].physics.rotation.roll]

        self.me.rvel.data = [game.game_cars[index].physics.angular_velocity.x,
                             game.game_cars[index].physics.angular_velocity.y,
                             game.game_cars[index].physics.angular_velocity.z]

        self.ball.pos.data = [game.game_ball.physics.location.x,
                              game.game_ball.physics.location.y,
                              game.game_ball.physics.location.z]

        self.ball.velocity.data = [game.game_ball.physics.velocity.x,
                                   game.game_ball.physics.velocity.y,
                                   game.game_ball.physics.velocity.z]

        self.ball.rotation.data = [game.game_ball.physics.rotation.pitch,
                                   game.game_ball.physics.rotation.yaw,
                                   game.game_ball.physics.rotation.roll]

        self.ball.rvel.data = [game.game_ball.physics.angular_velocity.x,
                               game.game_ball.physics.angular_velocity.y,
                               game.game_ball.physics.angular_velocity.z]
        self.ball.isBall = True

    def draw_curve(self, obj):
        t = time_to_ground(obj)
        ground_pos = pos_at_time(obj, t)
        self.renderer.draw_rect_3d(ground_pos, 20, 20, True,
                                   self.renderer.red())

        samples = 8
        prev_pos = pos_at_time(obj, 0)
        for i in range(1, samples+1):
            j = t*i/samples
            pos = pos_at_time(obj, j)
            self.renderer.draw_line_3d(prev_pos, pos, self.renderer.red())
            prev_pos = pos
