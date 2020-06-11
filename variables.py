import pygame
pygame.init()
# Pygame environment variables
window_name = "Game"
avail_resmodes = ["1920x1080", "1920x1200", "1280x1024", "1366x768", "1280x800",
                  "1440x900", "1600x900", "1024x768", "1680x1050"]
screen_resmodes = pygame.display.list_modes()
i = 0
while i < len(avail_resmodes):
    resmode = avail_resmodes[i]
    resmode_list = resmode.split("x")
    resmode_tuple = (int(resmode_list[0]), int(resmode_list[1]))
    if resmode_tuple not in screen_resmodes:
        avail_resmodes.remove(resmode)
    else:
        i += 1
resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
native_res = (1920, 1080)
ticks = 60
Window = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
Frame = pygame.Surface(native_res)
pygame.display.set_caption(window_name)
Clock = pygame.time.Clock()
tile_dim = (40, 40)
xpos_f = 1.0
ypos_f = 1.0
# Gameplay variables
money = 0
score = 0
health = 2
# Physics constants and variables
player_accel = 0.2
max_dy = 6
min_dy = -6
max_dx = 7
min_dx = -7
player_x = 960
player_y = 354
g = 0.4
# Declaring colour constants
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
# Controls
left_key = pygame.K_LEFT
right_key = pygame.K_RIGHT
jump_key = pygame.K_UP
# Declaring the inputs dictionary
inputs = {"queue":[],               # Stores current queue of interrupts
          "key":[],                 # Tracks pressed keys
          "k hold tick":0,          # How long a key is pressed without being interrupted
          "m pos":[0,0],            # Tracks cursor's current position
          "m vel":[0,0],            # Tracks cursor's speed
          "click pos":[-1,-1],      # Cursor position when clicked
          "m button":"",            # Mouse button being clicked
          "m hold tick":0,          # How long mouse button is held for
          "close":False}            # Close program signal
# Default settings
default_settings = {
    "resolution": "1920x1080",
    "fullscreen": True,
    "music vol": 100,
    "sfx vol": 100,
    "left key": pygame.K_LEFT,
    "right key": pygame.K_RIGHT,
    "jump key": pygame.K_UP,
    "difficulty": "Easy"
}
resmode = str(resolution[0]) + "x" + str(resolution[1])
if resmode in avail_resmodes:
    default_settings["resolution"] = resmode
else:
    print("Error: Your native resolution is not supported")
# Settings dictionary
settings_dict = default_settings.copy()
# List storing all object names
obj_names = []

'''Functions'''
# Procedure that gets inputs from queue and parses them into inputs
def update_input():
    inputs["m pos"] = (round(pygame.mouse.get_pos()[0]/xpos_f), round(pygame.mouse.get_pos()[1]/ypos_f))
    inputs["m vel"] = pygame.mouse.get_rel()
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            inputs["key"].append(event.key)             # Adds pressed key
            inputs["k hold tick"] = 0                   # Resets key hold tick
        if event.type == pygame.KEYUP:
            if event.key in inputs["key"]:
                inputs["key"].remove(event.key)         # Removes unpressed key
                inputs["k hold tick"] = 0               # Resets key hold tick
        if event.type == pygame.QUIT:
            inputs["close"] = True                      # Triggers close signal
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                inputs["m button"] = "l"                # Left mouse button
            elif event.button == 2:
                inputs["m button"] = "m"                # Scroll wheel click
            elif event.button == 3:
                inputs["m button"] = "r"                # Right mouse button
            elif event.button == 4:
                inputs["m button"] = "u"                # Scroll up
            elif event.button == 5:
                inputs["m button"] = "d"                # Scroll down
            inputs["click pos"] = (round(pygame.mouse.get_pos()[0]/xpos_f), round(pygame.mouse.get_pos()[1]/ypos_f))
        if event.type == pygame.MOUSEBUTTONUP:
            inputs["m button"] = ""
            inputs["m hold tick"] = 0                     # Resets mouse hold tick
            inputs["click pos"] = [-1,-1]
        inputs["queue"].append(event)
    if inputs["m button"] == "l":
        inputs["m hold tick"] += 1                        # Increments mouse hold tick when left mouse button is clicked
    if inputs["key"] != []:
        inputs["k hold tick"] += 1                      # Increments key hold tick when a key is being pressed


# Function that checks availability of an object name
def check_name(name):
    done = False        # Flag indicating if a unique name is found
    i = 0               # Integer suffix added if name already used
    new_name = name     # Holds the next available name
    while not done:
        if new_name not in obj_names:
            obj_names.append(new_name)  # Added to object names list
            done = True                 # Breaks the loop
        else:
            i += 1                      # Gets next integer
            new_name = name + str(i)    # Appends new integer to name
            print("Warning: Obj name " + name + " changed to " + new_name)
    return new_name                     # Returns the name found


# Function that adds points based on distance covered
def score_distance(player_pos, progress):
    global score
    tile_pos = int(player_pos/tile_dim[0])      # Calculates player position in tiles
    if tile_pos > progress:
        dx = tile_pos - progress                # Change in tile distance
        score += 10 * dx                        # Adds 10 times dx points
        progress += dx                          # Adds change in tile distance to progress
    return progress                             # Returns progress


# Function to add to score within local scopes
def add_points(points):
    global score
    score += points


# Function to add to money within local scopes
def add_money(amount):
    global money
    money += amount


# Function to return the current score
def get_points():
    global score
    return score


# Function to return the current amount of money
def get_money():
    global money
    return money

# Reset money and score
def reset_money_score():
    global money
    global score
    money = 0
    score = 0


def set_scale(xf, yf):
    global xpos_f
    global ypos_f
    xpos_f = xf
    ypos_f = yf