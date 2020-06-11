from variables import *
hitbox_mode = False


def update_controls(left, right, jump):
    global left_key
    global right_key
    global jump_key
    left_key, right_key, jump_key = left, right, jump




''' Classes '''
# Base class for all in game sprites, inherited from Sprite from Pygame
class Entity(pygame.sprite.Sprite):



    # The class constructor. Takes the sprite name, position, dimensions and fill colour
    def __init__(self, name, x, y, width, height, color=None, image=None):
        # Calls the superclass' constructor (i.e. Sprite class)
        super().__init__()
        # Positional and dimensional attributes
        self._w, self._h = width, height
        self._x, self._y = x, y
        # The entity's name is assigned. Used for sprite identification
        self._name = check_name(name)   # check_name called to check uniqueness
        # An image of the Sprite is assigned by creating a new Surface object and filling
        # it with the specified colour
        if image != None:
            self.image = image
            self.image = pygame.transform.scale(self.image, (self._w, self._h))
        elif color != None:
            self.image = pygame.Surface((self._w, self._h))
            self.image.fill(color)
        else:
            self.image = pygame.Surface((self._w, self._h))
        if hitbox_mode:
            pygame.draw.rect(self.image, GREEN, (0,0,self._w,self._h), 1)
        # The Entity object's rect attribute is a Rect object with the dimensions of the
        # above image. Used to hold and position the sprite
        self.rect = self.image.get_rect()
        # The rect is positioned at the specified coordinates
        self.rect.x, self.rect.y = self._x, self._y



    # Method that returns the entity's name
    def get_name(self):
        return self._name



    # Sets the Entity's position
    def set_pos(self, x, y):
        self._x, self._y = x, y



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



    # Draws the entity. Used by entities except for entities in groups
    def draw(self):
        Frame.blit(self.image, self.rect)




# Platform class for collidable platforms (Inherits Entity)
class Platform(Entity):



    # Class constructor required name, position, dimensions and colour
    def __init__(self, name, x, y, width, height, color):
        # Calls the superclass' constructor (i.e. Entity)
        super().__init__(name, x, y, width, height, color)



    # Method for executing scripts upon collision with the Player
    def whenCollide(self):
        pass



    # Update method which overrides the one from the Sprite class. Takes one argument: the
    # list names of sprites that collided with the Player
    def update(self, collide_list, _):
        # If the Platform's name is in the list, it will call the whenCollide method
        if self._name in collide_list:
            self.whenCollide()




# Class for all pickable items in game. Items have points and a list of additional effects
# that is applied to the player upon collision. Inherits the Entity class.
class Item(Entity):



    # Class constructor
    def __init__(self, name, x, y, width, height, points, effects = (), color=None, image=None):
        # Calls superclass' constructor
        super().__init__(name, x, y, width, height, color, image)
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
        for effect in self._effect_list:
            # Money effects add to the money variable
            if effect[0] == "money":
                add_money(effect[1])
            # Health effects heal the player
            elif effect[0] == "health":
                playerSprite.heal(effect[1])
            # Other effects use the Player's add_effect() method
            else:
                playerSprite.add_effect(effect[0], effect[1], effect[2])



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




# Class for obstacle sprites.
class Obstacle(Entity):



    # Class constructor
    def __init__(self, name, x, y, width, height, damage, lost_points, knockout_time, color=None, image=None):
        super().__init__(name, x, y, width, height, color, image)
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
        playerSprite.add_effect("knockout", None, self._delay)



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




# Class for the chasing wave enemy
class Tsunami(Obstacle):



    # Class constructor
    def __init__(self, name, x, y, width, height, color, speed, delay):
        super().__init__(name, x, y, width, height, 9999, 0, 0, color)
        self._speed = speed     # How far the wave moves per tick
        self._delay = delay     # The delay before the wave starts moving
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




