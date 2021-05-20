from var.variables import *
import pygame
p_speed = 5


''' Classes '''
hitbox_mode = 0
# Base class for Menu Objects (TODO: Refactor out unnecessary code)
class Entity(pygame.sprite.Sprite):
    # The class constructor. Takes the sprite name, position, dimensions and fill colour
    def __init__(self, name, x, y, width, height, color=None, image=None, animation=None):
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
            self.image = image.convert_alpha()
            self.image = pygame.transform.scale(self.image, (self._w, self._h))
            self._render_mode = "image"
        elif color != None:
            self.image = pygame.Surface((self._w, self._h), flags=pygame.SRCALPHA)
            self.image.fill(color)
            self._render_mode = "color"
        elif animation != None:
            self._animation = animation
            self.image = self._animation.frames[0]
            self._render_mode = "animate"
        else:
            self.image = pygame.Surface((self._w, self._h), flags=pygame.SRCALPHA)
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
        self.image = self._animation.next_frame(Clock.get_time())

    # Returns the rendering mode (color/image/animate/black)
    def get_render_mode(self):
        return self._render_mode

    def kill(self):
        remove_name(self._name)
        super().kill()


# Base class for interactive menu objects
class guiObj(Entity):
    # Constructor for gui objects
    def __init__(self, name, x, y, width, height, color=None, image=None):
        super().__init__(name, x, y, width, height, color, image)

    # Called when selected by keyboard
    def when_select(self):
        pass

    # Called when not selected by keyboard
    def when_not_select(self):
        pass

    # Called when user moves pointer after pressing enter
    def when_deselect(self):
        pass

    # Called when Menu focuses on object
    def when_focus(self, inputs):
        pass

    # Called to handle mouse inputs
    def mouse_input(self, inputs):
        pass

    # Removes Entity scroll method by overriding
    def scroll(self, vel):
        pass


# Class for images in Menus
class Image(guiObj):
    # Class constructor
    def __init__(self, name, x, y, imageSurf, width=None, height=None):
        # If no dimensions are given, imageSurf's dimensions are used by default
        if width == None and height == None:
            width = imageSurf.get_width()
            height = imageSurf.get_height()
        # Entity's constructor is called
        super().__init__(name, x, y, width, height, None, imageSurf)
        # Resizes image depending on set resolution
        self.image = pygame.transform.scale(self.image, (self._w, self._h))


# Class for clickable buttons in menus
class Button(guiObj):
    # Class constructor
    def __init__(self, name, x, y, inactive_img, active_img, press_img):
        super().__init__(name, x, y, inactive_img.get_width(), inactive_img.get_height(), None, inactive_img)
        self._off_img = pygame.transform.scale(inactive_img, (self._w, self._h))   # Image shown when button is not selected
        self._on_img = pygame.transform.scale(active_img, (self._w, self._h))      # Image shown when button is selected
        self._press_img = pygame.transform.scale(press_img, (self._w, self._h))    # Image shown when pressed
        self._active = False                # Boolean determining if selected
        self._pressed = False               # Boolean determining if pressed
        self._trigger = False               # Boolean determining whether to trigger action

    # Returns if the button is triggered
    def get_trigger(self):
        if self._trigger:
            self._trigger = False   # Trigger turned off as it is returned
            return True
        else:
            return False

    # Returns a Boolean determining whether the button is pressed
    def get_pressed(self):
        return self._pressed

    # Procedure when keyboard input selects this button
    def when_select(self):
        self._pressed = True

    # Procedure when keyboard inputs does not select this button
    def when_not_select(self):
        # Only does something if button was pressed in the last tick
        if self._pressed:
            self._trigger = True    # Button is triggered
            self._pressed = False   # Button is unpressed

    # Procedure when inputs deselect this object
    def when_deselect(self):
        self._pressed = False       # Unpresses the button

    # Procedure that handles response to mouse inputs
    def mouse_input(self, inputs):
        if self.rect.collidepoint(inputs["m pos"]):
            self._active = True         # Button is active when cursor hovers over it
        else:
            self._active = False        # Otherwise, it is inactive
        # Tests if clicked on the button
        if inputs["m button"] == "l" and self._active and self.rect.collidepoint(inputs["click pos"]):
            self._pressed = True        # Pressed when left clicked on button and active
        else:
            if self._pressed:
                if inputs["m button"] == "":
                    self._trigger = True    # If pressed and just unclicked, trigger is enabled
                else:
                    self.when_deselect()    # Otherwise, button is deselected
            self._pressed = False       # Pressed is set to false

    # Updates the button
    def update(self):
        if self._active:
            self.image = self._on_img   # If active, image is set to the active image
        else:
            self.image = self._off_img  # Otherwise, image is set to the inactive image
        if self._pressed:
            self.image = self._press_img # When pressed, image is set to pressed image


