''' Initialisation Procedure '''
# Pygame and window initialisation
import random as rand
from Sprites import *
from MenuObjs import *
import os
import ctypes
import pygame.freetype
pygame.init()
from Images import *
import platform
if platform.release() in ("Vista", "7", "8", "9", "10"):
    # Set the program to be DPI aware to avoid window stretching (Only for Vista or later)
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
# Turns of and on fullscreen to fix dodgy fullscreen
pygame.display.set_mode(resolution)
pygame.display.set_mode(resolution, pygame.FULLSCREEN)
# Game program variables
close = False
mode = "main"
loaded = False
game_init = False
shop_init = False
combat_init = False
pause = False
action_bind = ""
bind_time = 5000





'''Classes'''
class Camera(object):



    def __init__(self, cam_dim, course_dim):
        self._camRect = pygame.Rect((0, 0), cam_dim)
        self._courseRect = pygame.Rect((0, 0), course_dim)
        self._vel = (0, 0)



    def set_scroll(self, player):
        self._vel = player.set_scroll(resolution)
        self.checkOnBoundary()



    def get_rect(self):
        return self._courseRect



    def apply(self, sprites, endRect):
        dx, dy = round(self._vel[0], 0), round(self._vel[1], 0)
        self._courseRect.x += dx
        self._courseRect.y += dy
        for Sprite in sprites:
            Sprite.scroll((dx, dy))
        endRect.x += dx
        endRect.y += dy



    # Prevents the screen to scroll past the course area
    def checkOnBoundary(self):
        dx, dy = self._vel
        if self._courseRect.left + dx >= self._camRect.left:
            dx = self._camRect.left - self._courseRect.left
        elif self._courseRect.right + dx <= self._camRect.right:
            dx = self._camRect.right - self._courseRect.right
        if self._courseRect.top + dy >= self._camRect.top:
            dy = self._camRect.top - self._courseRect.top
        elif self._courseRect.bottom + dy <= self._camRect.bottom:
            dy = self._camRect.bottom - self._courseRect.bottom
        self._vel = (dx, dy)




