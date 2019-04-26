import math
import time
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from utility.util import *
from utility.predict import *
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator, GameInfoState


class Vector(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()
        self.ball = Obj()
        self.me = Obj()
        self.scale = 700
        self.once = True

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

        x_axis_vector = myVector3(x_axis[0], x_axis[1], x_axis[2])
        #print(x_axis_vector.angle(Vector32(0, 0, 1)))

        x_vector = myVector3(matrix[0].x, matrix[0].y, matrix[0].z)
        cross_vec = x_vector.cross(myVector3(0, 0, 1))
        #print(str(cross_vec.x) + ',' + str(cross_vec.y) + ',' + str(cross_vec.z))

        #local_cross = vector_to_local(matrix, cross_vec)
        #print(str(local_cross.x) + ',' + str(local_cross.y) + ',' + str(local_cross.z))

        #test = vector_to_local(matrix, Vector3(1, 0, 0))
        #print('t' + str(test.x) + ',' + str(test.y) + ',' + str(test.z))
        #print(str(cross_vec.y) + ',' + str(matrix[1].y))
        # TODO can determine what pitch to use based on sign

        cross_vec_axis = [self.scale * cross_vec.x + self.me.pos.x,
                          self.scale * cross_vec.y + self.me.pos.y,
                          self.scale * cross_vec.z + self.me.pos.z]


        # render stuff

        self.renderer.begin_rendering()
        # self.renderer.draw_string_2d(0, 0, 5, 5, 'P: {:0.2f}, Y: {:0.2f}, R: {:0.2f}'
        #                             .format(self.me.rotation.x, self.me.rotation.y, self.me.rotation.z),
        #                             self.renderer.black())

        self.renderer.draw_line_3d([self.me.pos.x, self.me.pos.y, self.me.pos.z], x_axis, self.renderer.red())
        self.renderer.draw_line_3d([self.me.pos.x, self.me.pos.y, self.me.pos.z], y_axis, self.renderer.blue())
        self.renderer.draw_line_3d([self.me.pos.x, self.me.pos.y, self.me.pos.z], z_axis, self.renderer.green())

        self.renderer.draw_line_3d([self.me.pos.x, self.me.pos.y, self.me.pos.z], cross_vec_axis, self.renderer.orange())

        #self.renderer.draw_line_3d([0, 0, 100], [700, 0, 100], self.renderer.red())
        #self.renderer.draw_line_3d([0, 0, 100], [0, 700, 100], self.renderer.blue())
        #self.renderer.draw_line_3d([0, 0, 100], [0, 0, 700], self.renderer.green())
        self.renderer.end_rendering()

        return self.controller

    def preprocess(self, game):
        index = 1
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

    def draw_curve(self, ball): # TODO move to utils
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