# Class for Sliders
class Slider(guiObj):
    # Class constructor
    def __init__(self, name, x, y, length, value_range, increment, pointerSurf, slideSurf, current_value=None, orientation="h"):
        self._len = length                  # The length of the slider (Longest side)
        self._orientation = orientation     # The slider's orientation (Horizontal or vertical)
        self._low = value_range[0]          # Lowest value
        self._hi = value_range[1]           # Highest value
        self._range = self._hi - self._low  # The range of the value
        self._increment = increment         # How much the value changes per key tap
        if current_value is None:
            self._val = self._low           # Default value is set to the lowest value
        else:
            self._val = current_value       # If a start value is specified, it is assigned to val
        self._active = False                # Determines if slider is draggable
        if orientation == "h":                  # When the slider is horizontal
            height = pointerSurf.get_height()   # Slider height is set to pointer's height
            super().__init__(name, x, y, self._len, height)            # Superclass constructor called
            self._slideSurf = pygame.transform.scale(slideSurf, (self._w, self._h))    # Slider image scale to new size
            self._xmin = self._x                  # Minimum x pos of pointer
            self._xmax = self._x + self._w      # Max x pos of pointer
            centerx = int(self._x+(((self._val-self._low)/self._range)*self._w))    # Pointer's center coordinates
            centery = int(self._y+(self._h/2))                                         # Ditto
            self._pointerRect = pointerSurf.get_rect(center=(centerx,centery))  # Pointer's rect
        elif orientation == "v":                # When slider is vertical
            width = pointerSurf.get_width()     # Slider width is set to pointer's width
            super().__init__(name, x, y, width, self._len)             # Calls superclass constructor
            self._slideSurf = pygame.transform.scale(slideSurf, (self._w, self._h))     # Slider image scale to new size
            self._ymin = self._y                  # Min y pos of pointer
            self._ymax = self._y + self._h        # Max y pos of pointer
            centerx = int(self._x + (self._w / 2))                                          # Pos of pointer's center
            centery = int(self._y + (((self._val - self._low) / self._range) * self._h))    # Ditto
            self._pointerRect = pointerSurf.get_rect(center=(centerx, centery))             # Pointer's rect
        self._slideRect = self._slideSurf.get_rect(topleft=(self._x,self._y))               # Slider's rect
        self._pointerSurf = pointerSurf                                                     # Pointer's image

    # Moves the slider to a specific coordinate
    def move_to(self, x, y):
        self._x, self._y = x, y
        self._slideRect.topleft = (x, y)
        if self._orientation == "h":
            centerx = int(self._x + (((self._val - self._low) / self._range) * self._w))
            centery = int(self._y + (self._h / 2))
            self._xmin = self._x
            self._xmax = self._x + self._w
        elif self._orientation == "v":
            centerx = int(self._x + (self._w / 2))
            centery = int(self._y + (((self._val - self._low) / self._range) * self._h))
            self._ymin = self._y
            self._ymax = self._y + self._h
        self._pointerRect = self._pointerSurf.get_rect(center=(centerx, centery))

    # Moves pointer up one increment
    def increase(self):
        if self._orientation == "h":
            dx = (self._increment/self._range)*self._len
            self._pointerRect.move_ip(dx, 0)                # Moves pointer to the right
        elif self._orientation == "v":
            dy = (self._increment/self._range)*self._len
            self._pointerRect.move_ip(0, dy)                # Moves pointer down

    # Moves pointer down one increment
    def decrease(self):
        if self._orientation == "h":
            dx = -(self._increment / self._range) * self._len
            self._pointerRect.move_ip(dx, 0)                # Moves pointer to the left
        elif self._orientation == "v":
            dy = -(self._increment / self._range) * self._len
            self._pointerRect.move_ip(0, dy)                # Moves pointer up

    # Set slider value
    def set_value(self, val):
        if val >= self._low and val <= self._hi:
            self._val = val
            if self._orientation == "h":
                centerx = int(self._x + (((self._val - self._low) / self._range) * self._w))
                centery = int(self._y + (self._h / 2))
                self._pointerRect.center = (centerx, centery)
            elif self._orientation == "v":
                centerx = int(self._x + (self._w / 2))
                centery = int(self._y + (((self._val - self._low) / self._range) * self._h))
                self._pointerRect.center = (centerx, centery)
        else:
            print("Error: " + self._name + " slider - " + str(val) + " is out of range")

    # Returns current pointer value
    def get_value(self):
        return self._val

    # Returns slider's active state
    def get_active(self):
        return self._active

    # Called when selected by keyboard
    def when_select(self):
        self._active = True     # Makes slider draggable

    # Called when menu focuses on Slider object
    def when_focus(self, inputs):
        if self._orientation == "h":    # When slider horizontal
            if inputs["k hold tick"] % p_speed == 0 and inputs["k hold tick"] >= 30 or inputs["k hold tick"] == 1:
                if pygame.K_LEFT in inputs["key"]:
                    self.decrease()     # Pointer moves left when user presses left
                elif pygame.K_RIGHT in inputs["key"]:
                    self.increase()     # Pointer moves right when user presses right
        elif self._orientation == "v":  # When slider vertical
            if inputs["k hold tick"] % p_speed == 0 and inputs["k hold tick"] >= 30 or inputs["k hold tick"] == 1:
                if pygame.K_UP in inputs["key"]:
                    self.decrease()     # Pointer moves up when user presses up
                elif pygame.K_DOWN in inputs["key"]:
                    self.increase()     # Pointer moves down when user presses down
        if pygame.K_RETURN in inputs["key"]:
            self._active = False        # Slider deselected when user presses enter while being focused

    # Handles mouse inputs
    def mouse_input(self, inputs):
        if inputs["m button"] == "l" and self._slideRect.collidepoint(inputs["click pos"]) \
                or self._pointerRect.collidepoint(inputs["click pos"]):
            self._active = True     # Slider active when mouse clicked inside slider
        elif inputs["m button"] != "l":
            self._active = False    # Slider deactivated when mouse unclicks
        if self._active:            # If slider is active
            if self._orientation == "h":
                self._pointerRect.centerx = inputs["m pos"][0]  # Pointer follows cursor's x pos when horizontal
            elif self._orientation == "v":
                self._pointerRect.centery = inputs["m pos"][1]  # Pointer follows cursor's y pos when vertical

    # Slider is drawn onto the screen
    def draw(self):
        Frame.blit(self._slideSurf, (self._x, self._y))    # Draw the slider image
        Frame.blit(self._pointerSurf, self._pointerRect.topleft)   # Draw the pointer image

    # Updates the slider's value
    def update(self):
        if self._orientation == "h":        # When horizontal
            if self._pointerRect.centerx <= self._xmin:
                self._pointerRect.centerx = self._xmin        # Prevents pointer from moving off the left
            elif self._pointerRect.centerx >= self._xmax:
                self._pointerRect.centerx = self._xmax        # Prevents pointer from moving off the right
            self._val = self._low+self._range*((self._pointerRect.centerx-self._xmin)/self._len)    # Value updated
        elif self._orientation == "v":      # When vertical
            if self._pointerRect.centery <= self._ymin:
                self._pointerRect.centery = self._ymin        # Prevents pointer from moving off the top
            elif self._pointerRect.centery >= self._ymax:
                self._pointerRect.centery = self._ymax        # Prevents pointer from moving off the bottom
            self._val = self._low+self._range*((self._pointerRect.centery-self._ymin)/self._len)    # Value updated


