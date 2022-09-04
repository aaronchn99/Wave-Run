from var.variables import *
import random as rand
hitbox_mode = 0


''' Classes '''
# Base class for all in game sprites, inherited from Sprite from Pygame
class Entity(pygame.sprite.Sprite):
    # The class constructor. Takes the sprite name, position, dimensions and fill colour
    def __init__(self, name, x, y, width, height, texture):
        # Calls the superclass' constructor (i.e. Sprite class)
        super().__init__()
        # Positional and dimensional attributes
        self._w, self._h = width, height
        self._x, self._y = x, y
        # The entity's name is assigned. Used for sprite identification
        self._name = check_name(name)   # check_name called to check uniqueness
        self.texture = texture
        self.texture.scale(width, height)
        # The Entity object's rect attribute is a Rect object with the dimensions of the
        # above image. Used to hold and position the sprite
        self.rect = self.texture.rect
        # The rect is positioned at the specified coordinates
        self.rect.x, self.rect.y = self._x, self._y

    # Method that returns the entity's name
    def get_name(self):
        return self._name

    # Sets the Entity's position
    def set_pos(self, x, y):
        self._x, self._y = x, y
        self.update_pos()

    # Returns Entity's current coords using the _x and _y attributes
    def get_pos(self):
        return self._x, self._y

    # Scrolls the entity by the specified scroll amount
    def scroll(self, vel):
        dx = vel[0]
        dy = vel[1]
        self._x = self._x + dx
        self._y = self._y + dy
        self.update_pos()

    # Update the rect coords
    def update_pos(self):
        self.rect.x = self._x
        self.rect.y = self._y

    @property
    def image(self):
        img = self.texture.surface
        if hitbox_mode:
            pygame.draw.rect(img, GREEN, (0,0,self._w,self._h), 1)
        return img

    def kill(self):
        remove_name(self._name)
        super().kill()


# Class for all pickable items in game. Items have points and a list of additional effects
# that is applied to the player upon collision. Inherits the Entity class.
class Item(Entity):
    # Class constructor
    def __init__(self, name, x, y, width, height, texture, points, effects = ()):
        # Calls superclass' constructor
        super().__init__(name, x, y, width, height, texture)
        # Private attribute for points that the player collects upon picking this item up
        self._points = points
        # Effect list is a list of 3 element arrays in this form: [type, amount, duration]
        self._effect_list = []
        # If the effect argument in the constructor is not empty, each effect is appended to the
        # effects list.
        if effects != ():
            # If effects consists of sublists, these lists are appended one by one
            if type(effects[0]) == list:
                for effect in effects:
                    self._effect_list.append(effect)
            # Otherwise, the whole list is appended. This is to not have to make one list in a list
            # for the effects argument
            else:
                self._effect_list.append(effects)

    # Method that applies all the item's effects onto the player sprite
    def apply_effect(self, playerSprite):
        if self._effect_list != ():
            for effect in self._effect_list:
                # Money effects add to the money variable
                if effect[0] == Effect.MONEY:
                    add_money(effect[1])
                # Health effects heal the player
                elif effect[0] == Effect.HEALTH:
                    playerSprite.heal(effect[1])
                # Other effects use the Player's add_effect() method
                else:
                    playerSprite.add_effect(effect[0], effect[1], effect[2])
        else:
            print("Warning: No effects in " + self.get_name())

    # Adds the points attribute to the score variable
    def add_points(self):
        add_points(self._points)

    # Method for when this sprite collides with the player
    def whenCollide(self, Player):
        # The item's effects are applied and the points are added to the score
        self.apply_effect(Player)
        self.add_points()

    # Updates sprite, which is called by the Collidables group
    def update(self, collide_list, player):
        # If this sprite is colliding with the player, it calls the whenCollide() method and then
        # kills itself, which removes itself from all groups
        if self.get_name() in collide_list:
            self.whenCollide(player)
            self.kill()
            # Returns nothing in order to break out of the method
            return None


# Item which required more than adding an effect to the player
class SpecialItem(Item):
    # Class constructor
    def __init__(self, name, x, y, width, height, texture, points, life_time, effects = ()):
        super().__init__(name, x, y, width, height, texture, points, effects)
        self._life_time = life_time
        self._start_life_time = life_time

    # Counts down the item's time until it is removed from the level
    def lifeCountdown(self):
        self._life_time -= Clock.get_time()

    # Draws the life timer bar onto sprite image
    def draw_timer(self, image):
        # Sanity Check
        if self._life_time == 0:
            return
        length = (self._w)*(self._life_time/self._start_life_time)
        pygame.draw.rect(image, RED, (0, (self._h/2)-5, length, 10))
    
    @property
    def image(self):
        img = super().image.copy()
        self.draw_timer(img)
        return img


# Class for obstacle sprites.
class Obstacle(Entity):
    # Class constructor
    def __init__(self, name, x, y, width, height, texture, damage, lost_points, knockout_time):
        super().__init__(name, x, y, width, height, texture)
        # The damage inflicted on the player upon collision.
        self._damage = damage
        # Points the player loses upon collision.
        self._points = lost_points
        # The amount of time the player cannot move after collision.
        self._delay = knockout_time

    # Takes health from the player.
    def inflict(self, playerSprite):
        playerSprite.hurt(self._damage)

    # Takes points from the score.
    def take_points(self):
        add_points(-self._points)

    # Knockouts the player for the duration set by the _delay attribute
    def knockout(self, playerSprite):
        playerSprite.add_effect(Effect.KNOCKOUT, None, self._delay)

    # Called upon collision.
    def whenCollide(self, player):
        self.inflict(player)
        self.knockout(player)
        self.take_points()

    # Updates sprite.
    def update(self, collide_list, player):
        # Similar to Item sprites, upon collision the whenCollide method is called and the sprite
        # is killed.
        if self.get_name() in collide_list:
            self.whenCollide(player)
            self.kill()
            return None


# Character class for all character sprites, including the Player
class Character(Entity):
    # Class constructor, with one extra argument: health
    def __init__(self, name, x, y, width, height, texture, health, strength, armor):
        # Calls superclass' constructor
        super().__init__(name, x, y, width, height, texture)
        self._health = health       # Declares the private attribute health
        self._sp = strength         # Declares the strength attribute for attacking
        self._ap = armor            # Declares the armor attribute for defence

    # Method that returns the player's current health
    def get_hp(self):
        return self._health

    # Returns the Character's attack strength
    def get_sp(self):
        return self._sp

    # Returns the Character's defence
    def get_ap(self):
        return self._ap


# Class for Enemy characters who can attack the player
class Enemy(Character):
    # Class constructor
    def __init__(self, name, x, y, width, height, texture, health, strength, armor, damage, win_points, lose_points):
        # Calls Character constructor
        super().__init__(name, x, y, width, height, texture, health, strength, armor)
        self._damage = damage           # Damage dealt when player loses
        self._win_p = win_points        # Points added when player wins
        self._lose_p = lose_points      # Points taken when player loses

    # Method when player wins fight
    def player_win(self):
        add_points(self._win_p)     # Points are added
        self.kill()                 # Kills the enemy sprite

    # Method when player loses fight. Takes playerSprite object
    def player_lose(self, player):
        add_points(-self._lose_p)       # Points are lost
        player.hurt(self._damage)       # Player takes damage
        player.trigger_invincibility(2000)

    def update(self, collide_list, player):
        if self.get_name() in collide_list:
            player.set_opponent(self)