class HUD(object):


    # Constructs the HUD for the first time
    def __init__(self, health, max_hp, money, score):
        # HUD background is rendered
        self.background = pygame.Surface((resolution[0], int(resolution[1]*(200/1080))))
        self.background.fill(BLACK)
        # Using the font loaded in the loading procedure, Text objects are set up and rendered
        # first for the variable labels
        self.hpLabel = res_scale(subFont.render("Hearts", False, WHITE))
        self.moneyLabel = res_scale(subFont.render("Gold", False, WHITE))
        self.scoreLabel = res_scale(subFont.render("Score", False, WHITE))
        self.effectLabel = res_scale(subFont.render("Effects", False, WHITE))
        self.progressLabel = res_scale(subFont.render("Course", False, WHITE))
        # The update function is called to render Text objects to show initial score and money
        # values and a list of Rects to represent the initial health
        self.hud_update(health, max_hp, money, score, [], 0)



    # Update the values shown by the HUD
    def hud_update(self, hp, max_hp, money, score, effects, progress):
        # Sets up the list of hearts
        # It is only set up if the health is larger than 0
        hearts = []
        if hp > 0:
            current_hp = hp
            while max_hp > 0:
                if current_hp >= 2:
                    hearts.append(1)
                    current_hp -= 2
                elif current_hp == 1:
                    if current_hp == max_hp:
                        hearts.append(3)
                        current_hp -= 1
                    else:
                        hearts.append(2)
                        current_hp -= 1
                elif current_hp == 0:
                    if max_hp == 1:
                        hearts.append(4)
                    elif max_hp >= 2:
                        hearts.append(5)
                max_hp -= 2
        self.Hearts = hearts
        # Creates a list of active effect types for the draw procedure to use
        effectList = list()
        for effect in effects:
            effectList.append(effect[0])
        self.effect_list = effectList
        # Creates progress bar as one Surface
        self.progressBar = pygame.Surface((int(1528*scale_f), int(42*scale_f)))
        self.progressBar.fill(WHITE, pygame.Rect(int(0*xpos_f), int(0*ypos_f), int(14*scale_f), int(42*scale_f)))
        self.progressBar.fill(WHITE, pygame.Rect(int(1514*xpos_f), int(0*ypos_f), int(14*scale_f), int(42*scale_f)))
        self.progressBar.fill(WHITE, pygame.Rect(int(14*xpos_f), int(15*ypos_f), int(1500*scale_f), int(6*scale_f)))
        self.progressBar.fill(RED, pygame.Rect(round(1514 * progress * xpos_f, 0), int(0*ypos_f), int(28*scale_f), int(42*scale_f)))
        # The Text object showing the current money and score values are rendered, taking the
        # money and score arguments in string data type
        self.moneyValue = subFontRes.render(str(money), YELLOW)[0]
        self.scoreValue = subFontRes.render(str(score), WHITE)[0]



    # Draws the HUD objects on screen. Takes the window surface and the list of HUD elements
    def draw_hud(self, screen):
        # The image of the HUD background is drawn on the window
        screen.blit(self.background, (0, 0))
        # The Hearts label is drawn
        screen.blit(self.hpLabel, (int(177*xpos_f), int(10*ypos_f)))
        # The list of hearts to be drawn is put together as one Surface object and centre-aligned
        # with the "Hearts" label.
        if self.Hearts != []:
            Heart1 = res_scale(crop(HeartSheet, (0, 0), (70, 65)))
            Heart2 = res_scale(crop(HeartSheet, (70, 0), (70, 65)))
            Heart3 = res_scale(crop(HeartSheet, (140, 0), (70, 65)))
            Heart4 = res_scale(crop(HeartSheet, (210, 0), (70, 65)))
            Heart5 = res_scale(crop(HeartSheet, (280, 0), (70, 65)))
            arrange = self.Hearts
            heartRect = pygame.Rect((0, 0), (int(70*scale_f), int(65*scale_f)))
            for i in range(1, len(arrange)):
                heartRect = heartRect.union(pygame.Rect((int(73 * xpos_f * i), 0), (int(70*scale_f), int(65*scale_f))))
            heart_x = self.hpLabel.get_rect(topleft=(int(177*xpos_f), int(10*ypos_f))).midbottom[0]
            heart_y = self.hpLabel.get_rect(topleft=(int(177*xpos_f), int(10*ypos_f))).midbottom[1] + int(8*ypos_f)
            heartRect.midtop = (heart_x, heart_y)
            Hearts = pygame.Surface((heartRect.width, heartRect.height))
            for i in range(len(arrange)):
                if arrange[i] == 1:
                    Hearts.blit(Heart1, (int(73 * xpos_f * i), 0))
                elif arrange[i] == 2:
                    Hearts.blit(Heart2, (int(73 * xpos_f * i), 0))
                elif arrange[i] == 3:
                    Hearts.blit(Heart3, (int(73 * xpos_f * i), 0))
                elif arrange[i] == 4:
                    Hearts.blit(Heart4, (int(73 * xpos_f * i), 0))
                elif arrange[i] == 5:
                    Hearts.blit(Heart5, (int(73 * xpos_f * i), 0))
            screen.blit(Hearts, heartRect.topleft)
        # The "Gold" label is drawn
        screen.blit(self.moneyLabel, (int(1210*xpos_f), int(10*ypos_f)))
        # The Text that shows the money amount is drawn next to the Gold label
        pos = list(self.moneyLabel.get_rect(topleft=(int(1210*xpos_f), int(10*ypos_f))).topright)
        pos[0] = pos[0] + int(40*xpos_f)
        screen.blit(self.moneyValue, pos)
        # The "Score" label is drawn
        screen.blit(self.scoreLabel, (int(1210*xpos_f), int(60*ypos_f)))
        # Similar to the money amount text, the score value text is drawn next to the Score label
        pos = list(self.scoreLabel.get_rect(topleft=(int(1210*xpos_f), int(60*ypos_f))).topright)
        pos[0] = pos[0] + int(40*xpos_f)
        screen.blit(self.scoreValue, pos)
        # Draws the Effects label
        screen.blit(self.effectLabel, (int(720*xpos_f), int(10*ypos_f)))
        # The list of effect sprites to be drawn is put together as one Surface object and centre-aligned
        # with the Effects label.
        effect_list = self.effect_list
        if effect_list != []:
            fastSprite = res_scale(crop(EffectSheet, (0, 0), (65, 65)))
            slowSprite = res_scale(crop(EffectSheet, (65, 0), (65, 65)))
            koSprite = res_scale(crop(EffectSheet, (130, 0), (65, 65)))
            confuseSprite = res_scale(crop(EffectSheet, (195, 0), (65, 65)))
            cannonSprite = res_scale(crop(EffectSheet, (260, 0), (65, 65)))
            shipSprite = res_scale(crop(EffectSheet, (325, 0), (65, 65)))
            spriteRect = fastSprite.get_rect()
            for i in range(1, len(effect_list)):
                spriteRect = spriteRect.union(fastSprite.get_rect(topleft=(int(70 * xpos_f * i), 0)))
            x = self.effectLabel.get_rect(topleft=(int(720*xpos_f), int(10*ypos_f))).midbottom[0]
            y = self.effectLabel.get_rect(topleft=(int(720*xpos_f), int(10*ypos_f))).midbottom[1] + int(8*ypos_f)
            spriteRect.midtop = (x, y)
            effectSurf = pygame.Surface(spriteRect.size)
            for i in range(len(effect_list)):
                if effect_list[i] == "fast":
                    effectSurf.blit(fastSprite, (int(70 * xpos_f * i), 0))
                elif effect_list[i] == "slow":
                    effectSurf.blit(slowSprite, (int(70 * xpos_f * i), 0))
                elif effect_list[i] == "knockout":
                    effectSurf.blit(koSprite, (int(70 * xpos_f * i), 0))
            screen.blit(effectSurf, spriteRect.topleft)
        # Draws the progress label
        screen.blit(self.progressLabel, (int(55*xpos_f), int(140*ypos_f)))
        # Draws the progress bar next to the label
        screen.blit(self.progressBar, (int(337*xpos_f), int(140*ypos_f)))




''' Procedures and Functions '''
# Scales Surface objects depending on the set resolution
def res_scale(surf):
    old_size = surf.get_size()
    new_size = (int(old_size[0]*scale_f), int(old_size[1]*scale_f))
    return pygame.transform.scale(surf, new_size)

# Crops an image with the specified position of the top left corner and the area
def crop(Image, pos, area):
    crop_area = pygame.Surface(area, pygame.SRCALPHA)
    crop_area.blit(Image, (-pos[0], -pos[1]))
    return crop_area

# Procedure that runs the game over sequence
def game_over():
    loseMenu.update(inputs)
    if loseMenu.find_obj("main button").get_trigger():
        return "main"
    if loseMenu.find_obj("retry button").get_trigger():
        return "retry"
    loseMenu.draw()

# Procedure that runs the level transition
def lvl_clear(inputs):
    # First, the window is filled white
    Window.fill(WHITE)
    # Game objects and sprites are drawn next
    Drawables.draw(Window)
    playerSprite.update({"key": [right_key]}, (), Platforms, playerGroup)
    winText = headerFontRes.render("Level Clear", GREEN)[0]
    continueText = subFontRes.render("Press any key to continue", GREEN)[0]
    pos = winText.get_rect(center=(int(resolution[0] / 2), int(resolution[1] / 2))).topleft
    Window.blit(winText, pos)
    pos = continueText.get_rect(center=(int(resolution[0] / 2), int(resolution[1] / 2 + (100*ypos_f)))).topleft
    if playerSprite.get_pos()[0] >= resolution[0]:
        Window.blit(continueText, pos)
        if inputs["key"] != []:
            inputs["key"] = []
            return True
        else:
            return False

