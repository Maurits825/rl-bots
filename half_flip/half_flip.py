from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import math
import time
from utility.util import *
from rlbot.utils.game_state_util import GameState


class HalfFlip(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()

        # Contants
        self.DODGE_TIME = 0.2

        self.me = Obj()
        self.ball = Obj()

        self.current_state = 'Idle'
        self.next_state = 'Idle'
        self.jump_start = 0

    def half_flip(self):
        if self.current_state == 'Idle':
            self.controller.throttle = 0
            self.controller.jump = 0
            self.controller.roll = 0
            self.controller.pitch = 0
            self.next_state = 'Idle'

        elif self.current_state == 'Reset':
            self.controller.throttle = 0
            self.controller.jump = 0
            self.controller.roll = 0
            self.controller.pitch = 0
            self.next_state = 'Start'

        elif self.current_state == 'Start':
            self.controller.jump = 1
            self.controller.pitch = 1
            self.jump_start = time.time()
            self.next_state = 'wait_jump'

        elif self.current_state == 'wait_jump':
            self.controller.jump = 0
            if (time.time()-self.jump_start) > self.DODGE_TIME:
                self.next_state = 'second_jump'
            else:
                self.next_state = 'wait_jump'

        elif self.current_state == 'second_jump':
            self.controller.jump = 1
            self.controller.pitch = 1
            if self.me.rotation.x > 1.4:
                self.next_state = 'cancel'
            else:
                self.next_state = 'second_jump'

        elif self.current_state == 'cancel':
            self.controller.pitch = -1
            if self.me.rotation.x < 0.3:
                self.next_state = 'roll'
            else:
                self.next_state = 'cancel'

        elif self.current_state == 'roll':
            self.controller.roll = 1
            if -0.1 < self.me.rotation.z < 0.1:
                self.next_state = 'Idle'
            else:
                self.next_state = 'roll'

        else:
            self.next_state = 'Idle'

        self.current_state = self.next_state

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Update game data variables
        self.preprocess(packet)

        if packet.game.game_cars[0].jumped:
            self.next_state = 'Reset'
            self.half_flip()

        # render stuff
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(0, 0, 5, 5, self.current_state, self.renderer.black())
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

        #self.me.matrix = rotator_to_matrix(self.me)

        self.ball.isBall = True
