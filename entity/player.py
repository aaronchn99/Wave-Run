from var.variables import *
from .Sprites import Character, Obstacle, Enemy
from .wave import Tsunami

def update_controls(left, right, jump):
    global left_key
    global right_key
    global jump_key
    left_key, right_key, jump_key = left, right, jump


''' Player class for the player sprite. Only instanced in one variable '''
class playerClass(Character):
    ''' Class constructor.  Takes all arguments from Character plus acceleration and a
        list of maximum speeds. '''
    def __init__(self, name, x, y, width, height, color, health, accel, max_speeds, strength, armor):
        super().__init__(name, x, y, width, height, color, health, strength, armor)      # Calls the superclass constructor
        # Player attributes are declared as private variables
        self._max_hp = health
        self._accel = accel
        self._max_dx = max_speeds[0][0]
        self._min_dx = max_speeds[0][1]
        self._max_dy = max_speeds[1][0]
        self._min_dy = max_speeds[1][1]
        self._max_speeds = max_speeds
        self._start_values = [self._accel, self._min_dy]
        self._trait_lvls = {"hp":0, "speed":0, "acc":0, "str":0, "def":0}
        self._dx = 0
        self._dy = 0
        self._hold_duration = 350
        self._can_jump = False
        self._can_move = True
        self._opponent = None
        self._ship = None
        self._noclip = False
        self._invincible = False
        self._invincible_time = 0
        self._transparent = False
        self._active_effects = []
        self._frame = self.image

    ''' Method that moves the player depending on the user's inputs.  Takes the inputs dict '''
    def user_move(self, inputs, Platforms):
        platform_list = []                  # A list of all the Platform sprites' rect objects
        for platform in Platforms:
            platform_list.append(platform.rect)

        dt = Clock.get_time()/1000
        ''' Horizontal movement '''
        if left_key in inputs["key"]:
            if self._dx > 0:
                self._dx = 0                # If the player was moving to the right, the player is stopped
            elif self._dx > self._min_dx:
                self._dx -= self._accel * dt     # Otherwise, the player accelerates to the left
            elif self._dx <= self._min_dx:
                self._dx = self._min_dx     # Sets player speed to the maximum speed if it exceeds it
        if right_key in inputs["key"]:
            if self._dx < 0:
                self._dx = 0                # If the player is moving to the left, it stops
            elif self._dx < self._max_dx:
                self._dx += self._accel * dt     # Otherwise, the player is accelerated to the right
            elif self._dx >= self._max_dx:
                self._dx = self._max_dx     # Sets player speed to the maximum speed if it exceeds it

        if self._can_move:                  # Checks if player can move
            # If neither left and right keys are pressed, the player stops moving horizontally
            if left_key not in inputs["key"] and right_key not in inputs["key"]:
                self._dx = 0
            # Likewise, if left and right keys are pressed, the player stops moving horizontally
            elif left_key in inputs["key"] and right_key in inputs["key"]:
                self._dx = 0
        self.set_pos(self._x + self._dx * dt, self._y)       # The horizontal movement is applied

        # Platforms collidable if noclip turned off
        if not self._noclip:
            # Collision code
            for platform in platform_list:      # Iterates through each platform rect
                # Tests if the player is moving horizontally and colliding with the selected platform
                if self.rect.colliderect(platform) and self._dx != 0:
                    if self._dx < 0:                                                # If player moves to the left
                        self.set_pos(platform.right, self._y)                       # Moved to the right edge of platform
                    if self._dx > 0:                                                # If player moves to the right
                        self.set_pos(platform.left - self.rect.width, self._y)      # Moved to the left edge of platform
                    if self.rect.collidelist(platform_list) == -1:                  # If player overlaps any platform
                        self.set_vel(0, self._dy)                                   # Stops moving horizontally


        ''' Vertical movement '''
        Ghost = self.rect.move(0, 1)                                # A copy of the player's rect, but moved 1 pixel down

        if jump_key in inputs["key"] and self._can_jump:            # Tests if jump key is pressed and player can jump
            # If hold duration more than 0, player jumps
            if self._hold_duration > 0:
                self._dy = self._min_dy
                self._hold_duration -= Clock.get_time()
            elif self._hold_duration <= 0:
                self._can_jump = False                              # If hold duration runs out, player can't jump
            if Ghost.move(0, -2).collidelist(platform_list) != -1:
                self._can_jump = False                              # If hitting a ceiling, player can't jump
        else:                                                       # If jump key not pressed or player can't jump
            self._hold_duration = 0                                 # Hold duration set to 0
            if self._dy < self._max_dy and Ghost.collidelist(platform_list) == -1:
                self._dy += g * dt                                       # Player falls if not on platform
            if self._dy >= self._max_dy:
                self._dy = self._max_dy                # Vertical velocity set to max velocity if exceeded

        # If player on platform and jump key not pressed, hold duration is reset and player can jump
        if Ghost.move(0, self._dy * dt).collidelist(platform_list) != -1 and jump_key not in inputs["key"]:
            self._hold_duration = 350
            self._can_jump = True

        self.set_pos(self._x, self._y + self._dy * dt)           # Vertical movement is applied

        # Platforms collidable if noclip turned off
        if not self._noclip:
            # Collision code
            for platform in platform_list:
                # If player is moving upwards and overlapping the platform
                if self._dy < 0 and self.rect.colliderect(platform):
                    new_y = platform.bottom                     # Player moved to bottom of platform
                    self.set_pos(self._x, new_y)
                    self.set_vel(self._dx, g * dt)                   # Player set to fall
                # If the player is moving downwards and overlapping the platform
                elif self._dy >= 0 and self.rect.colliderect(platform):
                    new_y = platform.top - self.rect.height     # Player set to top of platform
                    self.set_pos(self._x, new_y)
                    self.set_vel(self._dx, 0)                   # Player stops moving vertically


        # This prevents the player from moving off the screen
        if self._x < 0:
            self._x = 0
            self._dx = 0
        self.update_pos()

    # Enables player's ability to move
    def enable_movement(self):
        self._can_move = True

    # Disables player's ability to move
    def disable_movement(self):
        self._can_move = False

    # Enables player's ability to noclip
    def enable_noclip(self):
        self._noclip = True

    # Disables player's ability to noclip
    def disable_noclip(self):
        self._noclip = False

    # Enables player invisibility
    def enable_transparency(self):
        self._transparent = True
        self.image.set_alpha(0)

    # Disables player invisibility
    def disable_transparency(self):
        self._transparent = False
        self.image.set_alpha(255)

    # Allows the player to move at high velocities (When the player is launched)
    def high_speed_caps(self):
        self._max_dx, self._min_dx, self._max_dy, self._min_dy = 99999, 99999, 99999, 99999

    # Resets the speed caps to normal
    def normal_speed_caps(self):
        self._max_dx = self._max_speeds[0][0]
        self._min_dx = self._max_speeds[0][1]
        self._max_dy = self._max_speeds[1][0]
        self._min_dy = self._max_speeds[1][1]

    # Returns a tuple of the player's position plus dimensions
    def get_dim(self):
        return self._x, self._y, self.rect.width, self.rect.height

    # Returns the velocity of the player in perpendicular components
    def get_vel(self):
        return self._dx, self._dy

    # Method that takes the new velocity and sets the player velocity to this new velocity
    def set_vel(self, new_dx, new_dy):
        self._dx = new_dx
        self._dy = new_dy

    # Method for checking collision between the player and other sprites in the collidables
    # group. Returns the names of sprites colliding with the player
    def collide_trigger(self, collidables, playerGroup):
        collide_objs = pygame.sprite.groupcollide(playerGroup, collidables, False, False)
        # The names of each colliding sprite is put in a list and returned
        obj_names = []
        if collide_objs != {}:
            for obj in collide_objs[self]:
                obj_names.append(obj.get_name())
        return obj_names

    # Heals the player by the amount of hearts passed as the argument
    def heal(self, hearts):
        # This caps the player's health at the max_hp attribute
        if self._health + hearts > self._max_hp:
            self._health = self._max_hp
        # Only heals if the player's hp has not hit zero
        elif self._health > 0:
            self._health += hearts

    # Return max hp
    def get_max_hp(self):
        return self._max_hp

    # Damages the player by the amount passed into the function
    def hurt(self, dmg):
        self._health -= dmg

    # Sets the current opponent
    def set_opponent(self, enemy):
        self._opponent = enemy

    # Returns the current opponent
    def get_opponent(self):
        return self._opponent

    # Adds the boarding ship to the ship attribute
    def board_ship(self, ship_dock):
        self._ship = ship_dock

    # Removes the ship from the ship attribute
    def jump_ship(self):
        self._ship.jump_ship(self)

    # Checks if the player is sailing on a ship
    def is_sailing(self):
        if self._ship != None:
            return True
        else:
            return False

    # Activates and adds an effect to the active effects list attribute. Takes the effect type,
    # effect amount/strength and the duration of the effect (In milliseconds). However, some
    # effects do not use all the arguments so unused arguments are passed as None.
    def add_effect(self, effect_type, strength, duration):
        # Applies the knockout effect
        if effect_type == Effect.KNOCKOUT:
            # The player stops moving and the effect is added to the list
            self._accel = 0
            self._min_dy = 0
            self._dx = 0
            self._dy = 0
            self._active_effects.append([effect_type, strength, duration])
        # Increases the player's max speeds
        elif effect_type == Effect.FAST:
            # The maximum speeds are increased by the strength value and the effect is added
            self._min_dx -= strength
            self._max_dx += strength
            self._active_effects.append([effect_type, strength, duration])
        # Reduces max speeds
        elif effect_type == Effect.SLOW:
            self._min_dx += strength
            self._max_dx -= strength
            self._active_effects.append([effect_type, strength, duration])

    # Updates each active effect on the player by subtracting time from the duration property
    # of each effect, then reversing and removing expired effects
    def update_effect(self):
        # Gets the time passed since last tick
        dt = Clock.get_time()
        # If there are currently any active effects
        if self._active_effects != []:
            i = 0
            # Selects an effect in the list consecutively
            while i < len(self._active_effects):
                # Takes the time passed from the duration property
                self._active_effects[i][2] -= dt
                # If the selected effect has expired
                if self._active_effects[i][2] <= 0:
                    # If the effect is a knockout effect
                    if self._active_effects[i][0] == Effect.KNOCKOUT:
                        # Sets the player acceleration and max upward speed to normal
                        self._accel = self._start_values[0]
                        self._min_dy = self._start_values[1]
                    elif self._active_effects[i][0] == Effect.FAST:
                        # Decreases maximum speeds by the strength property value
                        self._max_dx -= self._active_effects[i][1]
                        self._min_dx += self._active_effects[i][1]
                    elif self._active_effects[i][0] == Effect.SLOW:
                        self._max_dx += self._active_effects[i][1]
                        self._min_dx -= self._active_effects[i][1]
                    # Removes effect from the list
                    del self._active_effects[i]
                i += 1

    # Returns the active effects list
    def get_effects(self):
        return self._active_effects

    # Flushes the active effects list
    def clear_effects(self):
        for effect in self._active_effects:
            effect[2] = 0
        self.update_effect()

    # Returns the list of traits and their levels
    def get_trait_lvls(self):
        return self._trait_lvls

    # Upgrades a specified trait by a specified number of levels
    def upgrade_trait(self, trait, amount):
        for i in range(amount):
            if trait == "hp":
                self._max_hp += upgrades["hp"]
            elif trait == "speed":
                self._max_dx = self._max_dx * upgrades["speed"]
                self._min_dx = self._min_dx * upgrades["speed"]
            elif trait == "acc":
                self._accel = self._accel * upgrades["acc"]
                self._start_values[0] = self._accel
            elif trait == "str":
                self._sp = self._sp * upgrades["str"]
            elif trait == "def":
                self._ap += upgrades["def"]
            else:
                print("Error: Trait" + trait + " not a valid trait")
            self._trait_lvls[trait] += 1

    # Sets the scroll amount depending on how far away the player is from the center of
    # the screen
    def set_scroll(self, cam_area):
        center = (cam_area[0]/2, cam_area[1]/2)
        dx = self._x + (self._w/2) - center[0]
        dy = self._y + (self._h/2) - center[1]
        return -dx, -dy

    # Starts the player's invincibility mode
    def trigger_invincibility(self, time):
        self._invincible = True             # Sets the invincible flag to true
        self._invincible_time = time        # Sets the duration of invincibility

    # Disables invincibility
    def disable_invincibility(self):
        self._invincible = False
        self._invincible_time = 0

    # Returns whether the player is invincible or not
    def get_invincibility(self):
        return self._invincible

    # Method to update the player sprite. Used by playerGroup. Returns the list of colliding
    # sprites with the player
    def update(self, inputs, collidables, platforms, playerGroup):
        if not self._can_move:
            for key in (left_key, right_key, jump_key):
                if key in inputs["key"]:
                    inputs["key"].remove(key)
        self.user_move(inputs, platforms)
        self.update_effect()
        if self._invincible:
            if self.image.get_alpha() == 255:
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)
            noDamageGroup = collidables.copy()
            for sprite in noDamageGroup:
                if (isinstance(sprite, Obstacle) and not isinstance(sprite, Tsunami)) \
                        or isinstance(sprite, Enemy):
                    noDamageGroup.remove(sprite)
            collide_list = self.collide_trigger(noDamageGroup, playerGroup)
            self._invincible_time -= Clock.get_time()
            if self._invincible_time <= 0:
                self._invincible = False
        else:
            self.image.set_alpha(255)
            collide_list = self.collide_trigger(collidables, playerGroup)
        if self._noclip:
            waveGroup = pygame.sprite.Group()
            for sprite in collidables:
                if isinstance(sprite, Tsunami):
                    waveGroup.add(sprite)
            collide_list = self.collide_trigger(waveGroup, playerGroup)
        if self._transparent:
            self.image.set_alpha(0)
        return collide_list