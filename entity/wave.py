from var.variables import *
from .Sprites import Obstacle

# Class for the chasing wave enemy
class Tsunami(Obstacle):
    # Class constructor
    def __init__(self, name, x, y, width, height, speed, delay, 
        increasers=(1,1), decreasers=(1,1),
        color=None, image=None, frames=None, fps=1, current_frame=0):
        super().__init__(name, x, y, width, height, 9999, 0, 0, color, image, frames, fps, current_frame)
        self._speed = round(speed*increasers[0]*increasers[1])     # How far the wave moves per tick
        self._delay = round(delay*decreasers[0]*decreasers[1])     # The delay before the wave starts moving
        self._start_pos = (x, y)
        self._counting_delay = delay

    # Moves the wave to the right of the screen
    def move(self):
        self._x += self._speed
        self.update_pos()

    # Resets the tsunami to its starting state
    def reset(self):
        self._counting_delay = self._delay
        self._x, self._y = self._start_pos
        self.update_pos()

    # Updates the Tsunami object
    def update(self, collide_list, player):
        if self._counting_delay > 0:
            self._counting_delay -= Clock.get_time()     # Takes time from delay
        else:
            self.move()             # If delay runs out, wave will move
        if self.get_name() in collide_list:
            self.whenCollide(player)    # Calls whenCollide inherited from Obstacle (Deals 9999 dmg)

