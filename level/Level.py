import json, pygame, enum, os, copy

from entity.wave import Tsunami
from entity.platforms import Platform
from entity.non_player import *

from images.Image import *

from var.variables import Effect

# Load spritesheets (TODO: Temporary, to be replaced by loader function using config file)
rootdir = os.path.dirname(os.path.dirname(__file__))
EntitySheet = pygame.image.load(os.path.join(rootdir, "images", "ItemObstacles.png"))
CoinSheet = pygame.image.load(os.path.join(rootdir, "images", "Coin.png"))
# Textures
CoinAnimation = AnimatedTexture(CoinSheet, 8, (20,20), 8)
TreasureTexture = ImageTexture(crop(EntitySheet, (40, 0), (40, 40)))
BandageTexture = ImageTexture(crop(EntitySheet, (80, 0), (40, 40)))
MedkitTexture = ImageTexture(crop(EntitySheet, (0, 40), (40, 40)))
RumTexture = ImageTexture(crop(EntitySheet, (40, 40), (40, 40)))
AnchorTexture = ImageTexture(crop(EntitySheet, (0, 80), (40, 40)))
BarrelTexture = ImageTexture(crop(EntitySheet, (40, 80), (40, 40)))
CrateTexture = ImageTexture(crop(EntitySheet, (80, 80), (40, 40)))
HorseTexture = ImageTexture(crop(EntitySheet, (80, 40), (40, 40)))
DockTexture = ColorTexture(GREEN)
ShipTexture = ColorTexture(BLUE)
ShipTexture.scale(400, 200)
CannonTexture = ColorTexture(YELLOW)
PirateTexture = ColorTexture((0, 0, 0))
RedcoatTexture = ColorTexture((255, 0, 0))
ParrotTexture = ColorTexture((0, 255, 0))
SkeletonTexture = ColorTexture((255, 255, 255))


# String to Effect mapping
effect_map = {
    "FAST": Effect.FAST,
    "SLOW": Effect.SLOW,
    "KNOCKOUT": Effect.KNOCKOUT,
    "DIZZY": Effect.DIZZY,
}