# Character class for all character sprites, including the Player
class Character(Entity):



    # Class constructor, with one extra argument: health
    def __init__(self, name, x, y, width, height, color, health, strength, armor):
        # Calls superclass' constructor
        super().__init__(name, x, y, width, height, color)
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
    def __init__(self, name, x, y, width, height, color, health, strength, armor, damage, win_points, lose_points):
        # Calls Character constructor
        super().__init__(name, x, y, width, height, color, health, strength, armor)
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
        self._start_values = [self._accel, self._min_dy]
        self._trait_lvls = {"hp":0, "speed":0, "acc":0, "str":0, "def":0}
        self._dx = 0
        self._dy = 0
        self._hold_duration = 350
        self._can_jump = False
        self._opponent = None
        self._invincible = False
        self._invincible_time = 0
        self._active_effects = []
        self._frame = self.image



    ''' Method that moves the player depending on the user's inputs.  Takes the inputs dict '''
    def user_move(self, inputs, Platforms):
        platform_list = []                  # A list of all the Platform sprites' rect objects
        for platform in Platforms:
            platform_list.append(platform.rect)


        ''' Horizontal movement '''
        if left_key in inputs["key"]:
            if self._dx > 0:
                self._dx = 0                # If the player was moving to the right, the player is stopped
            elif self._dx > self._min_dx:
                self._dx -= self._accel     # Otherwise, the player accelerates to the left
            elif self._dx <= self._min_dx:
                self._dx = self._min_dx     # Sets player speed to the maximum speed if it exceeds it
        if right_key in inputs["key"]:
            if self._dx < 0:
                self._dx = 0                # If the player is moving to the left, it stops
            elif self._dx < self._max_dx:
                self._dx += self._accel     # Otherwise, the player is accelerated to the right

            elif self._dx >= self._max_dx:
                self._dx = self._max_dx     # Sets player speed to the maximum speed if it exceeds it

        # If neither left and right keys are pressed, the player stops moving horizontally
        if left_key not in inputs["key"] and right_key not in inputs["key"]:
            self._dx = 0
        # Likewise, if left and right keys are pressed, the player stops moving horizontally
        elif left_key in inputs["key"] and right_key in inputs["key"]:
            self._dx = 0
        self.move_to(self._x + self._dx, self._y)       # The horizontal movement is applied

        # Collision code
        for platform in platform_list:      # Iterates through each platform rect
            # Tests if the player is moving horizontally and colliding with the selected platform
            if self.rect.colliderect(platform) and self._dx != 0:
                if self._dx < 0:                                                # If player moves to the left
                    self.move_to(platform.right, self._y)                       # Moved to the right edge of platform
                if self._dx > 0:                                                # If player moves to the right
                    self.move_to(platform.left - self.rect.width, self._y)      # Moved to the left edge of platform
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
                self._dy += g                                       # Player falls if not on platform

        # If player on platform and jump key not pressed, hold duration is reset and player can jump
        if Ghost.move(0, self._dy).collidelist(platform_list) != -1 and jump_key not in inputs["key"]:
            self._hold_duration = 350
            self._can_jump = True

        self.move_to(self._x, self._y + self._dy)           # Vertical movement is applied

        # Collision code
        for platform in platform_list:
            # If player is moving upwards and overlapping the platform
            if self._dy < 0 and self.rect.colliderect(platform):
                new_y = platform.bottom                     # Player moved to bottom of platform
                self.move_to(self._x, new_y)
                self.set_vel(self._dx, g)                   # Player set to fall
            # If the player is moving downwards and overlapping the platform
            elif self._dy > 0 and self.rect.colliderect(platform):
                new_y = platform.top - self.rect.height     # Player set to top of platform
                self.move_to(self._x, new_y)
                self.set_vel(self._dx, 0)                   # Player stops moving vertically


        # This prevents the player from moving off the screen
        if self._x < 0:
            self._x = 0
            self._dx = 0
        self.update_pos()



    # Returns a tuple of the player's position plus dimensions
    def get_dim(self):
        return self._x, self._y, self.rect.width, self.rect.height



    # Method which takes x and y coordinates and moves the player's rect object
    # to this set of coordinates
    def move_to(self, x, y):
        self._x = x
        self._y = y
        self.update_pos()



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



    # Activates and adds an effect to the active effects list attribute. Takes the effect type,
    # effect amount/strength and the duration of the effect (In milliseconds). However, some
    # effects do not use all the arguments so unused arguments are passed as None.
    def add_effect(self, effect_type, strength, duration):
        # Applies the knockout effect if effect_type is "knockout"
        if effect_type == "knockout":
            # The player stops moving and the effect is added to the list
            self._accel = 0
            self._min_dy = 0
            self._dx = 0
            self._dy = 0
            self._active_effects.append([effect_type, strength, duration])
        # Increases the player's max speeds if the effect_type is "fast"
        elif effect_type == "fast":
            # The maximum speeds are increased by the strength value and the effect is added
            self._min_dx -= strength
            self._max_dx += strength
            self._active_effects.append([effect_type, strength, duration])
        # Reduces max speeds if the effect_type is "slow"
        elif effect_type == "slow":
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
                    if self._active_effects[i][0] == "knockout":
                        # Sets the player acceleration and max upward speed to normal
                        self._accel = self._start_values[0]
                        self._min_dy = self._start_values[1]
                    elif self._active_effects[i][0] == "fast":
                        # Decreases maximum speeds by the strength property value
                        self._max_dx -= self._active_effects[i][1]
                        self._min_dx += self._active_effects[i][1]
                    elif self._active_effects[i][0] == "slow":
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
                self._max_hp += 1
            elif trait == "speed":
                self._max_dx = self._max_dx * 1.5
                self._min_dx = self._min_dx * 1.5
            elif trait == "acc":
                self._accel = self._accel * 1.5
                self._start_values[0] = self._accel
            elif trait == "str":
                self._sp = self._sp * 2
            elif trait == "def":
                self._ap += 0.05
            else:
                print("Error: Trait" + trait + " not a valid trait")
            self._trait_lvls[trait] += 1



    # Sets the scroll amount depending on how far away the player is from the center of
    # the screen
    def set_scroll(self, resolution):
        center = [resolution[0]/2, resolution[1]/2]
        dx = self._x - center[0]
        dy = self._y - center[1]
        return -dx, -dy



    # Starts the player's invincibility mode
    def trigger_invincibility(self, time):
        self._invincible = True             # Sets the invincible flag to true
        self._invincible_time = time        # Sets the duration of invincibility



    # Returns whether the player is invincible or not
    def get_invincibility(self):
        return self._invincible



    # Method to update the player sprite. Used by playerGroup. Returns the list of colliding
    # sprites with the player
    def update(self, inputs, collidables, platforms, playerGroup):
        self.user_move(inputs, platforms)
        self.update_effect()
        if self._invincible:
            if self.image.get_alpha() == 255:
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)
            noDamageGroup = collidables.copy()
            for sprite in noDamageGroup:
                if type(sprite).__name__ in ("Obstacle", "Enemy"):
                    noDamageGroup.remove(sprite)
            collide_list = self.collide_trigger(noDamageGroup, playerGroup)
            self._invincible_time -= Clock.get_time()
            if self._invincible_time <= 0:
                self._invincible = False
        else:
            self.image.set_alpha(255)
            collide_list = self.collide_trigger(collidables, playerGroup)
        return collide_list



