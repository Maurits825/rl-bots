from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import math
import time


class HalfFlip(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()

        # Contants
        self.DODGE_TIME = 0.2

        # Game values
        self.bot_pos = None
        self.bot_yaw = None
        self.bot_pitch = 0
        self.bot_roll = 0

        self.current_state = 'N'
        self.next_state = 'N'
        self.jump_start = 0

        # This is just a variable used to make the bot jump every few seconds as a demonstration.
        # This isn't used for anything else, so you can remove it (and the code block that contains this
        # variable (line 68-ish)) if you don't want to see the bot jump every few seconds
        self.dodge_interval = 0

    def aim(self, target_x, target_y):
        angle_between_bot_and_target = math.atan2(target_y - self.bot_pos.y,
                                                target_x - self.bot_pos.x)

        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw

        # Correct the values
        if angle_front_to_target < -math.pi:
            angle_front_to_target += 2 * math.pi
        if angle_front_to_target > math.pi:
            angle_front_to_target -= 2 * math.pi

        if angle_front_to_target < math.radians(-10):
            # If the target is more than 10 degrees right from the centre, steer left
            self.controller.steer = -1
        elif angle_front_to_target > math.radians(10):
            # If the target is more than 10 degrees left from the centre, steer right
            self.controller.steer = 1
        else:
            # If the target is less than 10 degrees from the centre, steer straight
            self.controller.steer = 0

    def half_flip(self):
        if self.current_state == 'N':
            self.controller.throttle = 0.2
            self.controller.jump = 0
            self.controller.roll = 0
            self.controller.pitch = 0
            self.next_state = 'N'

        elif self.current_state == 'start':
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
            self.next_state = 'wait_cancel'

        elif self.current_state == 'wait_cancel':
            self.controller.jump = 0
            self.controller.roll = 0
            if self.bot_pitch > 1.4:
                self.next_state = 'cancel'
            else:
                self.next_state = 'wait_cancel'

        elif self.current_state == 'cancel':
            self.controller.pitch = -1
            self.next_state = 'wait_roll'

        elif self.current_state == 'wait_roll':
            if self.bot_pitch < 0.3:
                self.next_state = 'roll'
            else:
                self.next_state = 'wait_roll'

        elif self.current_state == 'roll':
            self.controller.roll = 1
            self.next_state = 'wait_N'

        elif self.current_state == 'wait_N':
            if self.bot_roll < 0.1 and self.bot_roll > -0.1:
                self.next_state = 'N'
            else:
                self.next_state = 'wait_N'

        else:
            self.next_state = 'N'

        self.current_state = self.next_state

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Update game data variables
        self.bot_yaw = packet.game_cars[self.team].physics.rotation.yaw
        self.bot_pos = packet.game_cars[self.index].physics.location
        self.bot_pitch = packet.game_cars[self.team].physics.rotation.pitch
        self.bot_roll = packet.game_cars[self.team].physics.rotation.roll

        # Just making the bot jump every 3 seconds as demonstration. You can remove this if-block and it won't break the code.
        if self.dodge_interval < time.time():
            #self.should_dodge = True
            self.current_state = 'start'
            self.dodge_interval = time.time() + 3

        self.controller.throttle = -0.2
        self.half_flip()

        #render stuff
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(0, 0, 5, 5, self.current_state, self.renderer.black())
        self.renderer.end_rendering()

        return self.controller
