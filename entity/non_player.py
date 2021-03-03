import random as rand

from var.variables import *
from .Sprites import Item, Obstacle, SpecialItem, Enemy, Entity


''' Subclasses for each type of Item '''
# Coin sprites, awarding the player 1 Gold and between 5-20 points
class Coin(Item):
    def __init__(self, name, x, y, width, height, \
        increasers=(1,1), decreasers=(1,1), \
        color=None, image=None, frames=None, fps=1, current_frame=0,
        **kwargs):
        super().__init__(name, x, y, width, height, rand.randint(5, 20), \
            [Effect.MONEY, 1, 0], color, image, frames, fps, current_frame)


# Treasure Chests, awards player 20 Gold and between 25-50 points
class Treasure(Item):
    def __init__(self, name, x, y, width, height, \
        increasers=(1,1), decreasers=(1,1), \
        color=None, image=None, frames=None, fps=1, current_frame=0,
        **kwargs):
        super().__init__(name, x, y, width, height, rand.randint(25, 50), \
            [Effect.MONEY, 20, 0], color, image, frames, fps, current_frame)


# Bandage item, heals player by 1 hp (Half heart)
class Bandage(Item):
    def __init__(self, name, x, y, width, height, \
        increasers=(1,1), decreasers=(1,1), \
        color=None, image=None, frames=None, fps=1, current_frame=0,
        **kwargs):
        super().__init__(name, x, y, width, height, 0, \
            [Effect.HEALTH, 1, 0], color, image, frames, fps, current_frame)


# Medical Chest, heals player to maximum hp
class Medkit(Item):
    def __init__(self, name, x, y, width, height, \
        increasers=(1,1), decreasers=(1,1), \
        color=None, image=None, frames=None, fps=1, current_frame=0,
        **kwargs):
        super().__init__(name, x, y, width, height, 0, \
            [Effect.HEALTH, 999, 0], color, image, frames, fps, current_frame)


# Crate of Rum, awards 50-100 points and heals 2 hp, but slows player down
class Rum(Item):
    def __init__(self, name, x, y, width, height, \
        increasers=(1,1), decreasers=(1,1), \
        color=None, image=None, frames=None, fps=1, current_frame=0,
        **kwargs):
        effects = [
            [Effect.HEALTH, 2, 0],
            [Effect.SLOW, 150, round(10000*increasers[0]*increasers[1])]
        ]
        super().__init__(name, x, y, width, height, rand.randint(50, 100), \
            effects, color, image, frames, fps, current_frame)

Item.subclass_map = {
    "Coin": Coin,
    "Treasure": Treasure,
    "Bandage": Bandage,
    "Medkit": Medkit,
    "Rum": Rum,
}


''' Subclasses for each type of Obstacle '''
# Anchor Obstacle, damages player by 1 hp, takes 200 points away and 
# knockouts player for 4 seconds (damage and knockout adjusted by difficulty increasers)
class Anchor(Obstacle):
    def __init__(self, name, x, y, width, height, \
        increasers=(1,1), decreasers=(1,1), \
        color=None, image=None, frames=None, fps=1, current_frame=0,
        **kwargs):
        damage = round(1 * increasers[0] * increasers[1])
        lost_points = 200
        knockout_time = round(4000 * increasers[0] * increasers[1])
        super().__init__(name, x, y, width, height, damage, lost_points, knockout_time, \
            color, image, frames, fps, current_frame)


# Barrel Obstacle, 1 hp damage, takes 200 points and 3 seconds knockout
# (Damage and knockout adjusted by difficulty increasers)
class Barrel(Obstacle):
    def __init__(self, name, x, y, width, height, \
        increasers=(1,1), decreasers=(1,1), \
        color=None, image=None, frames=None, fps=1, current_frame=0,
        **kwargs):
        damage = round(1 * increasers[0] * increasers[1])
        lost_points = 200
        knockout_time = round(3000 * increasers[0] * increasers[1])
        super().__init__(name, x, y, width, height, damage, lost_points, knockout_time, \
            color, image, frames, fps, current_frame)


# Crate Obstacle, 1 hp damage, 200 points taken and 2 second knockout
# (Damage and knockout adjusted by difficulty increasers)
class Crate(Obstacle):
    def __init__(self, name, x, y, width, height, \
        increasers=(1,1), decreasers=(1,1), \
        color=None, image=None, frames=None, fps=1, current_frame=0,
        **kwargs):
        damage = round(1 * increasers[0] * increasers[1])
        lost_points = 200
        knockout_time = round(2000 * increasers[0] * increasers[1])
        super().__init__(name, x, y, width, height, damage, lost_points, knockout_time, \
            color, image, frames, fps, current_frame)


