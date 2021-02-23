from variables import *
hitbox_mode = 0


def update_controls(left, right, jump):
    global left_key
    global right_key
    global jump_key
    left_key, right_key, jump_key = left, right, jump


''' Classes '''
# Base class for all in game sprites, inherited from Sprite from Pygame
class Entity(pygame.sprite.Sprite):
    # The class constructor. Takes the sprite name, position, dimensions and fill colour
    def __init__(self, name, x, y, width, height, color=None, image=None, frames=None, fps=1, current_frame=0):
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
            self._render_mode = "image"
        elif color != None:
            self.image = pygame.Surface((self._w, self._h))
            self.image.fill(color)
            self._render_mode = "color"
        elif frames != None:
            self._frames = frames
            self._animate_fps = fps
            self._current_frame = current_frame
            self.image = frames[current_frame]
            self._render_mode = "animate"
        else:
            self.image = pygame.Surface((self._w, self._h))
            self._render_mode = "black"
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

    # Draws the entity. Used by entities except for entities in groups
    def draw(self):
        Frame.blit(self.image, self.rect)

    # Animates the entity by changing the current frame (Does not draw the frame)
    def animate(self):
        self._current_frame += self._animate_fps * Clock.get_time()/1000
        if self._current_frame >= len(self._frames):
            self._current_frame = 0
        self.image = self._frames[int(self._current_frame)]

    # Returns the rendering mode (color/image/animate/black)
    def get_render_mode(self):
        return self._render_mode

    def kill(self):
        remove_name(self._name)
        super().kill()


# Platform class for collidable platforms (Inherits Entity)
class Platform(Entity):
    # Class constructor required name, position, dimensions and colour
    def __init__(self, name, x, y, width, height, color=None, image=None):
        # Calls the superclass' constructor (i.e. Entity)
        super().__init__(name, x, y, width, height, color=color, image=image)

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
    def __init__(self, name, x, y, width, height, points, effects = (), color=None, image=None, frames=None, fps=1, current_frame=0):
        # Calls superclass' constructor
        super().__init__(name, x, y, width, height, color, image, frames, fps, current_frame)
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
        if self._render_mode == "animate":
            self.animate()
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
    def __init__(self, name, x, y, width, height, points, life_time, effects = (), color=None, image=None, frames=None, fps=1, current_frame=0):
        super().__init__(name, x, y, width, height, points, effects, color, image, frames, fps, current_frame)
        self._life_time = life_time
        self._start_life_time = life_time
        if self._render_mode != "animate":
            self._base_image = self.image.copy()

    # Counts down the item's time until it is removed from the level
    def lifeCountdown(self):
        self._life_time -= Clock.get_time()

    # Draws the life timer bar over the image/frame
    def draw_timer(self):
        length = (self._w)*(self._life_time/self._start_life_time)
        pygame.draw.rect(self.image, RED, (0, (self._h/2)-5, length, 10))


# Special Item which allows the player to move past a certain distance of the level
class ShipDock(SpecialItem):
    # Class constructor
    def __init__(self, name, x, y, width, height, points, wait_time, sail_time, speed, effects = (),
                 dock_color=None, dock_image=None, dock_frames=None, dock_fps=1, dock_current_frame=0,
                 ship_w=0, ship_h=0, ship_color=None, ship_image=None, ship_frames=None, ship_fps=1, ship_current_frame=0):
        super().__init__(name, x, y, width, height, points, wait_time, effects, dock_color, dock_image, dock_frames,
                         dock_fps, dock_current_frame)
        self._sailing = False
        self._sail_time = sail_time
        self._speed = speed
        if ship_image != None:
            ship_w = ship_image.get_width()
            ship_h = ship_image.get_height()
        elif ship_frames != None:
            frame = ship_frames[0]
            ship_w = frame.get_width()
            ship_h = frame.get_height()
        ship_x = x - (ship_w/2) + (width/2)
        self._shipEntity = Entity(name + "Ship", ship_x, 0, ship_w, ship_h, ship_color, ship_image, ship_frames,
                                  ship_fps, ship_current_frame)
        self._ship_alive = True

    # Sets the ship on the bottom of the level
    def ship_on_water(self, sea_level):
        pos = list(self._shipEntity.get_pos())
        pos[1] = sea_level - self._shipEntity.rect.height
        self._shipEntity.set_pos(pos[0], pos[1])

    # Makes ship drawable by adding it into drawables group
    def ship_drawable(self, drawablesGroup):
        drawablesGroup.add(self._shipEntity, layer=1)

    # Counts down journey duration
    def sail_timer(self):
        self._sail_time -= Clock.get_time()

    # Moves the ship depending on its speed
    def move_ship(self):
        pos = list(self._shipEntity.get_pos())
        dt = Clock.get_time()
        pos[0] = pos[0] + (self._speed * (dt/1000))
        self._shipEntity.set_pos(pos[0], pos[1])

    # Makes the ship sail off screen, where it will disappear
    def sail_away(self):
        if self._shipEntity.get_pos()[0] < native_res[0]:
            self.move_ship()
            return False
        else:
            remove_name(self._shipEntity.get_name())
            self._shipEntity.kill()
            self._ship_alive = False
            return True

    # Called when dock life runs out
    def when_life_time_out(self):
        return self.sail_away()

    # Called when the player collides with the dock item
    def whenCollide(self, Player):
        self._sailing = True
        self.add_points()
        Player.disable_movement()
        Player.enable_noclip()
        Player.enable_transparency()
        pos = self._shipEntity.rect.center
        Player.set_pos(pos[0], pos[1])
        Player.board_ship(self)

    # Called while player is sailing on ship
    def while_sail(self, Player):
        pos = self._shipEntity.rect.center
        Player.set_pos(pos[0], pos[1])

    # Called when ship journey ends
    def when_sail_time_out(self, Player):
        self.jump_ship(Player)
        Player.trigger_invincibility(3000)
        return self.sail_away()

    # Forces player off ship
    def jump_ship(self, Player):
        self._sailing = False
        Player.enable_movement()
        Player.disable_noclip()
        Player.disable_transparency()
        self._sail_time = 0

    # Update method
    def update(self, collide_list, player):
        if self._life_time > 0:                         # When dock item not yet expired
            # Checks if player collides with dock if not yet sailing
            if not self._sailing:
                if self.get_name() in collide_list:
                    # Player sails with ship if colliding with dock
                    self.whenCollide(player)
                    self._sailing = True
                # Counts down dock's life time if dock appears on screen
                if self.rect.centerx <= native_res[0]:
                    self.lifeCountdown()
            # If sailing
            else:
                # Keep on sailing if sail time isn't expired
                if self._sail_time > 0:
                    self.move_ship()
                    self.while_sail(player)
                    self.sail_timer()
                # Player leaves Ship and life time set to zero when sail time runs out
                else:
                    self.when_sail_time_out(player)
                    self._life_time = 0
        # Ship sails away and dock kills itself when life time runs out
        else:
            if self.when_life_time_out():
                self.kill()
        # Animates ship if it can
        if self._shipEntity.get_render_mode() == "animate":
            self._shipEntity.animate()
        # Animates dock if it can
        if self.get_render_mode() == "animate":
            self.animate()
        # Draws timer on current image/frame
        self.image = self._base_image.copy()
        self.draw_timer()