# Toggleable buttons to turn on or off an option
class TickBox(guiObj):
    # Class constructor
    def __init__(self, name, x, y, inactive_img, active_img, state=False):
        super().__init__(name, x, y, inactive_img.get_width(), inactive_img.get_height(), None, inactive_img)
        self._state = state             # The tick box's on/off state
        self._offSurf = pygame.transform.scale(inactive_img, (self._w, self._h))    # Image shown when turned off
        # Image when turned on. Resized to be the same size as offSurf
        self._onSurf = pygame.transform.scale(active_img, (self._w, self._h))
        self._is_pressed = False

    # Toggles the tick box's state
    def toggle(self):
        if self._state == True:
            self._state = False     # Box turned off when previously on
        else:
            self._state = True      # Box turned on when previously off

    # Sets the tick box state
    def set_state(self, state):
        self._state = state

    # Returns TickBox's current state
    def get_state(self):
        return self._state

    # Handles when keyboard selected
    def when_select(self):
        if not self._is_pressed:
            self.toggle()   # Toggle's TickBox when selected
            self._is_pressed = True     # Tick box is pressed

    # Handled when not keyboard selected
    def when_not_select(self):
        self._is_pressed = False        # Tick box is not pressed

    # Handles when keyboard deselects this tick box
    def when_deselect(self):
        self._is_pressed = False        # Tick box is not pressed

    # Handles mouse inputs
    def mouse_input(self, inputs):
        # Toggles TickBox when clicked for 1 tick within the TickBox's rect area
        if inputs["m button"] == "l" and self.rect.collidepoint(inputs["click pos"]) and inputs["m hold tick"] == 1:
            self.toggle()

    # Updates TickBox's appearance
    def update(self):
        if self._state == True:
            self.image = self._onSurf   # On image used when state is on
        else:
            self.image = self._offSurf  # Off image used when state is off


