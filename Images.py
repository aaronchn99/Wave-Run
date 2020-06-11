import pygame

# Loading font at font size 36
subFont = pygame.font.Font("PressStart2P.ttf", 36)
# Loads the same font, but large for headers
headerFont = pygame.font.Font("PressStart2P.ttf", 72)
# Fonts for labels
labelFont = pygame.font.Font("PressStart2P.ttf", 30)


# Main menu images
# Sets up images for buttons
MenuButton = pygame.Surface((373,56))
MenuButton.fill((110,80,10))
# Start Button
inactiveStartButton = MenuButton.copy()
inactiveStartButton.blit(labelFont.render("Start New", False, (0,0,0)), (0,14))
activeStartButton = MenuButton.copy()
activeStartButton.blit(labelFont.render("Start New", False, (255,255,255)), (0, 14))
pressStartButton = MenuButton.copy()
pressStartButton.blit(labelFont.render("Start New", False, (0,255,0)), (0, 14))
# Load Button
inactiveLoadButton = MenuButton.copy()
inactiveLoadButton.blit(labelFont.render("Load New", False, (0,0,0)), (0, 14))
activeLoadButton = MenuButton.copy()
activeLoadButton.blit(labelFont.render("Load New", False, (255,255,255)), (0, 14))
pressLoadButton = MenuButton.copy()
pressLoadButton.blit(labelFont.render("Load New", False, (0,255,0)), (0, 14))
# Level select Button
inactiveLevelButton = MenuButton.copy()
inactiveLevelButton.blit(labelFont.render("Level Select", False, (0, 0, 0)), (0, 14))
activeLevelButton = MenuButton.copy()
activeLevelButton.blit(labelFont.render("Level Select", False, (255, 255, 255)), (0, 14))
pressLevelButton = MenuButton.copy()
pressLevelButton.blit(labelFont.render("Level Select", False, (0, 255, 0)), (0, 14))
# Tutorial Button
inactiveTutorialButton = MenuButton.copy()
inactiveTutorialButton.blit(labelFont.render("How To Play", False, (0, 0, 0)), (0, 14))
activeTutorialButton = MenuButton.copy()
activeTutorialButton.blit(labelFont.render("How To Play", False, (255, 255, 255)), (0, 14))
pressTutorialButton = MenuButton.copy()
pressTutorialButton.blit(labelFont.render("How To Play", False, (0, 255, 0)), (0, 14))
# Score Button
inactiveScoreButton = MenuButton.copy()
inactiveScoreButton.blit(labelFont.render("Highscores", False, (0, 0, 0)), (0, 14))
activeScoreButton = MenuButton.copy()
activeScoreButton.blit(labelFont.render("Highscores", False, (255, 255, 255)), (0, 14))
pressScoreButton = MenuButton.copy()
pressScoreButton.blit(labelFont.render("Highscores", False, (0, 255, 0)), (0, 14))
# Setting Button
inactiveSettingButton = MenuButton.copy()
inactiveSettingButton.blit(labelFont.render("Settings", False, (0, 0, 0)), (0, 14))
activeSettingButton = MenuButton.copy()
activeSettingButton.blit(labelFont.render("Settings", False, (255, 255, 255)), (0, 14))
pressSettingButton = MenuButton.copy()
pressSettingButton.blit(labelFont.render("Settings", False, (0, 255, 0)), (0, 14))
# Quit Button
inactiveQuitButton = MenuButton.copy()
inactiveQuitButton.blit(labelFont.render("Quit Game", False, (0, 0, 0)), (0, 14))
activeQuitButton = MenuButton.copy()
activeQuitButton.blit(labelFont.render("Quit Game", False, (255, 255, 255)), (0, 14))
pressQuitButton = MenuButton.copy()
pressQuitButton.blit(labelFont.render("Quit Game", False, (0, 255, 0)), (0, 14))