# Special Item which can shoot the player across the level
class Cannon(SpecialItem):
    # Class constructor
    def __init__(self, name, x, y, width, height, points, life_time, speed, angle, effects = (), color=None, image=None, frames=None,
                 fps=1, current_frame=0):
        super().__init__(name, x, y, width, height, points, life_time, effects, color, image, frames, fps, current_frame)
        self._speed = speed
        self._angle = (angle/360) * (2*math.pi)
        self._player_flying = False

    # Launches the player at a certain speed and angle
    def launch(self, player):
        vel_h = self._speed * math.cos(self._angle)
        vel_v = -self._speed * math.sin(self._angle)
        player.set_vel(vel_h, vel_v)
        self._player_flying = True

    # Called when player collides with cannon
    def whenCollide(self, Player):
        self.add_points()
        Player.disable_movement()
        Player.enable_noclip()
        Player.high_speed_caps()
        self.launch(Player)

    # Called when player starts to fall (dy is positive)
    def when_player_falling(self, player):
        player.disable_noclip()
        player.trigger_invincibility(100)

    # Called when player lands on platform (dy = 0)
    def when_player_land(self, player):
        player.enable_movement()
        player.normal_speed_caps()
        player.trigger_invincibility(3000)
        self.kill()

    # Update method
    def update(self, collide_list, player):
        #
        if self._life_time > 0:
            if not self._player_flying:
                if self.get_name() in collide_list:
                    self.whenCollide(player)
                self.lifeCountdown()
            else:
                player_dy = player.get_vel()[1]
                if player_dy > 0:
                    self.when_player_falling(player)
                elif player_dy == 0:
                    self.when_player_land(player)
        #
        else:
            self.kill()
        # Draws timer on current image/frame
        self.image = self._base_image.copy()
        self.draw_timer()


# Class for obstacle sprites.
class Obstacle(Entity):
    # Class constructor
    def __init__(self, name, x, y, width, height, damage, lost_points, knockout_time, color=None, image=None, frames=None, fps=1, current_frame=0):
        super().__init__(name, x, y, width, height, color, image, frames, fps, current_frame)
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


# Class for the chasing wave enemy
class Tsunami(Obstacle):
    # Class constructor
    def __init__(self, name, x, y, width, height, color, speed, delay, image=None, frames=None, fps=1, current_frame=0):
        super().__init__(name, x, y, width, height, 9999, 0, 0, color, image, frames, fps, current_frame)
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
    # TODO: Change effect names to enum symbols
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
    # TODO: Change effect names to enum symbols
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
    def set_scroll(self, resolution):
        center = [resolution[0]/2, resolution[1]/2]
        dx = self._x - center[0]
        dy = self._y - center[1]
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
                if type(sprite).__name__ in ("Obstacle", "Enemy"):
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
                if type(sprite).__name__ == "Tsunami":
                    waveGroup.add(sprite)
            collide_list = self.collide_trigger(waveGroup, playerGroup)
        if self._transparent:
            self.image.set_alpha(0)
        return collide_list
