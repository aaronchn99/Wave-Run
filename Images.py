import pygame

# Loading the Arcade Classic font at font size 42
subFont = pygame.font.Font("PressStart2P.ttf", 42)
# Loads the same font, but large for headers
headerFont = pygame.font.Font("PressStart2P.ttf", 120)


# Main menu images
# Sets up images for buttons
MenuButton = pygame.Surface((500,70))
MenuButton.fill((110,80,10))
# Start Button
inactiveStartButton = MenuButton.copy()
inactiveStartButton.blit(subFont.render("Start New", False, (0,0,0)), (0,14))
activeStartButton = MenuButton.copy()
activeStartButton.blit(subFont.render("Start New", False, (255,255,255)), (0, 14))
pressStartButton = MenuButton.copy()
pressStartButton.blit(subFont.render("Start New", False, (0,255,0)), (0, 14))
# Load Button
inactiveLoadButton = MenuButton.copy()
inactiveLoadButton.blit(subFont.render("Load New", False, (0,0,0)), (0, 14))
activeLoadButton = MenuButton.copy()
activeLoadButton.blit(subFont.render("Load New", False, (255,255,255)), (0, 14))
pressLoadButton = MenuButton.copy()
pressLoadButton.blit(subFont.render("Load New", False, (0,255,0)), (0, 14))
# Level select Button
inactiveLevelButton = MenuButton.copy()
inactiveLevelButton.blit(subFont.render("Level Select", False, (0, 0, 0)), (0, 14))
activeLevelButton = MenuButton.copy()
activeLevelButton.blit(subFont.render("Level Select", False, (255, 255, 255)), (0, 14))
pressLevelButton = MenuButton.copy()
pressLevelButton.blit(subFont.render("Level Select", False, (0, 255, 0)), (0, 14))
# Tutorial Button
inactiveTutorialButton = MenuButton.copy()
inactiveTutorialButton.blit(subFont.render("How To Play", False, (0, 0, 0)), (0, 14))
activeTutorialButton = MenuButton.copy()
activeTutorialButton.blit(subFont.render("How To Play", False, (255, 255, 255)), (0, 14))
pressTutorialButton = MenuButton.copy()
pressTutorialButton.blit(subFont.render("How To Play", False, (0, 255, 0)), (0, 14))
# Score Button
inactiveScoreButton = MenuButton.copy()
inactiveScoreButton.blit(subFont.render("Highscores", False, (0, 0, 0)), (0, 14))
activeScoreButton = MenuButton.copy()
activeScoreButton.blit(subFont.render("Highscores", False, (255, 255, 255)), (0, 14))
pressScoreButton = MenuButton.copy()
pressScoreButton.blit(subFont.render("Highscores", False, (0, 255, 0)), (0, 14))
# Setting Button
inactiveSettingButton = MenuButton.copy()
inactiveSettingButton.blit(subFont.render("Settings", False, (0, 0, 0)), (0, 14))
activeSettingButton = MenuButton.copy()
activeSettingButton.blit(subFont.render("Settings", False, (255, 255, 255)), (0, 14))
pressSettingButton = MenuButton.copy()
pressSettingButton.blit(subFont.render("Settings", False, (0, 255, 0)), (0, 14))
# Quit Button
inactiveQuitButton = MenuButton.copy()
inactiveQuitButton.blit(subFont.render("Quit Game", False, (0, 0, 0)), (0, 14))
activeQuitButton = MenuButton.copy()
activeQuitButton.blit(subFont.render("Quit Game", False, (255, 255, 255)), (0, 14))
pressQuitButton = MenuButton.copy()
pressQuitButton.blit(subFont.render("Quit Game", False, (0, 255, 0)), (0, 14))

# Settings menu images
settingsBkgd = pygame.Surface((1920, 1080))
settingsBkgd.fill((0, 128, 255))
# Text surfaces
settingsTitle = headerFont.render("Settings", False, (59, 29, 0))
GraphicsText = subFont.render("Graphics", False, (255, 0, 0))
ResolutionText = subFont.render("Resolution", False, (255, 0, 0))
FullscreenText = subFont.render("Fullscreen", False, (255, 0, 0))
AudioText = subFont.render("Audio", False, (0, 222, 255))
MusicText = subFont.render("Music", False, (0, 222, 255))
SFXText = subFont.render("SFX", False, (0, 222, 255))
GameplayText = subFont.render("Gameplay", False, (27, 95, 0))
ControlsText = subFont.render("Controls", False, (27, 95, 0))
LeftText = subFont.render("Left", False, (27, 95, 0))
RightText = subFont.render("Right", False, (27, 95, 0))
JumpText = subFont.render("Jump", False, (27, 95, 0))
DifficultyText = subFont.render("Difficulty", False, (27, 95, 0))
# Slider images
sliderPointerSurfH = pygame.Surface((10, 40))
sliderPointerSurfV = pygame.transform.rotate(sliderPointerSurfH, 90)
tempSurf = pygame.Surface((5, 5))
tempSurf.fill((168, 168, 168))
slideSurfH = pygame.Surface((5, 40))
slideSurfH.set_colorkey((0, 0, 0))
slideSurfH.blit(tempSurf, (0, 17))
slideSurfV = pygame.transform.rotate(slideSurfH, 90)
# Tick box images
tickBoxOffSurf = pygame.Surface((40, 40))
tickBoxOffSurf.fill((255, 255, 255))
tickBoxOnSurf = tickBoxOffSurf.copy()
blackSquare = pygame.Surface((20, 20))
blackSquare.fill((0, 0, 0))
tickBoxOnSurf.blit(blackSquare, (10, 10))
# Drop Menu images
lineSurf = pygame.Surface((40, 100))
lineSurf.fill((255, 255, 255))
# Button images
SettingsButton = pygame.transform.scale(MenuButton.copy(), (315, 70))
# Default button
inactiveDefaultButton = SettingsButton.copy()
inactiveDefaultButton.blit(subFont.render("Default", False, (0, 0, 0)), (0, 0))
activeDefaultButton = SettingsButton.copy()
activeDefaultButton.blit(subFont.render("Default", False, (255, 255, 255)), (0, 0))
pressDefaultButton = SettingsButton.copy()
pressDefaultButton.blit(subFont.render("Default", False, (0, 255, 0)), (0, 0))
# Apply button
inactiveApplyButton = SettingsButton.copy()
inactiveApplyButton.blit(subFont.render("Apply", False, (0, 0, 0)), (0, 0))
activeApplyButton = SettingsButton.copy()
activeApplyButton.blit(subFont.render("Apply", False, (255, 255, 255)), (0, 0))
pressApplyButton = SettingsButton.copy()
pressApplyButton.blit(subFont.render("Apply", False, (0, 255, 0)), (0, 0))
# Back button
inactiveBackButton = SettingsButton.copy()
inactiveBackButton.blit(subFont.render("Back", False, (0, 0, 0)), (0, 0))
activeBackButton = SettingsButton.copy()
activeBackButton.blit(subFont.render("Back", False, (255, 255, 255)), (0, 0))
pressBackButton = SettingsButton.copy()
pressBackButton.blit(subFont.render("Back", False, (0, 255, 0)), (0, 0))
# White Button
WhiteButton = pygame.Surface((330, 59))
WhiteButton.fill((255, 255, 255))