# Settings menu images
settingsBkgd = pygame.Surface((1024, 768))
settingsBkgd.fill((0, 128, 255))
# Text surfaces
settingsTitle = headerFont.render("Settings", False, (59, 29, 0))
GraphicsText = subFont.render("Graphics", False, (255, 0, 0))
ResolutionText = labelFont.render("Resolution", False, (255, 0, 0))
FullscreenText = labelFont.render("Fullscreen", False, (255, 0, 0))
AudioText = subFont.render("Audio", False, (0, 222, 255))
MusicText = labelFont.render("Music", False, (0, 222, 255))
SFXText = labelFont.render("SFX", False, (0, 222, 255))
GameplayText = subFont.render("Gameplay", False, (27, 95, 0))
ControlsText = subFont.render("Controls", False, (27, 95, 0))
LeftText = labelFont.render("Left", False, (27, 95, 0))
RightText = labelFont.render("Right", False, (27, 95, 0))
JumpText = labelFont.render("Jump", False, (27, 95, 0))
DifficultyText = subFont.render("Difficulty", False, (27, 95, 0))
# Slider images
sliderPointerSurfH = pygame.Surface((10, 30))
sliderPointerSurfV = pygame.transform.rotate(sliderPointerSurfH, 90)
tempSurf = pygame.Surface((5, 5))
tempSurf.fill((168, 168, 168))
slideSurfH = pygame.Surface((5, 40))
slideSurfH.set_colorkey((0, 0, 0))
slideSurfH.blit(tempSurf, (0, 17))
slideSurfV = pygame.transform.rotate(slideSurfH, 90)
# Tick box images
tickBoxOffSurf = pygame.Surface((30, 30))
tickBoxOffSurf.fill((255, 255, 255))
tickBoxOnSurf = tickBoxOffSurf.copy()
blackSquare = pygame.Surface((16, 16))
blackSquare.fill((0, 0, 0))
tickBoxOnSurf.blit(blackSquare, (7, 7))
# Drop Menu images
lineSurf = pygame.Surface((258, 42))
lineSurf.fill((255, 255, 255))
# Button images
SettingsButton = pygame.transform.scale(MenuButton.copy(), (220, 50))
# Default button
inactiveDefaultButton = SettingsButton.copy()
inactiveDefaultButton.blit(labelFont.render("Default", False, (0, 0, 0)), (0, 0))
activeDefaultButton = SettingsButton.copy()
activeDefaultButton.blit(labelFont.render("Default", False, (255, 255, 255)), (0, 0))
pressDefaultButton = SettingsButton.copy()
pressDefaultButton.blit(labelFont.render("Default", False, (0, 255, 0)), (0, 0))
# Apply button
inactiveApplyButton = SettingsButton.copy()
inactiveApplyButton.blit(labelFont.render("Apply", False, (0, 0, 0)), (0, 0))
activeApplyButton = SettingsButton.copy()
activeApplyButton.blit(labelFont.render("Apply", False, (255, 255, 255)), (0, 0))
pressApplyButton = SettingsButton.copy()
pressApplyButton.blit(labelFont.render("Apply", False, (0, 255, 0)), (0, 0))
# Back button
inactiveBackButton = SettingsButton.copy()
inactiveBackButton.blit(labelFont.render("Back", False, (0, 0, 0)), (0, 0))
activeBackButton = SettingsButton.copy()
activeBackButton.blit(labelFont.render("Back", False, (255, 255, 255)), (0, 0))
pressBackButton = SettingsButton.copy()
pressBackButton.blit(labelFont.render("Back", False, (0, 255, 0)), (0, 0))
# White Button
WhiteButton = pygame.Surface((350, 34))
WhiteButton.fill((255, 255, 255))

# Shop Images
shopTitle = subFont.render("Upgrades", False, (255, 255, 0))
maxHealth = labelFont.render("Max Health", False, (255, 255, 255))
maxSpeeds = labelFont.render("Max Speeds", False, (255, 255, 255))
Acceleration = labelFont.render("Acceleration", False, (255, 255, 255))
Strength = labelFont.render("Strength", False, (255, 255, 255))
Defence = labelFont.render("Defence", False, (255, 255, 255))
Gold = subFont.render("Gold", False, (255, 255, 255))
bkgSurf = pygame.Surface((1024, 768), pygame.SRCALPHA)
backPanel = pygame.Surface((1024, 652))
backPanel.fill((94,55,0))
bkgSurf.blit(backPanel, (0, 58))
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
EndButton = pygame.transform.scale(MenuButton, (324, 56))
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