''' Initialisation Procedure '''
# Pygame and window initialisation
import random as rand
import os, ctypes, pygame.freetype, platform
os.environ['SDL_VIDEO_WINDOW_POS'] = "100, 100" # Set window position, prevents window from being placed offscreen
pygame.init()

from entity.Sprites import *
from entity.player import playerClass, update_controls
from entity.platforms import Platform
from entity.wave import Tsunami
from entity.non_player import *
from gui.MenuObjs import *
from Images import *
from var.variables import *
from images.Image import *
from level.World import World
from level.Level import Level

if platform.release() in ("Vista", "7", "8", "9", "10"):
    # Set the program to be DPI aware to avoid window stretching (Only for Vista or later)
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
# Turns off and on fullscreen to fix dodgy fullscreen
pygame.display.set_mode(resolution)
pygame.display.set_mode(resolution, pygame.FULLSCREEN)
# Game program variables
close = False
mode = ScreenMode.MAIN           # Controls what screen to show
loaded = False          # If level has loaded
game_init = False       # If game environment has initialised (Player, HUD, Rects, Pause menu)
shop_init = False       # If shop menu has initialised
combat_init = False     # If combat UI has initialised
pause = False
action_bind = ""        # Used by setting menu, indicates action to be bound
bind_time = 5000        # Milliseconds before key binding is cancelled


'''Classes'''
class Camera(object):
    # Camera constants
    CAM_DIM = (native_res[0]/2, native_res[1]/2)        # Size of world camera
    VIEW_POS = (0, 0)         # Position of viewport on window frame
    VIEW_DIM = (native_res[0], native_res[1]) # Size of viewport when drawn on frame

    # Camera handles scrolling of sprites, so that player is in center
    # Params:
    # cam_dim - Width & height of visible area (aka screen size)
    # course_dim - Width & height of course
    def __init__(self, course_dim):
        self._camRect = pygame.Rect((0, 0), self.CAM_DIM)
        self._courseRect = pygame.Rect((0, 0), course_dim)
        self._vel = (0, 0)

    # Query from player its displacement, set as scroll amount
    # Params:
    # player - The player sprite
    def set_scroll(self, player):
        self._vel = player.set_scroll(self.CAM_DIM)
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

    # Return Rect containing course
    def get_course_rect(self):
        return self._courseRect

    # Moves all sprites and Rects by scrolling amount
    # Params:
    # sprites - Pygame Group object containing all sprites
    # endRect - Rect object representing the finish line
    def apply(self, sprites, endRect):
        dx, dy = round(self._vel[0], 0), round(self._vel[1], 0)
        self._courseRect.x += dx
        self._courseRect.y += dy
        for Sprite in sprites:
            Sprite.scroll((dx, dy))
        endRect.x += dx
        endRect.y += dy

    # Draws sprites onto camera view and returns it as Surface
    # Params:
    # sprites - Pygame group containing drawable sprites
    def draw_camera(self, sprites):
        # Surface to draw game world from view of Camera
        Viewport = pygame.Surface(Camera.CAM_DIM, flags=pygame.SRCALPHA)
        # Game objects and sprites are drawn
        sprites.draw(Viewport)
        return Viewport
    
    # Draws Camera viewport to specified Surface
    # Params:
    # sprites - Pygame group containing drawable sprites
    # surface - Destination surface to draw viewport onto
    def draw_to_surface(self, sprites, surface):
        Viewport = self.draw_camera(sprites)
        # Scale camera viewport
        Viewport = pygame.transform.scale(Viewport, self.VIEW_DIM)
        # Viewport drawn below HUD
        surface.blit(Viewport, self.VIEW_POS)


