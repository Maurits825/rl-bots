import math
import time
import sys
import os

# in order to access utility folder
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from utility.util import *
from utility.prediction import *


class PredictBot(BaseAgent):

    def initialize_agent(self):
        # This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
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
        return self.controller_state

    def preprocess(self, game):  # TODO move to utils?
        index = 0
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

        self.ball.isBall = True

    def draw_curve(self, obj):
        t = time_to_ground(obj)
        ground_pos = pos_at_time(obj, t)
        self.renderer.draw_rect_3d(ground_pos, 20, 20, True,
                                   self.renderer.red())

        samples = 15
        prev_pos = pos_at_time(obj, 0)
        for i in range(1, samples+1):
            j = t*i/samples
            pos = pos_at_time(obj, j)
            self.renderer.draw_line_3d(prev_pos, pos, self.renderer.red())
            prev_pos = pos