# Class for drop down menus
class DropMenu(guiObj):
    # Class constructor. Font
    def __init__(self, name, x, y, Font, option_list, lineSurf, scrollPointerSurf, scrollSlideSurf, text_color=(0,0,0),
                 current_index=0, lines=3):
        char = Font.render("A", False, (0,0,0))                 # A character created for measurement
        # Length is the length of longest option, +1 to allow for the scrollbar
        lengths = []
        for op in option_list:
            lengths.append(Font.render(op, False, (0,0,0)).get_width())
        length = max(lengths)+char.get_width()
        height = int(1.5*char.get_height())                      # Height is the height of the character
        super().__init__(name, x, y, length, height, None)  # Calls superclass constructor
        self._Font = Font                                   # Text font
        self._txt_color = text_color                        # Text colour
        self._options = option_list                         # The list of options
        self._current = self._options[current_index]        # The currently selected option
        self._dropped = False                               # True if drop menu is dropped
        self._pointed_line = -1                             # Line of the drop list that is pointed
        self._list_index = 0                                # Index of options list where dropped list starts
        # Sets the drop list size to the value passed, unless larger than options list
        if lines > len(self._options):
            self._list_size = len(self._options)
        else:
            self._list_size = lines
        # Drop list set up with list index as the start index
        self._drop_list = self._options[self._list_index:self._list_index+self._list_size]
        # Rect object of the drop down box, excluding the list
        self._boxRect = pygame.Rect(self._x, self._y, self._w, self._h)
        # List of rects for each line of the drop down list
        self._rects_list = []
        for i in range(1, self._list_size + 1):
            self._rects_list.append(pygame.Rect(self._x,self._y+self._h*i,self._w-char.get_width(),self._h))
        # The image for a line is re-sized to set dimensions
        self._lineSurf = pygame.transform.scale(lineSurf, (self._w, self._h))
        # Variables needed to create Scroll slider
        low = 0
        scroll_x = self._x+self._w-char.get_width()
        scroll_y = self._y+self._h
        scroll_w = char.get_width()
        scroll_h = self._boxRect.height*self._list_size
        # Image surfaces needed for scrollbar
        scrollSlideSurf = pygame.transform.scale(scrollSlideSurf, (scroll_w, scroll_h))
        if self._list_size < len(self._options):
            high = len(self._options) - self._list_size
            scrollPointerSurf = pygame.transform.scale(scrollPointerSurf, (scroll_w, scrollPointerSurf.get_height()))
        else:
            high = 0.1
            scrollPointerSurf = pygame.Surface((0,0))
        # Scrollbar created
        self._Scrollbar = Slider(self._name+" scroll", scroll_x, scroll_y, scroll_h, (low, high), 1, scrollPointerSurf,
                                 scrollSlideSurf, self._list_index, "v")

    # Returns the state of the dropped list
    def get_dropped(self):
        return self._dropped

    # Sets the list to drop
    def drop_down(self):
        self._dropped = True

    # Sets the list to pull up
    def drop_up(self):
        self._dropped = False

    # Scrolls the drop list up
    def scroll_up(self):
        self._Scrollbar.decrease()      # Moves the scrollbar pointer up
        self._Scrollbar.update()        # Updates scrollbar
        self._list_index = round(self._Scrollbar.get_value())     # Sets start index to scrollbar value
        # Updates the drop list
        self._drop_list = self._options[self._list_index:self._list_index+self._list_size]

    # Scrolls the drop list down
    def scroll_down(self):
        self._Scrollbar.increase()      # Moves the scrollbar pointer up
        self._Scrollbar.update()        # Updates scrollbar
        self._list_index = round(self._Scrollbar.get_value())     # Sets start index tp scrollbar value
        # Updates drop list
        self._drop_list = self._options[self._list_index:self._list_index + self._list_size]

    # Sets the pointer to the passed line number
    def select_line(self, line):
        self._pointed_line = line

    # Set current option
    def set_option(self, option):
        if option in self._options:
            self._current = option
        else:
            print("Error: " + self._name + " - " + option + " not in option list")

    # Returns the currently selected option
    def get_option(self):
        return self._current

    # Draws the drop menu
    def draw(self):
        Frame.blit(self._lineSurf, (self._x, self._y))
        Frame.blit(self._Font.render(self._current, False, self._txt_color), (self._x, self._y))
        if self._dropped:
            for i in range(self._list_size):
                Frame.blit(self._lineSurf, self._rects_list[i])
                Label = self._Font.render(self._drop_list[i], False, self._txt_color)
                if i == self._pointed_line:
                    Label = pygame.transform.scale(Label, (int(Label.get_width()*1.1), int(Label.get_height()*1.1)))
                Frame.blit(Label, self._rects_list[i].topleft)
            self._Scrollbar.draw()

    # Procedure when selected by keyboard
    def when_select(self):
        self.drop_down()

    # Procedure when focused by keyboard
    def when_focus(self, inputs):
        if inputs["k hold tick"] == 1 or inputs["k hold tick"] % p_speed == 0 and inputs["k hold tick"] >= 30:
            if pygame.K_UP in inputs["key"]:
                if self._pointed_line <= 0:
                    if self._list_size < len(self._options):
                        self.scroll_up()
                else:
                    self._pointed_line -= 1
            elif pygame.K_DOWN in inputs["key"]:
                if self._pointed_line >= self._list_size - 1:
                    if self._list_size < len(self._options):
                        self.scroll_down()
                else:
                    self._pointed_line += 1
            elif pygame.K_RETURN in inputs["key"] and inputs["k hold tick"] == 1:
                self._current = self._drop_list[self._pointed_line]
                self.drop_up()

    # Handles mouse inputs
    def mouse_input(self, inputs):
        if inputs["m button"] == "l" and self._boxRect.collidepoint(inputs["click pos"])\
                and inputs["m hold tick"] == 1:
            if self._dropped == False:
                self._dropped = True
            elif self._dropped == True:
                self._dropped = False
        if self._dropped:
            if self._list_size < len(self._options):
                self._Scrollbar.mouse_input(inputs)
                self._Scrollbar.update()
                self._list_index = round(self._Scrollbar.get_value())
                self._drop_list = self._options[self._list_index:self._list_index+self._list_size]
            hover = False
            if not self._Scrollbar.get_active():
                for i in range(self._list_size):
                    rect = self._rects_list[i]
                    if rect.collidepoint(inputs["m pos"][0], inputs["m pos"][1]):
                        if rect.collidepoint(inputs["click pos"]) and inputs["m button"] == "l":
                            self._current = self._drop_list[i]
                            self._dropped = False
                        else:
                            self._pointed_line = i
                        hover = True
                if not hover:
                    self._pointed_line = -1
                    if inputs["m button"] == "l" and inputs["m hold tick"] == 1 and\
                            not self._boxRect.collidepoint(inputs["click pos"]):
                        if self._dropped == True:
                            self._dropped = False