class HUD(object):
    # HUD Constants
    HUD_POS = (0, 0)
    HUD_DIM = (native_res[0], 208)
    HP_POS = (78, 16)
    HEART_DIM = (70, 65)
    GOLD_POS = (660, 16)
    SCORE_POS = (660, 60)
    EFFECT_POS = (360, 16)
    EFFECT_SPRITE_DIM = (65, 65)
    PROGRESS_POS = (16, 150)

    # Constructs the HUD for the first time
    # Params: (See hud_update)
    def __init__(self, health, max_hp, money, score):
        # HUD background is rendered (TODO: Replace with custom background)
        self.background = pygame.Surface(self.HUD_DIM)
        self.background.fill(BLACK)
        # Using the font loaded in the loading procedure, Text objects are set up and rendered
        # first for the variable labels
        self.hpLabel = subFont.render("Hearts", False, WHITE)
        self.moneyLabel = subFont.render("Gold", False, WHITE)
        self.scoreLabel = subFont.render("Score", False, WHITE)
        self.effectLabel = subFont.render("Effects", False, WHITE)
        self.progressLabel = subFont.render("Course", False, WHITE)
        # Heart sprite list
        # 0: Empty Half heart, 1: Full Half, 2: Empty Whole, 3: Half Whole, 4: Full Whole
        self.HeartSprites = [
            crop(HeartSheet, (0, 0), self.HEART_DIM),
            crop(HeartSheet, (self.HEART_DIM[0], 0), self.HEART_DIM),
            crop(HeartSheet, (self.HEART_DIM[0]*2, 0), self.HEART_DIM),
            crop(HeartSheet, (self.HEART_DIM[0]*3, 0), self.HEART_DIM),
            crop(HeartSheet, (self.HEART_DIM[0]*4, 0), self.HEART_DIM),
        ]
        # Effects sprite dictionary
        self.EffectSprites = {
            Effect.FAST: crop(EffectSheet, (0, 0), self.EFFECT_SPRITE_DIM),
            Effect.SLOW: crop(EffectSheet, (self.EFFECT_SPRITE_DIM[0], 0), self.EFFECT_SPRITE_DIM),
            Effect.KNOCKOUT: crop(EffectSheet, (self.EFFECT_SPRITE_DIM[0]*2, 0), self.EFFECT_SPRITE_DIM),
            Effect.DIZZY: crop(EffectSheet, (self.EFFECT_SPRITE_DIM[0]*3, 0), self.EFFECT_SPRITE_DIM),
            Effect.CANNON: crop(EffectSheet, (self.EFFECT_SPRITE_DIM[0]*4, 0), self.EFFECT_SPRITE_DIM),
            Effect.SHIP: crop(EffectSheet, (self.EFFECT_SPRITE_DIM[0]*5, 0), self.EFFECT_SPRITE_DIM),
        }
        # The update function is called to render Text objects to show initial score and money
        # values and a list of Rects to represent the initial health
        self.hud_update(health, max_hp, money, score)

    # Update the values shown by the HUD
    # Params:
    # health - Player's current health
    # max_hp - Player's maximum health
    # money - Current money count
    # score - Current points
    # effects - List of effects currently applied to player
    # player_progress - Player's position (as proportion of course)
    # wave_progress - Wave's position (as proportion of wave)
    def hud_update(self, hp, max_hp, money, score, effects=[], player_progress=0, wave_progress=0):
        # Sets up the list of hearts
        # It is only set up if the health is larger than 0
        self.Hearts = []
        if hp > 0:
            self.Hearts = [4 for i in range(hp//2)] + [2 for i in range(max_hp//2-hp//2)] + [0 for i in range(max_hp % 2)]
            if hp%2 == 1 :
                self.Hearts[hp//2] += 1
        # Creates a list of active effect types for the draw procedure to use
        effectList = list()
        for effect in effects:
            effectList.append(effect[0])
        self.effect_list = effectList
        # Creates progress bar as one Surface
        self.progressBar = pygame.Surface((740, 42))
        self.progressBar.fill(WHITE, pygame.Rect((0, 0, 14, 42)))
        self.progressBar.fill(WHITE, pygame.Rect((726, 0, 14, 42)))
        self.progressBar.fill(WHITE, pygame.Rect((0, 18, 740, 6)))
        # TODO: Replace red rectangle with player sprite
        self.progressBar.fill(RED, pygame.Rect((round(740 * player_progress - 14), 0, 28, 42)))
        # TODO: Replace wavePointer with custom wave sprite
        wavePointer = pygame.Surface((42, 42))
        wavePointer.fill(BLUE)
        self.progressBar.blit(wavePointer, (round((740 * wave_progress) - 42), 0))
        # The Text object showing the current money and score values are rendered, taking the
        # money and score arguments in string data type
        self.moneyValue = subFont.render(str(money), False, YELLOW)
        self.scoreValue = subFont.render(str(score), False, WHITE)

    # Draws the HUD objects on screen. Takes the window surface and the list of HUD elements
    def draw_hud(self, screen):
        # The image of the HUD background is drawn on the window
        # screen.blit(self.background, self.HUD_POS)
        # The Hearts label is drawn
        screen.blit(self.hpLabel, self.HP_POS)
        # The list of hearts to be drawn is put together as one Surface object and centre-aligned
        # with the "Hearts" label.
        if self.Hearts != []:
            heartRect = pygame.Rect(0, 0, (self.HEART_DIM[0]+3)*len(self.Hearts)-3, self.HEART_DIM[1])
            heartRect.midtop = self.hpLabel.get_rect(topleft=self.HP_POS).midbottom
            heartRect.y += 8
            Hearts = pygame.Surface(heartRect.size, flags=pygame.SRCALPHA)
            for i in range(len(self.Hearts)):
                Hearts.blit(self.HeartSprites[self.Hearts[i]], ((self.HEART_DIM[0]+3) * i, 0))
            screen.blit(Hearts, heartRect.topleft)
        # The "Gold" label is drawn
        screen.blit(self.moneyLabel, self.GOLD_POS)
        # The Text that shows the money amount is drawn next to the Gold label
        pos = list(self.moneyLabel.get_rect(topleft=self.GOLD_POS).topright)
        pos[0] += 20
        screen.blit(self.moneyValue, pos)
        # The "Score" label is drawn
        screen.blit(self.scoreLabel, self.SCORE_POS)
        # Similar to the money amount text, the score value text is drawn next to the Score label
        pos = list(self.scoreLabel.get_rect(topleft=self.SCORE_POS).topright)
        pos[0] += 20
        screen.blit(self.scoreValue, pos)
        # Draws the Effects label
        screen.blit(self.effectLabel, self.EFFECT_POS)
        # The list of effect sprites to be drawn is put together as one Surface object and centre-aligned
        # with the Effects label.
        effect_list = self.effect_list
        if effect_list != []:
            spriteRect = pygame.Rect(0, 0, (self.EFFECT_SPRITE_DIM[0]+5)*len(effect_list)-5, self.EFFECT_SPRITE_DIM[1])
            spriteRect.midtop = self.effectLabel.get_rect(topleft=self.EFFECT_POS).midbottom
            spriteRect.y += 8
            effectSurf = pygame.Surface(spriteRect.size, flags=pygame.SRCALPHA)
            for i in range(len(effect_list)):
                effectSurf.blit(self.EffectSprites[effect_list[i]], ((self.EFFECT_SPRITE_DIM[0]+5) * i, 0))
            screen.blit(effectSurf, spriteRect.topleft)
        # # Draws the progress label
        # screen.blit(self.progressLabel, self.PROGRESS_POS)
        # # Draws the progress bar next to the label
        # pos = list(self.progressLabel.get_rect(topleft=self.PROGRESS_POS).topright)
        # pos[0] += 20
        # screen.blit(self.progressBar, pos)


''' Procedures and Functions '''
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
    Frame.fill(LIGHT_BLUE)
    # Draw camera to Frame
    GameCam.draw_to_surface(Drawables, Frame)
    # Draw HUD
    Hud.draw_hud(Frame)
    playerSprite.update({"key": [right_key]}, (), Platforms, playerGroup)
    Wave.update([], playerSprite)
    winText = headerFont.render("Level Clear", False, GREEN)
    continueText = subFont.render("Press any key to continue", False, GREEN)
    pos = winText.get_rect(center=(int(native_res[0] / 2), int(native_res[1] / 2))).topleft
    Frame.blit(winText, pos)
    pos = continueText.get_rect(center=(int(native_res[0] / 2), int(native_res[1] / 2 + 100))).topleft
    if playerSprite.get_pos()[0] >= native_res[0]:
        Frame.blit(continueText, pos)
        if inputs["key"] != []:
            inputs["key"] = []
            return True
        else:
            return False

# Handles game win procedure
def game_win():
    Frame.fill(WHITE)
    winText = headerFont.render("You win", False, GREEN)
    continueText = labelFont.render("Press enter to go back to menu", False, GREEN)
    pos = winText.get_rect(center=(int(native_res[0] / 2), int(native_res[1] / 2))).topleft
    Frame.blit(winText, pos)
    pos = continueText.get_rect(center=(int(native_res[0] / 2), int(native_res[1] / 2 + 100))).topleft
    Frame.blit(continueText, pos)

# Procedure that applies the settings passed into it
def apply_settings(settings):
    global resolution
    global scale_res
    global origin
    global xpos_f
    global ypos_f
    # Changes scale and position factors depending on resolution
    temp_list = settings["resolution"].split("x")
    resolution = (int(temp_list[0]), int(temp_list[1]))
    scale_res = find_res(resolution)
    origin = (round(resolution[0]/2-(scale_res[0]/2)), round(resolution[1]/2-scale_res[1]/2))
    xpos_f = scale_res[0]/1024
    ypos_f = scale_res[1]/768
    set_screen_settings(xpos_f, ypos_f, origin)
    # Turns on or off fullscreen
    global Window
    if settings["fullscreen"] == True:
        Window = pygame.display.set_mode(resolution, pygame.HWSURFACE | pygame.FULLSCREEN)
    else:
        Window = pygame.display.set_mode(resolution)

if __name__ == "__main__":
    ''' Loading Procedure '''
    # Loading font at font size 36
    subFont = pygame.font.Font("PressStart2P.ttf", 36)
    # Loads the same font, but large for headers
    headerFont = pygame.font.Font("PressStart2P.ttf", 72)
    # Fonts for labels
    labelFont = pygame.font.Font("PressStart2P.ttf", 30)
    # Loading spritesheets
    HeartSheet = pygame.image.load("images\\Hearts.png")
    EffectSheet = pygame.image.load("images\\Effects.png")

    # Loading level data
    game_world = World(LEVEL_ROOT)

    ''' Class instances '''
    # Main Menu components
    Main = Menu("main", [
        Image("main title", 223, 64, headerFont.render("Wave Run", False, (0,198,255))),
        Button("start", 326, 188, inactiveStartButton, activeStartButton, pressStartButton),
        Button("load", 326, 266, inactiveLoadButton, activeLoadButton, pressLoadButton),
        Button("level select", 326, 344, inactiveLevelButton, activeLevelButton, pressLevelButton),
        Button("tutorial", 326, 422, inactiveTutorialButton, activeTutorialButton, pressTutorialButton),
        Button("score", 326, 500, inactiveScoreButton, activeScoreButton, pressScoreButton),
        Button("setting", 326, 578, inactiveSettingButton, activeSettingButton, pressSettingButton),
        Button("quit", 326, 656, inactiveQuitButton, activeQuitButton, pressQuitButton)
    ], {"A": {"left": "A", "right": "A", "up": "G", "down": "B", "obj name": "start"},
        "B": {"left": "B", "right": "B", "up": "A", "down": "C", "obj name": "load"},
        "C": {"left": "C", "right": "C", "up": "B", "down": "D", "obj name": "level select"},
        "D": {"left": "D", "right": "D", "up": "C", "down": "E", "obj name": "tutorial"},
        "E": {"left": "E", "right": "E", "up": "D", "down": "F", "obj name": "score"},
        "F": {"left": "F", "right": "F", "up": "E", "down": "G", "obj name": "setting"},
        "G": {"left": "G", "right": "G", "up": "F", "down": "A", "obj name": "quit"}
        }, pointerSurf=blackRightArrow)
    unavailableText = labelFont.render("This feature is not yet available", False, BLACK)
    # Settings Menu components
    Settings = Menu("settings menu", [
        Image("setting title", 47, 26, settingsTitle),
        Image("graphics label", 36, 132, GraphicsText),
        Image("res label", 36, 188, ResolutionText),
        Image("fullscreen label", 36, 241, FullscreenText),
        Image("audio title", 36, 295, AudioText),
        Image("music label", 36, 347, MusicText),
        Image("sfx label", 36, 399, SFXText),
        Image("gameplay title", 36, 454, GameplayText),
        Image("control label", 137, 504, ControlsText),
        Image("left label", 32, 549, LeftText),
        Image("right label", 32, 592, RightText),
        Image("jump label", 32, 628, JumpText),
        Image("difficulty label", 578, 504, DifficultyText),
        TickBox("fullscreen tick", 765, 250, tickBoxOffSurf, tickBoxOnSurf, state=settings_dict["fullscreen"]),
        Slider("music slider", 425, 347, 570, (0, 100), 10, sliderPointerSurfH, slideSurfH, settings_dict["music vol"]),
        Slider("sfx slider", 425, 399, 570, (0, 100), 10, sliderPointerSurfH, slideSurfH, settings_dict["sfx vol"]),
        Button("set left button", 256, 548, WhiteButton, WhiteButton, WhiteButton),
        Button("set right button", 256, 588, WhiteButton, WhiteButton, WhiteButton),
        Button("set jump button", 256, 628, WhiteButton, WhiteButton, WhiteButton),
        Button("default", 255, 700, inactiveDefaultButton, activeDefaultButton, pressDefaultButton),
        Button("apply", 525, 700, inactiveApplyButton, activeApplyButton, pressApplyButton),
        Button("back", 795, 700, inactiveBackButton, activeBackButton, pressBackButton),
        DropMenu("difficulty list", 659, 549, labelFont, ["Easy", "Normal", "Hard", "Extreme"], lineSurf,
                 sliderPointerSurfV, slideSurfV),
        DropMenu("res list", 700, 188, labelFont, avail_resmodes, lineSurf,
                 sliderPointerSurfV, slideSurfV, current_index=avail_resmodes.index(default_settings["resolution"]),
                 lines=9)
    ], {
        "A": {"left": "A", "right": "A", "up": "K", "down": "C", "obj name": "res list"},
        "B": {"left": "G", "right": "G", "up": "H", "down": "D", "obj name": "set left button"},
        "C": {"left": "C", "right": "C", "up": "A", "down": "F", "obj name": "fullscreen tick"},
        "D": {"left": "G", "right": "G", "up": "B", "down": "E", "obj name": "set right button"},
        "E": {"left": "G", "right": "G", "up": "D", "down": "I", "obj name": "set jump button"},
        "F": {"left": "F", "right": "F", "up": "C", "down": "H", "obj name": "music slider"},
        "G": {"left": "B", "right": "B", "up": "H", "down": "K", "obj name": "difficulty list"},
        "H": {"left": "H", "right": "H", "up": "F", "down": "B", "obj name": "sfx slider"},
        "I": {"left": "K", "right": "J", "up": "E", "down": "A", "obj name": "default"},
        "J": {"left": "I", "right": "K", "up": "G", "down": "A", "obj name": "apply"},
        "K": {"left": "J", "right": "I", "up": "G", "down": "A", "obj name": "back"}
        }, settingsBkgd, pointerSurf=blackRightArrow)
    # Shop Menu components
    Shop = Menu("shop", [
        Image("shop title", 375, 80, shopTitle),
        Image("max health", 49, 166, maxHealth),
        Image("max speeds", 49, 232, maxSpeeds),
        Image("acceleration", 49, 302, Acceleration),
        Image("strength", 49, 372, Strength),
        Image("defence", 49, 438, Defence),
        Image("gold", 49, 634, Gold),
        Button("hp down", 455, 159, inactiveLeftButton, activeLeftButton, pressLeftButton),
        Button("hp up", 809, 159, inactiveRightButton, activeRightButton, pressRightButton),
        Button("speed down", 455, 227, inactiveLeftButton, activeLeftButton, pressLeftButton),
        Button("speed up", 809, 227, inactiveRightButton, activeRightButton, pressRightButton),
        Button("acc down", 455, 295, inactiveLeftButton, activeLeftButton, pressLeftButton),
        Button("acc up", 809, 295, inactiveRightButton, activeRightButton, pressRightButton),
        Button("str down", 455, 363, inactiveLeftButton, activeLeftButton, pressLeftButton),
        Button("str up", 809, 363, inactiveRightButton, activeRightButton, pressRightButton),
        Button("def down", 455, 432, inactiveLeftButton, activeLeftButton, pressLeftButton),
        Button("def up", 809, 432, inactiveRightButton, activeRightButton, pressRightButton),
        Button("reset", 481, 634, inactiveResetButton, activeResetButton, pressResetButton),
        Button("continue", 712, 634, inactiveContinueButton, activeContinueButton, pressContinueButton)
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
    # The game over buttons
    loseMenu = Menu("lose menu", [
        Button("main button", 140, 500, inactiveMainButton, activeMainButton, pressMainButton),
        Button("retry button", 560, 500, inactiveRetryButton, activeRetryButton, pressRetryButton),
        Image("lose title", 188, 348, headerFont.render("Game Over", False, WHITE))
    ], {"A": {"left": "B", "right": "B", "up": "A", "down": "A", "obj name": "main button"},
        "B": {"left": "A", "right": "A", "up": "B", "down": "B", "obj name": "retry button"}
        }, pygame.Surface(native_res), pointerSurf=greenRightArrow)
    # Pause button during gameplay
    pauseButton = Button("pause", 994, 0, pauseButtonSurf, pauseButtonSurf, pauseButtonSurf)

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
        if pygame.K_1 in inputs["key"]:
            add_money(1000)
            inputs["key"].remove(pygame.K_1)

        # Main Menu screen
        if mode == ScreenMode.MAIN:
            Main.update(inputs)     # Update the Menu
            tell = False
            if Main.find_obj("start") != False:
                button = Main.find_obj("start")
                if button.get_trigger():
                    mode = ScreenMode.PLAY       # If the Start New button was triggered, mode is set to "play"
                    game_init = False
                    loaded = False
                    level = game_world.first_level
            if Main.find_obj("setting") != False:
                button = Main.find_obj("setting")
                if button.get_trigger():
                    mode = ScreenMode.SETTINGS
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
                Frame.blit(unavailableText, (0, 738))

        # Settings menu
        elif mode == ScreenMode.SETTINGS:
            # Menu updated if not waiting for key binding
            if action_bind == "":
                Settings.update(inputs)
            # Handles set left button
            if Settings.find_obj("set left button").get_trigger() or action_bind == "left":
                action_bind = "left"
                if inputs["key"] != [] and bind_time <= 5000:
                    if inputs["key"][0] not in (settings_dict["right key"], settings_dict["jump key"]):
                        action_bind = ""
                        settings_dict["left key"] = inputs["key"][0]
                        bind_time = 5000
                    else:
                        bind_time = 8000
                elif bind_time > 5000 and bind_time <= 6000:
                    action_bind = ""
                    bind_time = 5000
                else:
                    bind_time -= Clock.get_time()
                if bind_time < 0:
                    action_bind = ""
                    bind_time = 5000
            # Handles set right button
            if Settings.find_obj("set right button").get_trigger() or action_bind == "right":
                action_bind = "right"
                if inputs["key"] != [] and bind_time <= 5000:
                    if inputs["key"][0] not in (settings_dict["left key"], settings_dict["jump key"]):
                        action_bind = ""
                        settings_dict["right key"] = inputs["key"][0]
                        bind_time = 5000
                    else:
                        bind_time = 8000
                elif bind_time > 5000 and bind_time <= 6000:
                    action_bind = ""
                    bind_time = 5000
                else:
                    bind_time -= Clock.get_time()
                if bind_time < 0:
                    action_bind = ""
                    bind_time = 5000
            # Handles set jump button
            if Settings.find_obj("set jump button").get_trigger() or action_bind == "jump":
                action_bind = "jump"
                if inputs["key"] != [] and bind_time <= 5000:
                    if inputs["key"][0] not in (settings_dict["right key"], settings_dict["left key"]):
                        action_bind = ""
                        settings_dict["jump key"] = inputs["key"][0]
                        bind_time = 5000
                    else:
                        bind_time = 8000
                elif bind_time > 5000 and bind_time <= 6000:
                    action_bind = ""
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
                mode = ScreenMode.MAIN
            # Drawing code
            Settings.draw()
            if action_bind == "left":
                if bind_time <= 5000:
                    label = labelFont.render(str(int(bind_time/1000)+1)+"...", False, BLACK)
                else:
                    label = labelFont.render("Key Used", False, BLACK)
            else:
                label = labelFont.render(pygame.key.name(settings_dict["left key"]), False, BLACK)
            pos = list(label.get_rect(midleft=Settings.find_obj("set left button").rect.midleft).topleft)
            pos[0] += 10
            Frame.blit(label, pos)
            if action_bind == "right":
                if bind_time <= 5000:
                    label = labelFont.render(str(int(bind_time/1000)+1)+"...", False, BLACK)
                else:
                    label = labelFont.render("Key Used", False, BLACK)
            else:
                label = labelFont.render(pygame.key.name(settings_dict["right key"]), False, BLACK)
            pos = list(label.get_rect(midleft=Settings.find_obj("set right button").rect.midleft).topleft)
            pos[0] += 10
            Frame.blit(label, pos)
            if action_bind == "jump":
                if bind_time <= 5000:
                    label = labelFont.render(str(int(bind_time / 1000) + 1)+"...", False, BLACK)
                else:
                    label = labelFont.render("Key Used", False, BLACK)
            else:
                label = labelFont.render(pygame.key.name(settings_dict["jump key"]), False, BLACK)
            pos = list(label.get_rect(midleft=Settings.find_obj("set jump button").rect.midleft).topleft)
            pos[0] += 10
            Frame.blit(label, pos)
            #note = labelFont.render("Note: Currently no sound or difficulty settings", False, BLACK)
            #Frame.blit(note, (10, native_res[1] - note.get_height()))

        # Gameplay mode
        elif mode == ScreenMode.PLAY:
            # Initialises game
            if not game_init:
                PlayerTexture = ColorTexture(RED)
                playerSprite = playerClass("player", 0, 0, 32, 48, PlayerTexture, health, player_accel,
                                           ((max_dx, min_dx), (max_dy, min_dy)), 1, 0.4)
                # Resetting money and score
                reset_money_score()
                # Initialising the HUD's image list
                Hud = HUD(playerSprite.get_hp(), playerSprite.get_max_hp(), get_money(), get_points())
                # Create Pause screen components
                Overlay = pygame.Surface(native_res)
                Overlay.set_alpha(128)
                pauseText = headerFont.render("Paused", False, RED)
                pauseRect = pauseText.get_rect()
                pauseRect.center = (round(native_res[0] / 2), round(native_res[1] / 2))
                game_init = True

            # Constructs a new level when not already loaded
            if not loaded:
                Drawables, Collidables, Platforms, playerGroup, EndArea, Wave = level.build(playerSprite, 1, 1)
                # Camera object that views into world (scrolls screen through course)
                GameCam = Camera((level.w, level.h))
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
                    progress = (playerSprite.get_pos()[0] - GameCam.get_course_rect().left)/(EndArea.left - GameCam.get_course_rect().left)
                    # The wave's progress in the course is calculated
                    wave_progress = (Wave.rect.right - GameCam.get_course_rect().left)/(EndArea.left - GameCam.get_course_rect().left)
                    # The player's tile position is calculated for the score_distance function
                    player_pos = playerSprite.get_pos()[0] - GameCam.get_course_rect().left
                    tile_progress = score_distance(player_pos, tile_progress)
                    # New updated HUD elements are returned to new_values
                    Hud.hud_update(playerSprite.get_hp(), playerSprite.get_max_hp(), get_money(), get_points(),
                                   playerSprite.get_effects(), progress, wave_progress)
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
                        attack_times = rand.randrange(5, 10)
                        progress = 0
                        combat_init = True
                        playerSprite.user_move(inputs, [enemy])
                    if attack_key in inputs["key"]:
                        attack = player_sp * (1 - enemy_ap)
                        progress += attack
                        inputs["key"].remove(attack_key)
                        attack_times -= 1
                        if attack_times == 0:
                            old_key = attack_key
                            while attack_key == old_key:
                                attack_key = rand.randint(97, 122)
                            attack_times = rand.randrange(5, 10)
                    attack = (enemy_sp * (1 - player_ap))*(Clock.get_time()/1000)
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
                    if combat_init:
                        KeySignal = headerFont.render(chr(attack_key).upper(), False, YELLOW)
                        Back = pygame.Rect((0, 0), (100, 100))
                        Back.center = KeySignal.get_rect(topleft=(512-int(KeySignal.get_width()/2), 250)).center
                        CombatBar = pygame.Surface((800, 50))
                        progress_pos = int(800*((player_hp+progress)/(player_hp+enemy_hp)))
                        neutral_pos = int(800*(player_hp/(player_hp+enemy_hp)))
                        CombatBar.fill(RED)
                        CombatBar.fill(WHITE, pygame.Rect(neutral_pos-1, 0, 2, 50))
                        Pointer = pygame.Rect(112+progress_pos-1, 380, 2, 70)
                if pygame.K_ESCAPE in inputs["key"]:
                    pause = True
                    inputs["key"].remove(pygame.K_ESCAPE)
            elif pause:
                if pygame.K_ESCAPE in inputs["key"] or pauseButton.get_trigger():
                    pause = False
                    if pygame.K_ESCAPE in inputs["key"]:
                        inputs["key"].remove(pygame.K_ESCAPE)

            if playerSprite.get_hp() <= 0:
                mode = ScreenMode.LOSE
            elif playerSprite.rect.colliderect(EndArea):
                playerSprite.disable_invincibility()
                if playerSprite.is_sailing():
                    playerSprite.jump_ship()
                inputs["key"] = []
                mode = ScreenMode.PASS

            ''' Output Procedure '''
            # First, the window is filled white
            Frame.fill(LIGHT_BLUE)
            # Draw camera to Frame
            GameCam.draw_to_surface(Drawables, Frame)
            # Finally, the HUD is drawn
            Hud.draw_hud(Frame)
            pauseButton.draw()
            if combat_init == True:
                pygame.draw.rect(Frame, BLUE, Back)
                Frame.blit(KeySignal, (512-int(KeySignal.get_width()/2), 250))
                Frame.blit(CombatBar, (112, 400))
                pygame.draw.rect(Frame, BLACK, Pointer)
            if pause:
                Frame.blit(Overlay, (0,0))
                Frame.blit(pauseText, pauseRect.topleft)
                pauseButton.draw()

        # Upgrade shop
        elif mode == ScreenMode.SHOP:
            # Update code
            # Fetches data for shop if not already done so
            if not shop_init:
                current_lvls = playerSprite.get_trait_lvls()        # Initial trait levels
                menu_lvls = current_lvls.copy()                     # Trait lvls shown on shop menu
                money_left = get_money()                            # Money left on upgrading traits
                bar_width = Shop.find_obj("hp up").rect.left - Shop.find_obj("hp down").rect.right - 90
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
                Level.destroy(Drawables, Collidables, Platforms)
                mode = ScreenMode.PLAY                   # Transistions back to the game
                shop_init = False               # De-initialises shop menu
            # Drawing code
            Shop.draw()
            for i in range(1,9):
                marker = pygame.Surface((1, bar_height))
                marker.fill(BLACK)
                whiteBar.blit(marker, (round((bar_width/8)*i), 0))
            for trait in list(menu_lvls.keys()):
                xpos = Shop.find_obj(trait + " down").rect.right + 20
                ypos = Shop.find_obj(trait + " down").get_pos()[1]
                Frame.blit(whiteBar, (xpos, ypos))
                redBar = pygame.Surface((round((bar_width/8)*menu_lvls[trait]), (bar_height*(7/9))))
                redBar.fill(RED)
                Frame.blit(redBar, (xpos, ypos+5))
                xpos = Shop.find_obj(trait + " up").rect.right + 20
                if menu_lvls[trait] < 8:
                    priceText = subFont.render(str(prices[trait]), False, YELLOW)
                    Frame.blit(priceText, (xpos, ypos))
                elif menu_lvls[trait] == 8:
                    maxText = subFont.render("Max", False, YELLOW)
                    Frame.blit(maxText, (xpos, ypos))
            # Draws the text showing money left to spend
            moneyLeftTxt = subFont.render(str(money_left), False, YELLOW)
            goldLabelRect = Shop.find_obj("gold").rect
            pos = (goldLabelRect.right + 10, goldLabelRect.y)
            Frame.blit(moneyLeftTxt, pos)

        # The game over procedure is called when the player's health is zero or lower
        elif mode == ScreenMode.LOSE:
            Level.destroy(Drawables, playerGroup, Collidables, Platforms)
            option = game_over()
            if option == "main":
                mode = ScreenMode.MAIN
            elif option == "retry":
                mode = ScreenMode.PLAY
                game_init = False
                loaded = False
                level = game_world.first_level

        # Handles when the player has cleared a level
        elif mode == ScreenMode.PASS:
            cont = lvl_clear(inputs)
            if cont:
                if game_world.on_last_level:
                    mode = ScreenMode.WIN
                else:
                    level = game_world.next_level
                    mode = ScreenMode.SHOP
                    loaded = False

        # Handles when the player has won the game
        elif mode == ScreenMode.WIN:
            Level.destroy(Drawables, playerGroup, Collidables, Platforms)
            game_win()
            if pygame.K_RETURN in inputs["key"]:
                mode = ScreenMode.MAIN
                inputs["key"].remove(pygame.K_RETURN)

        # Shows fps
        fps = labelFont.render(str(int(Clock.get_fps())), False, GREEN, BLACK)
        fps.set_alpha(128)
        Frame.blit(fps, (0, 0))
        # Final frame is scaled to output resolution
        FrameToRender = pygame.transform.scale(Frame, scale_res)
        Window.blit(FrameToRender, origin)
        # The window is updated
        pygame.display.flip()
        # Clock object restricts the game to the set ticks per second
        Clock.tick(ticks)
    # Quits and de-initialises Pygame
    pygame.quit()
