from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import math
import time

class Vector3:
    def __init__(self, data):
        self.data = data
    def __sub__(self, value):
        return Vector3([self.data[0]-value.data[0], self.data[1]-value.data[1], self.data[2]-value.data[2]])
    def __mul__(self, value):
        return (self.data[0]*value.data[0] + self.data[1]*value.data[1] + self.data[2]*value.data[2])


class obj:
    def __init__(self):
        self.location = Vector3([0, 0, 0])
        self.velocity = Vector3([0, 0, 0])
        self.rotation = Vector3([0, 0, 0])
        self.rvelocity = Vector3([0, 0, 0])

        self.local_location = Vector3([0, 0, 0])
        self.boost = 0


class HalfFlip(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()


    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Update game data variables
        self.bot_yaw = packet.game_cars[self.team].physics.rotation.yaw
        self.bot_pos = packet.game_cars[self.index].physics.location
        self.bot_pitch = packet.game_cars[self.team].physics.rotation.pitch
        self.bot_roll = packet.game_cars[self.team].physics.rotation.roll

        self.ball_pos = packet.game_ball.physics.location.x


        #render stuff
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(0, 0, 5, 5, 'Ball: ' + str(self.ball_pos), self.renderer.black())
        self.renderer.end_rendering()

        return self.controller