# Handles game win procedure
def game_win():
    Window.fill(WHITE)
    winText = headerFontRes.render("You win", GREEN)[0]
    continueText = subFontRes.render("Press enter to go back to main menu", GREEN)[0]
    pos = winText.get_rect(center=(int(resolution[0] / 2), int(resolution[1] / 2))).topleft
    Window.blit(winText, pos)
    pos = continueText.get_rect(center=(int(resolution[0] / 2), int(resolution[1] / 2 + (100*ypos_f)))).topleft
    Window.blit(continueText, pos)

# Loads the data needed for a level from a level data file. It separates the
# data into 2 parts: mapping array and metadata and returns them
def loadLevel(filename):
    filePointer = open(filename, "r")
    map = []
    metadata = {}
    read_list = filePointer.readlines()
    data_type = ""
    for line in read_list:
        if "\n" in line:
            line = line.replace("\n", "")
        if line == "map":
            data_type = "map"
        elif line == "metadata":
            data_type = "metadata"
        elif line == "":
            data_type = ""
        elif data_type == "map":
            row = []
            for tile in line:
                row.append(tile)
            map.append(row)
        elif data_type == "metadata":
            temp = line.split(':')
            metadata[temp[0]] = temp[1]
    return map, metadata

# Builds the level by checking each tile in the 2D mapping array
# and creating the sprite corresponding to that tile
def buildLevel(map, metadata, tile_dim, Groups):
    Drawables, playerGroup, Collidables, Platforms = Groups
    for y in range(len(map)):
        for x in range(len(map[y])):
            pos = (x * tile_dim[0], y * tile_dim[1])
            tile = map[y][x]
            name = str(x) + str(y)
            if tile == " ":
                pass
            elif tile == "#":
                platform = Platform(name, pos[0], pos[1], tile_dim[0], tile_dim[1], BLACK)
                for Group in (Drawables, Collidables, Platforms):
                    Group.add(platform)
            elif tile == "C":
                coin = Item(name, pos[0], pos[1], tile_dim[0], tile_dim[1], rand.randint(10, 40), ["money", 1, 0],
                            image=crop(EntitySheet, (0, 0), (40, 40)))
                for Group in (Drawables, Collidables):
                    Group.add(coin)
            elif tile == "T":
                chest = Item(name, pos[0], pos[1], tile_dim[0], tile_dim[1], rand.randint(50, 100),
                             ["money", 20, 0], image=crop(EntitySheet, (40, 0), (40, 40)))
                for Group in (Drawables, Collidables):
                    Group.add(chest)
            elif tile == "B":
                bandage = Item(name, pos[0], pos[1], tile_dim[0], tile_dim[1], 0, ["health", 1, 0],
                               image=crop(EntitySheet, (80, 0), (40, 40)))
                for Group in (Drawables, Collidables):
                    Group.add(bandage)
            elif tile == "M":
                medkit = Item(name, pos[0], pos[1], tile_dim[0], tile_dim[1], 0, ["health", 999, 0],
                              image=crop(EntitySheet, (0, 40), (40, 40)))
                for Group in (Drawables, Collidables):
                    Group.add(medkit)
            elif tile == "R":
                rum = Item(name, pos[0], pos[1], tile_dim[0], tile_dim[1], rand.randint(100, 200),
                           [["health", 3, 0], ["slow", 3, 10000]], image=crop(EntitySheet, (40, 40), (40, 40)))
                for Group in (Drawables, Collidables):
                    Group.add(rum)
            elif tile == "H":
                horse = Item(name, pos[0], pos[1], tile_dim[0], tile_dim[1], rand.randint(100, 200),
                             ["fast", 5, 20000], image=crop(EntitySheet, (80, 40), (40, 40)))
                for Group in (Drawables, Collidables):
                    Group.add(horse)
            elif tile == "A":
                anchor = Obstacle(name, pos[0], pos[1], tile_dim[0], tile_dim[1], 1, 200, 6000,
                                  image=crop(EntitySheet, (0, 80), (40, 40)))
                for Group in (Drawables, Collidables):
                    Group.add(anchor)
            elif tile == "N":
                barrel = Obstacle(name, pos[0], pos[1], tile_dim[0], tile_dim[1], 1, 200, 3000,
                                  image=crop(EntitySheet, (40, 80), (40, 40)))
                for Group in (Drawables, Collidables):
                    Group.add(barrel)
            elif tile == "O":
                crate = Obstacle(name, pos[0], pos[1], tile_dim[0], tile_dim[1], 1, 200, 2000,
                                 image=crop(EntitySheet, (80, 80), (40, 40)))
                for Group in (Drawables, Collidables):
                    Group.add(crate)
            elif tile == "P":
                global playerSprite
                playerSprite.move_to(pos[0], pos[1])
                playerSprite.clear_effects()
                playerSprite.set_vel(0, 0)
                for Group in (Drawables, playerGroup):
                    Group.add(playerSprite)
            elif tile == "E":
                enemy = Enemy(name, pos[0], pos[1], tile_dim[0], tile_dim[1], (255, 0, 255), 3, 2, 0.4, 2, 500, 400)
                for Group in (Drawables, Collidables):
                    Group.add(enemy)

