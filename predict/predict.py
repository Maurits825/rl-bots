from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import math
import time


class Vector3:
    def __init__(self, data):
        self.data = data

    def __sub__(self, value):
        return Vector3([self.data[0]-value.data[0],
                        self.data[1]-value.data[1],
                        self.data[2]-value.data[2]])

    def __mul__(self, value):
        return (self.data[0]*value.data[0] +
                self.data[1]*value.data[1] +
                self.data[2]*value.data[2])


class obj:
    def __init__(self):
        self.location = Vector3([0, 0, 0])
        self.velocity = Vector3([0, 0, 0])
        self.rotation = Vector3([0, 0, 0])
        self.rvelocity = Vector3([0, 0, 0])

        self.local_location = Vector3([0, 0, 0])


class Predict(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()
        self.ball = obj()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # preprocess game data variables
        self.preprocess(packet)

        # render stuff
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(0, 0, 5, 5, 'Hello!',
                                     self.renderer.black())
        self.renderer.end_rendering()

        return self.controller

    def preprocess(self, game):
        self.ball.location.data = [game.game_ball.physics.location.x,
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
