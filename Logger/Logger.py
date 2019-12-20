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
        # pre-process ball
        pre_process(packet, -1)

        return self.controller_state
