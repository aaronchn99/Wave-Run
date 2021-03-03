import json, pygame, enum


# Maintains level data (e.g. level size, platform and sprite info)
# Used to build level
class Level:
    sprite_class_map = {

    }

    # Takes path of level data file (i.e. ldtkl file)
    def __init__(self, path):
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
            self.player_pos = player["px"]
            self.player_size = (player["width"], player["height"])
            # Sprites
            sprites = layers[1]["entityInstances"]
            self.sprites_data = self.__parse_sprites(sprites)
            # Endpoint
            self.end_pos = layers[2]["entityInstances"][0]["px"]
            # Platforms
            platform_layer = layers[3]
            self.platform_grid_w = platform_layer["__gridSize"]
            self.platforms_data = self.__parse_platforms(platform_layer["gridTiles"])


    # Selects the required information for all sprite instances and returns as list
    def __parse_sprites(self, data):
        sprites = list()
        for d_i in data:
            sprite = {
                "type": d_i["__identifier"],
                "w": d_i["width"],
                "h": d_i["height"],
                "x": d_i["px"][0],
                "y": d_i["px"][1],
            }
            for field in d_i["fieldInstances"]:
                sprite[field["__identifier"]] = field["__value"]
            sprites.append(sprite)
        return sprites
    
    # Selects required information for all platform tiles and returns as list
    def __parse_platforms(self, data):
        platforms = list()
        for d_i in data:
            platforms.append({
                "x": d_i["px"][0],
                "y": d_i["px"][1],
                "src": d_i["src"],
            })
        return platforms

    # Using the parsed level data, build sprite groups containing the level objects
    # Param:
    # player - Sprite object of player (Created outside of level to maintain traits across levels)
    # Returns:
    # Drawables - Group of visible sprites
    # Collidables - Group of sprites that collide with player
    # Platforms - Group of platforms
    # EndRect - Rect object covering finish area of level
    # Wave - Tsunami instance
    def build(self, player):
        return 
    
    @staticmethod
    # Takes sprite groups from game and destroys all sprites in these groups
    def destroy(*groups):
        for group in groups:
            group.empty()