''' Subclasses for each type of SpecialItem '''
# Special Item which allows the player to move past a certain distance of the level
class ShipDock(SpecialItem):
    # Class constructor
    def __init__(self, name, x, y, width, height, points, wait_time, sail_time, speed,
            increasers=(1,1), decreasers=(1,1), effects = (),
            dock_color=None, dock_image=None, dock_frames=None, dock_fps=1, dock_current_frame=0,
            ship_w=0, ship_h=0, ship_color=None, ship_image=None, ship_frames=None, ship_fps=1, ship_current_frame=0,
            **kwargs):
        # Waiting and Sailing duration reduced by difficulty decreasers
        wait_time = round(wait_time * decreasers[0] * decreasers[1])
        sail_time = round(sail_time * decreasers[0] * decreasers[1])
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
        self.effects = effects

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
        for effect in self.effects:
            Player.add_effect(*effect)
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
    def __init__(self, name, x, y, width, height, points, fuse_time, speed, angle,
            increasers=(1,1), decreasers=(1,1), effects = (),
            color=None, image=None, frames=None, fps=1, current_frame=0,
            **kwargs):
        # Fuse duration and speed reduced by difficulty decreasers
        fuse_time = round(fuse_time * decreasers[0] * decreasers[1])
        speed = round(speed * decreasers[0] * decreasers[1])
        super().__init__(name, x, y, width, height, points, fuse_time, effects, color, image, frames, fps, current_frame)
        self._speed = speed
        self._angle = (angle/360) * (2*math.pi)
        self._player_flying = False
        self.effects = effects

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
        for effect in self.effects:
            player.add_effect(*effect)
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


# Special Item that speeds the player (Also changes player sprite to a mounted player)
# Speed duration reduced by difficulty decreasers
class Horse(SpecialItem):
    def __init__(self, name, x, y, width, height, points, \
        increasers=(1,1), decreasers=(1,1), \
        color=None, image=None, frames=None, fps=1, current_frame=0,
        **kwargs):
        life_time = 0
        effects = [Effect.FAST, 240, round(15000*decreasers[0]*decreasers[1])]
        super().__init__(name, x, y, width, height, points, life_time, effects, \
            color, image, frames, fps, current_frame)


''' Subclasses for each type of Enemy '''
# 
class Pirate(Enemy):
    def __init__(self, name, x, y, width, height,
        increasers=(1,1), decreasers=(1,1),
        color=None, image=None, frames=None, fps=1, current_frame=0,
        **kwargs):
        health, strength, armor, damage, win_points, lose_points = 3, 2, 0.4, 2, 100, 300
        color=(0,0,0)
        super().__init__(name, x, y, width, height, color, health, strength, armor, damage, win_points, lose_points)


class Redcoat(Enemy):
    def __init__(self, name, x, y, width, height,
        increasers=(1,1), decreasers=(1,1),
        color=None, image=None, frames=None, fps=1, current_frame=0,
        **kwargs):
        health, strength, armor, damage, win_points, lose_points = 3, 2, 0.4, 2, 100, 300
        color=(255,0,0)
        super().__init__(name, x, y, width, height, color, health, strength, armor, damage, win_points, lose_points)


class Parrot(Enemy):
    def __init__(self, name, x, y, width, height,
        increasers=(1,1), decreasers=(1,1),
        color=None, image=None, frames=None, fps=1, current_frame=0,
        **kwargs):
        health, strength, armor, damage, win_points, lose_points = 3, 2, 0.4, 2, 100, 300
        color=(0,255,0)
        super().__init__(name, x, y, width, height, color, health, strength, armor, damage, win_points, lose_points)


class Skeleton(Enemy):
    def __init__(self, name, x, y, width, height,
        increasers=(1,1), decreasers=(1,1),
        color=None, image=None, frames=None, fps=1, current_frame=0,
        **kwargs):
        health, strength, armor, damage, win_points, lose_points = 3, 2, 0.4, 2, 100, 300
        color=(255,255,255)
        super().__init__(name, x, y, width, height, color, health, strength, armor, damage, win_points, lose_points)