# Procedure that applies the settings passed into it
def apply_settings(settings):
    global resolution
    global scale_f
    global xpos_f
    global ypos_f
    # Changes scale and position factors depending on resolution
    temp_list = settings["resolution"].split("x")
    resolution = (int(temp_list[0]), int(temp_list[1]))
    xpos_f = resolution[0]/1920
    ypos_f = resolution[1]/1080
    scale_f = min((xpos_f, ypos_f))
    for obj in gui_list:
        if type(obj) == Menu:
            obj.update_res(scale_f, xpos_f, ypos_f, resolution)
        else:
            obj.update_res(scale_f, xpos_f, ypos_f)
    update_res(scale_f, xpos_f, ypos_f)
    global subFontRes
    global headerFontRes
    subFontRes = pygame.freetype.Font("PressStart2P.ttf", int(37 * scale_f))
    headerFontRes = pygame.freetype.Font("PressStart2P.ttf", int(107 * scale_f))
    # Turns on or off fullscreen
    global Window
    if settings["fullscreen"] == True:
        Window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
    else:
        Window = pygame.display.set_mode(resolution)

if __name__ == "__main__":
    ''' Loading Procedure '''
    # Loading the Arcade Classic font at font size 42
    subFont = pygame.font.Font("PressStart2P.ttf", 42)
    subFontRes = pygame.freetype.Font("PressStart2P.ttf", int(37*scale_f))
    # Loads the same font, but large for headers
    headerFont = pygame.font.Font("PressStart2P.ttf", 120)
    headerFontRes = pygame.freetype.Font("PressStart2P.ttf", int(107*scale_f))
    # Loads the hearts sprite sheet
    HeartSheet = pygame.image.load("images\Hearts.png")
    # Loads the
    EffectSheet = pygame.image.load("images\Effects.png")
    # Loads and crops sprite images for items and obstacles
    EntitySheet = pygame.image.load("images\ItemObstacles.png")

    ''' Class instances '''
    # Menus
    Main = Menu("main", [
        Image("main title", 480, 100, headerFont.render("Wave Run", False, (0,198,255))),
        Button("start", 710, 300, inactiveStartButton, activeStartButton, pressStartButton),
        Button("load", 710, 400, inactiveLoadButton, activeLoadButton, pressLoadButton),
        Button("level select", 710, 500, inactiveLevelButton, activeLevelButton, pressLevelButton),
        Button("tutorial", 710, 600, inactiveTutorialButton, activeTutorialButton, pressTutorialButton),
        Button("score", 710, 700, inactiveScoreButton, activeScoreButton, pressScoreButton),
        Button("setting", 710, 800, inactiveSettingButton, activeSettingButton, pressSettingButton),
        Button("quit", 710, 900, inactiveQuitButton, activeQuitButton, pressQuitButton)
    ], {"A": {"left": "A", "right": "A", "up": "G", "down": "B", "obj name": "start"},
        "B": {"left": "B", "right": "B", "up": "A", "down": "C", "obj name": "load"},
        "C": {"left": "C", "right": "C", "up": "B", "down": "D", "obj name": "level select"},
        "D": {"left": "D", "right": "D", "up": "C", "down": "E", "obj name": "tutorial"},
        "E": {"left": "E", "right": "E", "up": "D", "down": "F", "obj name": "score"},
        "F": {"left": "F", "right": "F", "up": "E", "down": "G", "obj name": "setting"},
        "G": {"left": "G", "right": "G", "up": "F", "down": "A", "obj name": "quit"}
        }, pointerSurf=blackRightArrow)
    unavailableText = subFontRes.render("This feature is not yet available", BLACK)[0]

    Settings = Menu("settings menu", [
        Image("setting title", 144, 67, settingsTitle),
        Image("graphics label", 144, 228, GraphicsText),
        Image("res label", 189, 327, ResolutionText),
        Image("fullscreen label", 189, 421, FullscreenText),
        Image("audio title", 144, 547, AudioText),
        Image("music label", 189, 653, MusicText),
        Image("sfx label", 189, 812, SFXText),
        Image("gameplay title", 1087, 228, GameplayText),
        Image("control label", 1148, 315, ControlsText),
        Image("left label", 1259, 405, LeftText),
        Image("right label", 1259, 484, RightText),
        Image("jump label", 1259, 568, JumpText),
        Image("difficulty label", 1167, 681, DifficultyText),
        TickBox("fullscreen tick", 700, 409, tickBoxOffSurf, tickBoxOnSurf, state=settings_dict["fullscreen"]),
        Slider("music slider", 202, 709, 870, (0, 100), 10, sliderPointerSurfH, slideSurfH, settings_dict["music vol"]),
        Slider("sfx slider", 202, 868, 870, (0, 100), 10, sliderPointerSurfH, slideSurfH, settings_dict["sfx vol"]),
        Button("set left button", 1515, 391, WhiteButton, WhiteButton, WhiteButton),
        Button("set right button", 1515, 474, WhiteButton, WhiteButton, WhiteButton),
        Button("set jump button", 1515, 560, WhiteButton, WhiteButton, WhiteButton),
        Button("default", 800, 947, inactiveDefaultButton, activeDefaultButton, pressDefaultButton),
        Button("apply", 1170, 947, inactiveApplyButton, activeApplyButton, pressApplyButton),
        Button("back", 1543, 947, inactiveBackButton, activeBackButton, pressBackButton),
        DropMenu("res list", 700, 315, subFontRes, avail_resmodes, lineSurf,
                 sliderPointerSurfV, slideSurfV, current_index=avail_resmodes.index(default_settings["resolution"]),
                 lines=9),
        DropMenu("difficulty list", 1259, 769, subFontRes, ["Easy", "Normal", "Hard", "Extreme"], lineSurf,
                 sliderPointerSurfV, slideSurfV)
    ], {
        "A": {"left": "B", "right": "B", "up": "I", "down": "C", "obj name": "res list"},
        "B": {"left": "C", "right": "C", "up": "K", "down": "D", "obj name": "set left button"},
        "C": {"left": "B", "right": "B", "up": "A", "down": "F", "obj name": "fullscreen tick"},
        "D": {"left": "C", "right": "C", "up": "B", "down": "E", "obj name": "set right button"},
        "E": {"left": "C", "right": "E", "up": "D", "down": "G", "obj name": "set jump button"},
        "F": {"left": "G", "right": "G", "up": "C", "down": "H", "obj name": "music slider"},
        "G": {"left": "F", "right": "F", "up": "E", "down": "J", "obj name": "difficulty list"},
        "H": {"left": "G", "right": "G", "up": "F", "down": "I", "obj name": "sfx slider"},
        "I": {"left": "K", "right": "J", "up": "H", "down": "A", "obj name": "default"},
        "J": {"left": "I", "right": "K", "up": "G", "down": "B", "obj name": "apply"},
        "K": {"left": "J", "right": "I", "up": "G", "down": "B", "obj name": "back"}
        }, settingsBkgd, pointerSurf=blackRightArrow)

    Shop = Menu("shop", [
        Image("shop title", 795, 265, shopTitle),
        Image("max health", 346, 373, maxHealth),
        Image("max speeds", 346, 458, maxSpeeds),
        Image("acceleration", 346, 548, Acceleration),
        Image("strength", 346, 629, Strength),
        Image("defence", 346, 723, Defence),
        Image("gold", 346, 830, Gold),
        Button("hp down", 920, 369, inactiveLeftButton, activeLeftButton, pressLeftButton),
        Button("hp up", 1400, 369, inactiveRightButton, activeRightButton, pressRightButton),
        Button("speed down", 920, 454, inactiveLeftButton, activeLeftButton, pressLeftButton),
        Button("speed up", 1400, 454, inactiveRightButton, activeRightButton, pressRightButton),
        Button("acc down", 920, 544, inactiveLeftButton, activeLeftButton, pressLeftButton),
        Button("acc up", 1400, 544, inactiveRightButton, activeRightButton, pressRightButton),
        Button("str down", 920, 625, inactiveLeftButton, activeLeftButton, pressLeftButton),
        Button("str up", 1400, 625, inactiveRightButton, activeRightButton, pressRightButton),
        Button("def down", 920, 719, inactiveLeftButton, activeLeftButton, pressLeftButton),
        Button("def up", 1400, 719, inactiveRightButton, activeRightButton, pressRightButton),
        Button("reset", 980, 830, inactiveResetButton, activeResetButton, pressResetButton),
        Button("continue", 1270, 830, inactiveContinueButton, activeContinueButton, pressContinueButton)
    ], {"A": {"left": "B", "right": "B", "up": "K", "down": "C", "obj name": "hp down"},
        "B": {"left": "A", "right": "A", "up": "L", "down": "D", "obj name": "hp up"},
        "C": {"left": "D", "right": "D", "up": "A", "down": "E", "obj name": "speed down"},
        "D": {"left": "C", "right": "C", "up": "B", "down": "F", "obj name": "speed up"},
        "E": {"left": "F", "right": "F", "up": "C", "down": "G", "obj name": "acc down"},
        "F": {"left": "E", "right": "E", "up": "D", "down": "H", "obj name": "acc up"},
        "G": {"left": "H", "right": "H", "up": "E", "down": "I", "obj name": "str down"},
        "H": {"left": "G", "right": "G", "up": "F", "down": "J", "obj name": "str up"},
        "I": {"left": "J", "right": "J", "up": "G", "down": "K", "obj name": "def down"},
        "J": {"left": "I", "right": "I", "up": "H", "down": "L", "obj name": "def up"},
        "K": {"left": "L", "right": "L", "up": "I", "down": "A", "obj name": "reset"},
        "L": {"left": "K", "right": "K", "up": "J", "down": "B", "obj name": "continue"}
                                }, bkgSurf, pointerSurf=blackRightArrow)

    loseMenu = Menu("lose menu", [
        Button("main button", 450, 800, inactiveMainButton, activeMainButton, pressMainButton),
        Button("retry button", 1100, 800, inactiveRetryButton, activeRetryButton, pressRetryButton),
        Image("lose title", 428, 488, headerFont.render("Game Over", False, WHITE))
    ], {"A": {"left": "B", "right": "B", "up": "A", "down": "A", "obj name": "main button"},
        "B": {"left": "A", "right": "A", "up": "B", "down": "B", "obj name": "retry button"}
        }, pygame.Surface(resolution), pointerSurf=greenRightArrow)

    pauseButton = Button("pause", round(1880*xpos_f), 0, pauseButtonSurf, pauseButtonSurf, pauseButtonSurf)

    gui_list = [Main, Settings, Shop, loseMenu, pauseButton]
    # Updates settings
    apply_settings(default_settings)

    ''' Program Loop '''
    while not close:


        ''' Input Procedure '''
        update_input()


        ''' Update Procedure '''
        if pygame.K_LALT in inputs["key"] and pygame.K_F4 in inputs["key"] or inputs["close"]:
            close = True
        if pygame.K_F5 in inputs["key"]:
            pygame.display.set_mode(resolution, pygame.FULLSCREEN)
            inputs["key"].remove(pygame.K_F5)
        if pygame.K_F6 in inputs["key"]:
            pygame.display.set_mode(resolution)
            inputs["key"].remove(pygame.K_F6)

        # Main Menu screen
        if mode == "main":
            Main.update(inputs)     # Update the Menu
            tell = False
            if Main.find_obj("start") != False:
                button = Main.find_obj("start")
                if button.get_trigger():
                    mode = "play"       # If the Start New button was triggered, mode is set to "play"
                    game_init = False
                    loaded = False
                    level = 1
            if Main.find_obj("setting") != False:
                button = Main.find_obj("setting")
                if button.get_trigger():
                    mode = "settings"
            if Main.find_obj("quit") != False:
                button = Main.find_obj("quit")
                if button.get_trigger():
                    close = True        # When Quit button triggered, close is set to True
            # Other buttons show a text saying it is unavailable
            for name in ("load","level select","tutorial","score"):
                button = Main.find_obj(name)
                if button.get_pressed():
                    tell = True
            Main.draw()     # All objects in main menu are drawn
            if tell:
                Window.blit(unavailableText, (0, int(1030*ypos_f)))

        # Settings menu
        elif mode == "settings":
            # Menu updated if not waiting for key binding
            if action_bind == "":
                Settings.update(inputs)
            # Handles set left button
            if Settings.find_obj("set left button").get_trigger() or action_bind == "left":
                action_bind = "left"
                if inputs["key"] != []:
                    action_bind = ""
                    settings_dict["left key"] = inputs["key"][0]
                    apply_settings(settings_dict)
                    bind_time = 5000
                else:
                    bind_time -= Clock.get_time()
                if bind_time < 0:
                    action_bind = ""
                    bind_time = 5000
            # Handles set right button
            if Settings.find_obj("set right button").get_trigger() or action_bind == "right":
                action_bind = "right"
                if inputs["key"] != []:
                    action_bind = ""
                    settings_dict["right key"] = inputs["key"][0]
                    apply_settings(settings_dict)
                    bind_time = 5000
                else:
                    bind_time -= Clock.get_time()
                if bind_time < 0:
                    action_bind = ""
                    bind_time = 5000
            # Handles set jump button
            if Settings.find_obj("set jump button").get_trigger() or action_bind == "jump":
                action_bind = "jump"
                if inputs["key"] != []:
                    action_bind = ""
                    settings_dict["jump key"] = inputs["key"][0]
                    apply_settings(settings_dict)
                    bind_time = 5000
                else:
                    bind_time -= Clock.get_time()
                if bind_time < 0:
                    action_bind = ""
                    bind_time = 5000
            # Sets controls to keys specified in settings
            left_key = settings_dict["left key"]
            right_key = settings_dict["right key"]
            jump_key = settings_dict["jump key"]
            update_controls(left_key, right_key, jump_key)
            # Resets settings if default is triggered
            if Settings.find_obj("default").get_trigger():
                settings_dict = default_settings.copy()
                Settings.find_obj("res list").set_option(settings_dict["resolution"])
                Settings.find_obj("fullscreen tick").set_state(settings_dict["fullscreen"])
                Settings.find_obj("music slider").set_value(settings_dict["music vol"])
                Settings.find_obj("sfx slider").set_value(settings_dict["sfx vol"])
                Settings.find_obj("difficulty list").set_option(settings_dict["difficulty"])
                apply_settings(settings_dict)
            # Apply new settings to settings dict
            if Settings.find_obj("apply").get_trigger():
                settings_dict["resolution"] = Settings.find_obj("res list").get_option()
                settings_dict["fullscreen"] = Settings.find_obj("fullscreen tick").get_state()
                settings_dict["music vol"] = Settings.find_obj("music slider").get_value()
                settings_dict["sfx vol"] = Settings.find_obj("sfx slider").get_value()
                settings_dict["difficulty"] = Settings.find_obj("difficulty list").get_option()
                apply_settings(settings_dict)
            # Game goes back to main menu if back button triggered
            if Settings.find_obj("back").get_trigger():
                Settings.find_obj("res list").set_option(settings_dict["resolution"])
                Settings.find_obj("fullscreen tick").set_state(settings_dict["fullscreen"])
                Settings.find_obj("music slider").set_value(settings_dict["music vol"])
                Settings.find_obj("sfx slider").set_value(settings_dict["sfx vol"])
                Settings.find_obj("difficulty list").set_option(settings_dict["difficulty"])
                mode = "main"
            # Drawing code
            Settings.draw()
            if action_bind == "left":
                label = subFontRes.render(str(int(bind_time/1000)+1)+"...", BLACK)[0]
            else:
                label = subFontRes.render(pygame.key.name(settings_dict["left key"]), BLACK)[0]
            pos = list(label.get_rect(midleft=Settings.find_obj("set left button").rect.midleft).topleft)
            pos[0] += 10*xpos_f
            Window.blit(label, pos)
            if action_bind == "right":
                label = subFontRes.render(str(int(bind_time/1000)+1)+"...", BLACK)[0]
            else:
                label = subFontRes.render(pygame.key.name(settings_dict["right key"]), BLACK)[0]
            pos = list(label.get_rect(midleft=Settings.find_obj("set right button").rect.midleft).topleft)
            pos[0] += 10*xpos_f
            Window.blit(label, pos)
            if action_bind == "jump":
                label = subFontRes.render(str(int(bind_time / 1000) + 1)+"...", BLACK)[0]
            else:
                label = subFontRes.render(pygame.key.name(settings_dict["jump key"]), BLACK)[0]
            pos = list(label.get_rect(midleft=Settings.find_obj("set jump button").rect.midleft).topleft)
            pos[0] += 10 * xpos_f
            Window.blit(label, pos)
            note = subFontRes.render("Note: Currently no sound or difficulty settings", BLACK)[0]
            Window.blit(note, (int(10*xpos_f), resolution[1] - note.get_height()))

        # Gameplay mode
        elif mode == "play":
            # Initialises game
            if not game_init:
                Drawables = pygame.sprite.LayeredUpdates()
                playerGroup = pygame.sprite.GroupSingle()
                Collidables = pygame.sprite.Group()
                Platforms = pygame.sprite.Group()
                playerSprite = playerClass("player", player_x, player_y, 32, 48, RED, health, player_accel,
                                           ((max_dx, min_dx), (max_dy, min_dy)), 1, 0.4)
                # Represents the area of the course
                CourseArea = pygame.Rect(0, 0, 1.5 * resolution[0], resolution[1])
                # Represents the level clear area
                EndArea = pygame.Rect(1920, 0, 0.5 * resolution[0], resolution[1])
                # Resetting money and score
                reset_money_score()
                # Initialising the HUD's image list
                Hud = HUD(playerSprite.get_hp(), playerSprite.get_max_hp(), get_money(), get_points())
                # Camera object that allows the screen to scroll across the course
                GameCam = Camera(resolution, (10, 10))
                # Create game images
                Overlay = pygame.Surface(resolution)
                Overlay.set_alpha(128)
                pauseText, pauseRect = headerFontRes.render("Paused", RED)
                pauseRect.center = (round(resolution[0] / 2), round(resolution[1] / 2))
                game_init = True

            # Constructs a new level when not already loaded
            if not loaded:
                Drawables = pygame.sprite.LayeredUpdates()
                playerGroup = pygame.sprite.GroupSingle()
                Collidables = pygame.sprite.Group()
                Platforms = pygame.sprite.Group()
                Map, Metadata = loadLevel("levels\lvl"+str(level)+".ldat")
                length = int(Metadata["length"])
                height = int(Metadata["height"])
                end = int(Metadata["end"])
                end_pos = (end*tile_dim[0], 0)
                end_area = ((length-end)*tile_dim[0], height*tile_dim[1])
                EndArea = pygame.Rect(end_pos, end_area)
                buildLevel(Map, Metadata, tile_dim, (Drawables, playerGroup, Collidables, Platforms))
                Wave = Tsunami("wave", -length*tile_dim[0], 0, length*tile_dim[0], height*tile_dim[0], BLUE, 5, 5000)
                Drawables.add(Wave)
                Collidables.add(Wave)
                GameCam = Camera(resolution, (length*tile_dim[0], height*tile_dim[1]))
                tile_progress = 0
                loaded = True

            # Gives pause button mouse input
            pauseButton.mouse_input(inputs)
            if not pause:
                if playerSprite.get_opponent() == None:
                    collide_list = playerSprite.update(inputs, Collidables, Platforms, playerGroup)
                    Collidables.update(collide_list, playerSprite)
                    GameCam.set_scroll(playerSprite)
                    GameCam.apply(Drawables, EndArea)

                    # The player's progress in the course is calculated
                    progress = (playerSprite.get_pos()[0] - GameCam.get_rect().left)/(EndArea.left - GameCam.get_rect().left)
                    # The player's tile position is calculated for the score_distance function
                    player_pos = playerSprite.get_pos()[0] - GameCam.get_rect().left
                    tile_progress = score_distance(player_pos, tile_progress)
                    # New updated HUD elements are returned to new_values
                    Hud.hud_update(playerSprite.get_hp(), playerSprite.get_max_hp(), get_money(), get_points(),
                                   playerSprite.get_effects(), progress)
                    # Handles pause button
                    pause = pauseButton.get_trigger()
                else:
                    enemy = playerSprite.get_opponent()
                    if not combat_init:
                        player_hp = playerSprite.get_hp()
                        enemy_hp = enemy.get_hp()
                        player_sp = playerSprite.get_sp()
                        enemy_sp = enemy.get_sp()
                        player_ap = playerSprite.get_ap()
                        enemy_ap = enemy.get_ap()
                        attack_key = rand.randint(97, 122)
                        progress = 0
                        combat_init = True
                        playerSprite.user_move(inputs, [enemy])
                    if attack_key in inputs["key"]:
                        attack = player_sp * (1 - enemy_ap)
                        progress += attack
                        inputs["key"].remove(attack_key)
                        if rand.random() <= 1/5:
                            attack_key = rand.randint(97, 122)
                    if rand.random() <= 1/60:
                        attack = enemy_sp * (1 - player_ap)
                        progress -= attack
                    if progress <= -player_hp:
                        enemy.player_lose(playerSprite)
                        playerSprite.set_opponent(None)
                        combat_init = False
                    elif progress >= enemy_hp:
                        enemy.player_win()
                        playerSprite.set_opponent(None)
                        combat_init = False
                    # Drawing code
                    KeySignal = headerFontRes.render(chr(attack_key).upper(), YELLOW)[0]
                    Back = pygame.Rect((0, 0), (int(200*scale_f), int(150*scale_f)))
                    Back.center = KeySignal.get_rect(topleft=(int(960*xpos_f-int(KeySignal.get_width()/2)), int(400*ypos_f))).center
                    CombatBar = pygame.Surface((int(800*scale_f), int(50*scale_f)))
                    progress_pos = int(800*((player_hp+progress)/(player_hp+enemy_hp))*scale_f)
                    neutral_pos = int(800*(player_hp/(player_hp+enemy_hp))*scale_f)
                    CombatBar.fill(RED)
                    CombatBar.fill(WHITE, pygame.Rect(neutral_pos-1, 0, 2, int(50*scale_f)))
                    Pointer = pygame.Rect(int(560*xpos_f+progress_pos-1), int(580*ypos_f), 2, int(70*ypos_f))
                if pygame.K_ESCAPE in inputs["key"]:
                    pause = True
                    inputs["key"].remove(pygame.K_ESCAPE)
            elif pause:
                if pygame.K_ESCAPE in inputs["key"] or pauseButton.get_trigger():
                    pause = False
                    if pygame.K_ESCAPE in inputs["key"]:
                        inputs["key"].remove(pygame.K_ESCAPE)

            if playerSprite.get_hp() <= 0:
                mode = "lose"
            elif playerSprite.rect.colliderect(EndArea):
                inputs["key"] = []
                mode = "pass"

            ''' Output Procedure '''
            # First, the window is filled white
            Window.fill(WHITE)
            # Game objects and sprites are drawn next
            Drawables.draw(Window)
            # Finally, the HUD is drawn
            Hud.draw_hud(Window)
            pauseButton.draw()
            if combat_init == True:
                pygame.draw.rect(Window, BLUE, Back)
                Window.blit(KeySignal, (int(960*xpos_f-int(KeySignal.get_width()/2)), int(400*ypos_f)))
                Window.blit(CombatBar, (int(560*xpos_f), int(600*ypos_f)))
                pygame.draw.rect(Window, BLACK, Pointer)
            if pause:
                Window.blit(Overlay, (0,0))
                Window.blit(pauseText, pauseRect.topleft)
                pauseButton.draw()

        # Upgrade shop
        elif mode == "shop":
            # Update code
            # Fetches data for shop if not already done so
            if not shop_init:
                current_lvls = playerSprite.get_trait_lvls()        # Initial trait levels
                menu_lvls = current_lvls.copy()                     # Trait lvls shown on shop menu
                money_left = get_money()                            # Money left on upgrading traits
                bar_width = Shop.find_obj("hp up").rect.left - Shop.find_obj("hp down").rect.right - round(90 * xpos_f)
                bar_height = Shop.find_obj("hp down").rect.height
                whiteBar = pygame.Surface((bar_width, bar_height))
                whiteBar.fill(WHITE)
                shop_init = True                                    # Shop initialised
            # Updates the prices for the next lvl of each trait
            prices = {"hp": 20 + (10 * (menu_lvls["hp"] + 1)), "speed": 50 + (20 * (menu_lvls["speed"] + 1)),
                      "acc": 40 + (15 * (menu_lvls["acc"] + 1)), "str": 30 + (20 * (menu_lvls["str"] + 1)),
                      "def": 20 + (10 * (menu_lvls["def"] + 1))}
            # Tracks price of trait's current lvls
            prev_prices = {"hp": 20 + (10 * menu_lvls["hp"]), "speed": 50 + (20 * menu_lvls["speed"]),
                           "acc": 40 + (15 * menu_lvls["acc"]), "str": 30 + (20 * menu_lvls["str"]),
                           "def": 20 + (10 * menu_lvls["def"])}
            Shop.update(inputs)                                 # Update's shop menu
            # Iterates through each trait
            for trait in list(menu_lvls.keys()):
                # Trait downgraded and money refunded if trait's down button triggered
                if Shop.find_obj(trait + " down").get_trigger():
                    # Only downgrade if lvl shown is higher than initial lvl
                    if menu_lvls[trait] > current_lvls[trait]:
                        money_left += prev_prices[trait]
                        menu_lvls[trait] -= 1
                # Trait upgraded and cost subtracted if trait's up button triggered
                if Shop.find_obj(trait + " up").get_trigger():
                    # Only upgrade if not already lvl 8 or can afford upgrade
                    if menu_lvls[trait] < 8 and money_left >= prices[trait]:
                        money_left -= prices[trait]
                        menu_lvls[trait] += 1
            # Resets menu lvls and money values if reset button triggered
            if Shop.find_obj("reset").get_trigger():
                menu_lvls = current_lvls.copy()
                money_left = get_money()
            # Money updated and upgrades applied if continue button triggered
            if Shop.find_obj("continue").get_trigger():
                add_money(-(get_money()-money_left))
                for trait in list(menu_lvls.keys()):
                    dlvl = menu_lvls[trait] - current_lvls[trait]
                    if dlvl > 0:
                        playerSprite.upgrade_trait(trait, dlvl)
                mode = "play"                   # Transistions back to the game
                shop_init = False               # De-initialises shop menu
            # Drawing code
            Shop.draw()
            for i in range(1,9):
                marker = pygame.Surface((1, bar_height))
                marker.fill(BLACK)
                whiteBar.blit(marker, (round((bar_width/8)*i), 0))
            for trait in list(menu_lvls.keys()):
                xpos = Shop.find_obj(trait + " down").rect.right + round(20*xpos_f)
                ypos = Shop.find_obj(trait + " down").get_pos()[1]
                Window.blit(whiteBar, (xpos, ypos))
                redBar = pygame.Surface((round((bar_width/8)*menu_lvls[trait]), round((bar_height*(7/9))*ypos_f)))
                redBar.fill(RED)
                Window.blit(redBar, (xpos, ypos+round(5*ypos_f)))
                xpos = Shop.find_obj(trait + " up").rect.right + round(20*xpos_f)
                if menu_lvls[trait] < 8:
                    priceText = subFontRes.render(str(prices[trait]), YELLOW)[0]
                    Window.blit(priceText, (xpos, ypos))
                elif menu_lvls[trait] == 8:
                    maxText = subFontRes.render("Max", YELLOW)[0]
                    Window.blit(maxText, (xpos, ypos))
            # Draws the text showing money left to spend
            moneyLeftTxt = subFontRes.render(str(money_left), YELLOW)[0]
            goldLabelRect = Shop.find_obj("gold").rect
            pos = (goldLabelRect.right + round(10*xpos_f), goldLabelRect.y)
            Window.blit(moneyLeftTxt, pos)

        # The game over procedure is called when the player's health is zero or lower
        elif mode == "lose":
            option = game_over()
            if option == "main":
                mode = "main"
            elif option == "retry":
                mode = "play"
                game_init = False
                loaded = False
                level = 1

        # Handles when the player has cleared a level
        elif mode == "pass":
            cont = lvl_clear(inputs)
            if cont:
                level += 1
                if level > len(os.listdir("levels")):
                    mode = "win"
                else:
                    mode = "shop"
                    loaded = False

        # Handles when the player has won the game
        elif mode == "win":
            game_win()
            if pygame.K_RETURN in inputs["key"]:
                mode = "main"
                inputs["key"].remove(pygame.K_RETURN)

        # Shows fps
        fps = subFontRes.render(str(int(Clock.get_fps())), GREEN, BLACK)[0]
        Window.blit(fps, (0, 0))
        # The window is updated
        pygame.display.flip()
        # Clock object restricts the game to the set ticks per second
        Clock.tick_busy_loop(ticks)
    # Quits and de-initialises Pygame
    pygame.quit()
