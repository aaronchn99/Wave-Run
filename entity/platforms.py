from .Sprites import Entity


# Platform class for collidable platforms (Inherits Entity)
class Platform(Entity):
    # Class constructor required name, position, dimensions and colour
    def __init__(self, name, x, y, width, height, texture, **kwargs):
        # Calls the superclass' constructor (i.e. Entity)
        super().__init__(name, x, y, width, height, texture)

    # Method for executing scripts upon collision with the Player
    def whenCollide(self):
        pass

    # Update method which overrides the one from the Sprite class. Takes one argument: the
    # list names of sprites that collided with the Player
    def update(self, collide_list, _):
        # If the Platform's name is in the list, it will call the whenCollide method
        if self._name in collide_list:
            self.whenCollide()

