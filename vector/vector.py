import math
import time
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from utility.util import *
from utility.predict import *


class Predict(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()
        self.ball = Obj()
        self.me = Obj()
        self.scale = 700

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # preprocess game data variables
        self.preprocess(packet)

        #vector stuff
        matrix = rotator_to_matrix(self.me)
        x_axis = [self.scale*matrix[0].x + self.me.pos.x,
                  self.scale*matrix[0].y + self.me.pos.y,
                  self.scale*matrix[0].z + self.me.pos.z]

        y_axis = [self.scale * matrix[1].x + self.me.pos.x,
                  self.scale * matrix[1].y + self.me.pos.y,
                  self.scale * matrix[1].z + self.me.pos.z]

        z_axis = [self.scale * matrix[2].x + self.me.pos.x,
                  self.scale * matrix[2].y + self.me.pos.y,
                  self.scale * matrix[2].z + self.me.pos.z]

        # render stuff
        t = time_to_ground(self.ball)
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(0, 0, 5, 5, 'P: {:0.2f}, Y: {:0.2f}, R: {:0.2f}'
                                     .format(self.me.rotation.x, self.me.rotation.y, self.me.rotation.z),
                                     self.renderer.black())

        self.renderer.draw_line_3d([self.me.pos.x, self.me.pos.y, self.me.pos.z], x_axis, self.renderer.red())
        self.renderer.draw_line_3d([self.me.pos.x, self.me.pos.y, self.me.pos.z], y_axis, self.renderer.blue())
        self.renderer.draw_line_3d([self.me.pos.x, self.me.pos.y, self.me.pos.z], z_axis, self.renderer.green())
        self.renderer.end_rendering()
        return self.controller

    def preprocess(self, game):
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

    def draw_curve(self, ball):
        t = time_to_ground(ball)
        prev_pos = ball.pos.data

        ground_pos = pos_at_time(ball, t)
        self.renderer.draw_rect_3d(ground_pos, 20, 20, True,
                                   self.renderer.red())
        self.renderer.draw_string_2d(0, 0, 5, 5, 'x: {:0.2f}, y: {:0.2f}'
                                     .format(ground_pos[0], ground_pos[1]),
                                     self.renderer.black())

        samples = 8
        for i in range(1, samples+1):
            j = t*i/samples
            pos = pos_at_time(ball, j)
            pos[2] = (ball.velocity.data[2]*j + 0.5*G*j**2) + ball.pos.data[2]
            self.renderer.draw_line_3d(prev_pos, pos, self.renderer.red())
            prev_pos = pos
