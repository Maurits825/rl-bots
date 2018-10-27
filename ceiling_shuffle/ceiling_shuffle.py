from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import math
from utility.util import *
from utility.predict import *


class CeilingShuffle(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()
        self.ball = Obj()
        self.me = Obj()

        # Contants
        self.DODGE_TIME = 0.2

        self.current_state = 'Idle'
        self.next_state = 'Idle'

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # preprocess game data variables
        self.preprocess(packet)

        # ceiling shuffle
        self.ceiling_shuffle()
        if self.current_state == 'Idle':
            self.current_state = 'Reset'

        #render stuff
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(0, 0, 5, 5, self.current_state,
                                     self.renderer.black())
        self.renderer.draw_string_2d(0, 100, 5, 5, str(self.me.pos.x),
                                     self.renderer.black())
        self.renderer.draw_string_2d(0, 200, 5, 5, str(self.me.pos.y),
                                     self.renderer.black())
        self.renderer.draw_string_2d(0, 300, 5, 5, str(self.me.pos.z),
                                     self.renderer.black())
        self.renderer.end_rendering()

        return self.controller

    def preprocess(self, game):
        index = self.index
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

        self.me.matrix = rotator_to_matrix(self.me)

        self.ball.isBall = True

    def ceiling_shuffle(self):
        if self.current_state == 'Reset':
            # aim at orange goal and throttle
            target_y = 3200
            self.controller.steer = aim_front(self.me, Vector3(0, target_y, 0))
            self.controller.throttle = 0.5

            # check if at orange goal
            offset = 200
            if (-offset < self.me.pos.x < offset and
                    (target_y-offset) < self.me.pos.y < (target_y+offset)):
                self.next_state = 'Middle'

        elif self.current_state == 'Middle':
            # aim at middle and throttle
            self.controller.steer = aim_front(self.me, Vector3(0, 0, 0))
            self.controller.throttle = 1

            # check if at center
            offset = 50
            if (-offset < self.me.pos.x < offset and
                    -offset < self.me.pos.y < offset):
                self.controller.throttle = -1
                self.next_state = 'Corner'

        elif self.current_state == 'Corner':
            # aim at corner and throttle
            t_x = 3072
            t_y = -4096
            self.controller.steer = aim_front(self.me, Vector3(t_x, t_y, 0))
            self.controller.throttle = 1

            # check if at center
            offset = 50
            if ((t_x-offset) < self.me.pos.x < (t_x+offset) and
                    (t_y-offset) < self.me.pos.y < (t_y+offset)):
                self.controller.throttle = -1
                self.next_state = 'Roof'

        elif self.current_state == 'Roof':
            # go to roof
            # should be facing correct direction
            self.controller.steer = 0
            self.controller.throttle = 1

            # check if at roof
            ceiling_z = 2044
            offset = 50
            if self.me.pos.z > ceiling_z - offset:
                self.controller.throttle = -1
                self.next_state = 'Middle'

        elif self.current_state == 'Idle':
            self.controller.steer = 0
            self.controller.throttle = 0

        self.current_state = self.next_state