# Maintains level data (e.g. level size, platform and sprite info)
# Used to build level
class Level:
    # Takes path of level data file (i.e. ldtkl file)
    def __init__(self, path):
        # Full directory path of level package
        dirpath = os.path.realpath(os.path.dirname(os.path.dirname(path)))
        with open(path, "r") as fp:
            data = json.load(fp)
            self.name = data["identifier"]
            # Level origin point (top-left) and dimensions
            self.x, self.y = data["worldX"], data["worldY"]
            self.w, self.h = data["pxWid"], data["pxHei"]
            # Background (TODO: Background image)
            if data["bgColor"] is not None:
                self.bg_color = pygame.Color(data["bgColor"])
            # Difficulty modifiers
            self.difficult_inc = data["fieldInstances"][0]["__value"]
            self.difficult_dec = data["fieldInstances"][1]["__value"]
            ''' Parsing Layers '''
            layers = data["layerInstances"]
            # Player
            player = layers[0]["entityInstances"][0]
            self.player_x, self.player_y = player["px"]
            self.player_size = (player["width"], player["height"])
            # Sprites
            sprites = layers[1]["entityInstances"]
            self.sprites_data = self.__parse_sprites(sprites)
            # Endpoint
            self.end_pos = layers[2]["entityInstances"][0]["px"]
            self.end_pos[1] = 0     # End Y set to top of level
            # Platforms
            platform_layer = layers[3]
            self.platform_size = [platform_layer["__gridSize"] for i in range(2)]
            self.platform_tilepath = os.path.join(dirpath, platform_layer["__tilesetRelPath"])
            self.platforms_data = self.__parse_platforms(platform_layer["gridTiles"])

    # Selects the required information for all sprite instances and returns as list
    def __parse_sprites(self, data):
        sprites = list()
        for d_i in data:
            sprite = {
                "type": d_i["__identifier"],
                "width": d_i["width"],
                "height": d_i["height"],
                "x": d_i["px"][0],
                "y": d_i["px"][1],
            }
            sprite["name"] = str(sprite["x"])+"-"+str(sprite["y"])
            for field in d_i["fieldInstances"]:
                if field["__identifier"] == "effect_types":
                    effect_types = list(map(lambda x: effect_map[x], field["__value"]))
                elif field["__identifier"] == "effect_amounts":
                    effect_amounts = field["__value"]
                elif field["__identifier"] == "effect_durations":
                    effect_durations = field["__value"]
                else:
                    sprite[field["__identifier"]] = field["__value"]
            try:
                effects = tuple(zip(effect_types, effect_amounts, effect_durations))
                sprite["effects"] = effects
            except NameError:
                pass
            sprites.append(sprite)
        return sprites
    
    # Selects required information for all platform tiles and returns as list
    def __parse_platforms(self, data):
        platforms = list()
        for d_i in data:
            platforms.append({
                "name": str(d_i["px"][0])+"-"+str(d_i["px"][1]),
                "x": d_i["px"][0],
                "y": d_i["px"][1],
                "src": d_i["src"],
            })
        return platforms

    # Using the parsed level data, build sprite groups containing the level objects
    # Param:
    # player - Sprite object of player (Created outside of level to maintain traits across levels)
    # global_diff_inc - Difficulty increasing modifier set from settings
    # global_diff_dec - Difficulty decreasing modifier set from settings
    # Returns:
    # Drawables - Group of visible sprites
    # Collidables - Group of sprites that collide with player
    # Platforms - Group of platforms
    # playerGroup - Single sprite group containing the player (for collision detection)
    # EndRect - Rect object covering finish area of level
    # Wave - Tsunami instance
    def build(self, player, global_diff_inc, global_diff_dec):
        # Create Sprite Groups
        Drawables = pygame.sprite.LayeredUpdates()
        playerGroup = pygame.sprite.GroupSingle()
        Collidables = pygame.sprite.Group()
        Platforms = pygame.sprite.Group()
        # Build end area Rect
        end_area = (self.w-self.end_pos[0], self.h)
        EndRect = pygame.Rect(self.end_pos, end_area)
        # Set player position, reset effects, velocity and add to groups
        player.set_pos(self.player_x, self.player_y)
        player.clear_effects()
        player.set_vel(0,0)
        playerGroup.add(player)
        Drawables.add(player, layer=4)
        # Build platforms from level data
        self.__build_platforms(Collidables, Platforms, Drawables)
        # Build sprites from level data
        self.__build_sprites(Collidables, Drawables, global_diff_inc, global_diff_dec)
        # Create Wave
        WaveTexture = ColorTexture((0,0,255))
        Wave = Tsunami("wave", -self.w, 0, self.w, self.h, WaveTexture, 5, 5000)
        Drawables.add(Wave, layer=5)
        Collidables.add(Wave)
        # Output Groups and other objects required by game
        return Drawables, Collidables, Platforms, playerGroup, EndRect, Wave
    
    def __build_platforms(self, Collidables, Platforms, Drawables):
        PlatformSheet = pygame.image.load(self.platform_tilepath)
        for p_i in self.platforms_data:
            PlatformTexture = ImageTexture(crop(PlatformSheet, p_i["src"], self.platform_size))
            platform = Platform(**p_i,
                width=self.platform_size[0], height=self.platform_size[1],
                texture=PlatformTexture
            )
            Collidables.add(platform)
            Platforms.add(platform)
            Drawables.add(platform, layer=2)
    
    def __build_sprites(self, Collidables, Drawables, global_inc, global_dec):
        for sprite_d in self.sprites_data:
            sprite_d["increasers"] = (global_inc, self.difficult_inc)
            sprite_d["decreasers"] = (global_dec, self.difficult_dec)
            # Item Sprites
            if sprite_d["type"] == "Coin":
                Sprite = Coin(**sprite_d,
                    texture=CoinAnimation.copy())
            elif sprite_d["type"] == "Treasure":
                Sprite = Treasure(**sprite_d,
                    texture=TreasureTexture)
            elif sprite_d["type"] == "Bandage":
                Sprite = Bandage(**sprite_d,
                    texture=BandageTexture)
            elif sprite_d["type"] == "Medkit":
                Sprite = Medkit(**sprite_d,
                    texture=MedkitTexture)
            elif sprite_d["type"] == "Rum":
                Sprite = Rum(**sprite_d,
                    texture=RumTexture)
            # Obstacle Sprites
            elif sprite_d["type"] == "Anchor":
                Sprite = Anchor(**sprite_d,
                    texture=AnchorTexture)
            elif sprite_d["type"] == "Barrel":
                Sprite = Barrel(**sprite_d,
                    texture=BarrelTexture)
            elif sprite_d["type"] == "Crate":
                Sprite = Crate(**sprite_d,
                    texture=CrateTexture)
            # Special Item Sprites
            elif sprite_d["type"] == "Horse":
                Sprite = Horse(**sprite_d,
                    texture=HorseTexture)
            elif sprite_d["type"] == "ShipDock":
                Sprite = ShipDock(**sprite_d,
                    dock_texture=DockTexture, ship_texture=ShipTexture)
                Sprite.ship_on_water(self.h)
                Sprite.ship_drawable(Drawables)
            elif sprite_d["type"] == "Cannon":
                Sprite = Cannon(**sprite_d,
                    texture=CannonTexture)
            # Enemy Sprites
            elif sprite_d["type"] == "Pirate":
                Sprite = Pirate(**sprite_d,
                    texture=PirateTexture)
            elif sprite_d["type"] == "Redcoat":
                Sprite = Redcoat(**sprite_d,
                    texture=RedcoatTexture)
            elif sprite_d["type"] == "Parrot":
                Sprite = Parrot(**sprite_d,
                    texture=ParrotTexture)
            elif sprite_d["type"] == "Skeleton":
                Sprite = Skeleton(**sprite_d,
                    texture=SkeletonTexture)
            # Add Sprite to groups
            Collidables.add(Sprite)
            Drawables.add(Sprite, layer=3)

    @staticmethod
    # Takes sprite groups from game and destroys all sprites in these groups
    def destroy(*groups):
        for group in groups:
            for sprite in group:
                sprite.kill()