# Shop Images
shopTitle = subFont.render("Upgrades", False, (255, 255, 0))
maxHealth = subFont.render("Max Health", False, (255, 255, 255))
maxSpeeds = subFont.render("Max Speeds", False, (255, 255, 255))
Acceleration = subFont.render("Acceleration", False, (255, 255, 255))
Strength = subFont.render("Strength", False, (255, 255, 255))
Defence = subFont.render("Defence", False, (255, 255, 255))
Gold = subFont.render("Gold", False, (255, 255, 255))
bkgSurf = pygame.Surface((1920, 1080))
bkgSurf.set_colorkey((0,0,0))
backPanel = pygame.Surface((1318, 652))
backPanel.fill((94,55,0))
bkgSurf.blit(backPanel, (301, 242))
# Button images
whiteButton = pygame.Surface((45, 45))
whiteButton.fill((255, 255, 255))
blackLeftArrow, blackRightArrow = subFont.render("<", False, (0,0,0)), subFont.render(">", False, (0,0,0))
greyLeftArrow, greyRightArrow = subFont.render("<", False, (128,128,128)), subFont.render(">", False, (128,128,128))
greenLeftArrow, greenRightArrow = subFont.render("<", False, (0,255,0)), subFont.render(">", False, (0,255,0))
arrow_list = [blackLeftArrow, blackRightArrow, greyLeftArrow, greyRightArrow, greenLeftArrow, greenRightArrow]
for i in range(len(arrow_list)):
    arrow_list[i] = pygame.transform.scale(arrow_list[i], (45, 45))
blackLeftArrow, blackRightArrow, greyLeftArrow, greyRightArrow, greenLeftArrow, greenRightArrow = arrow_list
inactiveLeftButton, inactiveRightButton, activeLeftButton, activeRightButton, pressLeftButton, pressRightButton = [whiteButton.copy() for i in range(6)]
inactiveLeftButton.blit(blackLeftArrow, (0, 0))
inactiveRightButton.blit(blackRightArrow, (0, 0))
activeLeftButton.blit(greyLeftArrow, (0, 0))
activeRightButton.blit(greyRightArrow, (0, 0))
pressLeftButton.blit(greenLeftArrow, (0, 0))
pressRightButton.blit(greenRightArrow, (0, 0))
inactiveResetButton = subFont.render("Reset", False, (0,0,0))
activeResetButton = subFont.render("Reset", False, (128,128,128))
pressResetButton = subFont.render("Reset", False, (0,255,0))
inactiveContinueButton = subFont.render("Continue", False, (0,0,0))
activeContinueButton = subFont.render("Continue", False, (128,128,128))
pressContinueButton = subFont.render("Continue", False, (0,255,0))

# Lose/Win screen buttons
EndButton = pygame.transform.scale(MenuButton, (378, 70))
inactiveMainButton = EndButton.copy()
inactiveMainButton.blit(subFont.render("Main Menu", False, (0, 0, 0)), (0, 14))
activeMainButton = EndButton.copy()
activeMainButton.blit(subFont.render("Main Menu", False, (255, 255, 255)), (0, 14))
pressMainButton = EndButton.copy()
pressMainButton.blit(subFont.render("Main Menu", False, (0, 255, 0)), (0, 14))

inactiveRetryButton = EndButton.copy()
inactiveRetryButton.blit(subFont.render("Retry", False, (0, 0, 0)), (84, 14))
activeRetryButton = EndButton.copy()
activeRetryButton.blit(subFont.render("Retry", False, (255, 255, 255)), (84, 14))
pressRetryButton = EndButton.copy()
pressRetryButton.blit(subFont.render("Retry", False, (0, 255, 0)), (84, 14))

# Pause button
pauseButtonSurf = pygame.Surface((30, 40))
pauseButtonSurf.set_colorkey((0,0,0))
pauseButtonSurf.fill((255,255,255), pygame.Rect(0, 0, 10, 40))
pauseButtonSurf.fill((255,255,255), pygame.Rect(20, 0, 10, 40))