# Class for Menu screens
class Menu(object):
    # Class constructor requires name (string), objects (list), gui_map (2D array)
    def __init__(self, name, objects, gui_map, bkgSurf=None, pointerSurf=None):
        self._name = check_name(name)       # Name to identify this Menu
        self._objs = objects                # List of objects on the Menu
        self.validate_map(gui_map)          # Validates gui map
        self._map = gui_map                 # Dict map for keyboard to navigate around
        self._pointer = "A"                 # Position of keyboard pointer [column, row]
        self._inp_mode = ""                 # Mode of input, either keyboard or mouse
        if bkgSurf == None:
            self._back = pygame.Surface(native_res)
            self._back.fill((255,255,255))
        else:
            self._back = bkgSurf    # Image drawn as backdrop
        self._focus = None      # The GUI object that is being focused for input
        # If no pointer image is given, the menu uses a 40x40 pixel black square by default
        if pointerSurf == None:
            self._pointSurf = pygame.Surface((40, 40))
            self._pointSurf.fill((0,0,0))
        else:
            self._pointSurf = pointerSurf   # If given, pointer image is set as attribute

    # Validates gui maps for empty or incorrect entries
    def validate_map(self, map):
        for node in list(map.keys()):       # Iterate through each node
            if type(node) != str:           # Outputs warning if node not a string
                print("Warning: " + self._name + " menu's node " + str(node) + " is not a string")
            for field in list(map[node].keys()):        # Iterate each field of current node
                if type(map[node][field]) != str:       # Warning if field value not a string
                    print("Warning: " + self._name + " menu's node " + node + "'s " + field + " value is not a string")
                elif map[node][field] == "":            # Warning if field value empty
                    print("Warning: " + self._name + " menu's node " + node + "'s " + field + " value is empty")
                else:
                    if field in ("left", "right", "up", "down"):        # If directional field
                        if len(map[node][field]) != 1:                  # Warning if field value not one character
                            print("Warning: " + self._name + " menu's node " + node + "'s " + field +
                                  " value is not 1 character")
                        elif map[node][field] not in list(map.keys()):  # Warning if field value not a node
                            print("Warning: " + self._name + " menu's node " + node + "'s " + field +
                                  " value is not one of the nodes")
                    if field == "obj name":
                        if not self.find_obj(map[node][field]):         # Warning if field value not an object name
                            print("Warning: " + self._name + " menu's node " + node + "'s " + field +
                                  " value is not a name of one of the available objects")

    # Returns Menu's name
    def get_name(self):
        return self._name

    # Finds the object with the passed name
    def find_obj(self, name):
        obj = None  # Holds the object found (None if not found)
        i = 0       # Index currently looked at
        while obj == None and i < len(self._objs):
            if self._objs[i].get_name() == name:
                obj = self._objs[i]  # If matched with name, object set to obj
            i += 1      # Current index increases
        if obj != None:
            return obj  # Returns object if found
        else:
            return False    # Otherwise, False is returned

    # Handles keyboard inputs
    def key_input(self, inputs):
        obj = self.find_obj(self._map[self._pointer]["obj name"])  # The pointed object
        # If an object is focused (Only Sliders and Drop Menus can be focused here)
        if self._focus is not None:
            self._focus.when_focus(inputs)  # Focused object's focus method is called
            if pygame.K_RETURN in inputs["key"] and inputs["k hold tick"] == 1:
                self._focus = None          # Focused object is unfocused if enter key pressed
                inputs["key"].remove(pygame.K_RETURN)   # Enter key removed from inputs
        else:
            # If left key is pressed
            if pygame.K_LEFT in inputs["key"]:
                if inputs["k hold tick"] % p_speed == 0 and inputs["k hold tick"] >= 30 or inputs["k hold tick"] == 1:
                    obj.when_deselect()         # Deselects previous object
                    self._pointer = self._map[self._pointer]["left"]
            # If right key is pressed
            elif pygame.K_RIGHT in inputs["key"]:
                if inputs["k hold tick"] % p_speed == 0 and inputs["k hold tick"] >= 30 or inputs["k hold tick"] == 1:
                    obj.when_deselect()         # Deselects previous object
                    self._pointer = self._map[self._pointer]["right"]
            # If up key is pressed
            elif pygame.K_UP in inputs["key"]:
                if inputs["k hold tick"] % p_speed == 0 and inputs["k hold tick"] >= 30 or inputs["k hold tick"] == 1:
                    obj.when_deselect()         # Deselects previous object
                    self._pointer = self._map[self._pointer]["up"]
            # If down key is pressed
            elif pygame.K_DOWN in inputs["key"]:
                if inputs["k hold tick"] % p_speed == 0 and inputs["k hold tick"] >= 30 or inputs["k hold tick"] == 1:
                    obj.when_deselect()            # Deselects previous object
                    self._pointer = self._map[self._pointer]["down"]
            # If enter key is pressed
            elif pygame.K_RETURN in inputs["key"]:
                obj.when_select()   # The object's procedure that deals when key pressed down
                # If object has a focus method, it is set to focus
                if type(obj).__name__ in ("Slider","DropMenu"):
                    self._focus = obj
            # If enter key is not pressed
            elif pygame.K_RETURN not in inputs["key"]:
                obj.when_not_select()    # Object's procedure that deals when key is let go

    # Procedure for handling mouse inputs
    def mouse_input(self, inputs):
        # If an object is being focused (Only Drop Menus can be focused here)
        if self._focus != None:
            self._focus.mouse_input(inputs)     # Only the focused object receives inputs
            if type(self._focus).__name__ == "DropMenu":
                if not self._focus.get_dropped():
                    self._focus = None              # Drop Menu is unfocused when undropped
                    inputs["m button"] = ""
        else:
            # Iterates through each object, selecting only GUI objects
            for obj in self._objs:
                if type(obj).__name__ in ("Button","Slider","TickBox","DropMenu"):
                    # Tests if mouse cursor is hovering over the object
                    if obj.rect.collidepoint(inputs["m pos"]):
                        name = obj.get_name()
                        # Searches for the object's name in map
                        for node in list(self._map.keys()):
                            if self._map[node]["obj name"] == name:
                                self._pointer = node  # If found, pointer set to object's position
                    obj.mouse_input(inputs)     # Calls selected object's mouse input method
                    # If the selected Drop Menu is dropped, it is focused
                    if type(obj).__name__ == "DropMenu":
                        if obj.get_dropped():
                            self._focus = obj

    # Procedure that updates the Menu
    def update(self, inputs):
        if inputs["key"] != []:
            self._inp_mode = "keyboard"     # Menu set to keyboard mode if any keys are pressed
        elif inputs["m button"] != "" or inputs["m vel"] != (0,0):
            if self._inp_mode == "keyboard":
                self._focus = None
            self._inp_mode = "mouse"        # Set to mouse mode if mouse is moved or clicked
        if self._inp_mode == "keyboard":
            self.key_input(inputs)          # The key input method is called if in keyboard mode
        elif self._inp_mode == "mouse":
            self.mouse_input(inputs)        # Mouse input method called if in mouse mode
        for obj in self._objs:
            if type(obj).__name__ in ("Button", "Slider", "TickBox", "DropMenu"):
                obj.update()        # Updates each GUI object

    # Procedure that draws all objects in this Menu
    def draw(self):
        # Object being pointed by the keyboard
        pointed_obj = self.find_obj(self._map[self._pointer]["obj name"])
        # Draws the background image
        Frame.blit(self._back, (0, 0))
        for obj in self._objs:
            # The Pointer is drawn to the left of the pointed object
            if obj.get_name() == pointed_obj.get_name() and self._inp_mode == "keyboard":
                pos = (obj.get_pos()[0] - 50, obj.get_pos()[1])
                Frame.blit(self._pointSurf, pos)
            obj.draw()      # Draws all objects by calling their draw method

