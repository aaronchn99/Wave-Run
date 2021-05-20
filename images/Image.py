import pygame
from var.variables import *


# Crops an image with the specified position of the top left corner and the area
def crop(Image, pos, area):
    crop_area = pygame.Surface(area, pygame.SRCALPHA)
    crop_area.blit(Image, (-pos[0], -pos[1]))
    return crop_area

# Base class for all sprite textures
class Texture:
    def __init__(self):
        self._alpha = 255
    
    # Getter and setter for transparency level
    def get_alpha(self):
        return self._alpha

    def set_alpha(self, alpha):
        self._alpha = alpha
    
    def scale(self, width, height):
        self._rect = pygame.Rect(0, 0, width, height)
    
    # All subclasses must be able to return a single surface
    @property
    def surface(self):
        return None

    # Bounding rectangle
    @property
    def rect(self):
        return None

class ImageTexture(Texture):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.image = image.convert_alpha()
        self._rect = self.image.get_rect()

    def scale(self, width, height):
        super().scale(width, height)
        self.image = pygame.transform.scale(self.image, (width, height))

    @property
    def surface(self):
        image_copy = self.image.copy()
        image_copy.set_alpha(self.get_alpha())
        return image_copy

    @property
    def rect(self):
        return self._rect

class ColorTexture(ImageTexture):
    # Texture filled with a single color, bound to certain dimensions
    def __init__(self, color):
        image = pygame.Surface((10, 10), flags=pygame.SRCALPHA)
        image.fill(color)
        super().__init__(image)

class AnimatedTexture(Texture):
    # Animated images, consisting of a list of frames cropped from a frame sheet
    # Params:
    # image_path - Filepath of the frame sheet
    # frame_count - # of frames
    # frame_dim - Width and Height of animation frames
    # fps - Frames Per Second
    def __init__(self, Sheet, frame_count, frame_dim, fps):
        super().__init__()
        self._framesheet = Sheet
        self._frames = list()
        for i in range(frame_count):
            self._frames.append(crop(Sheet, (frame_dim[0]*i, 0), frame_dim))
        self._rect = pygame.Rect((0, 0), frame_dim)
        self._fps = fps
        self._animation_ended = False
        self._paused = False
        self._progress = 0
    
    # If animation has reached its last frame
    @property
    def ended(self):
        return self._animation_ended
    
    @property
    def frames(self):
        return self._frames

    @property
    def surface(self):
        if self._paused:
            frame = self._frames[int(self._progress)]
        else:
            frame = self.next_frame()
        frame.set_alpha(self.get_alpha())
        return frame

    @property
    def rect(self):
        return self._rect
    
    def pause(self):
        self._paused = True
    
    def play(self):
        self._paused = False

    def goto_frame(self, i):
        self._progress = i

    def set_fps(self, fps):
        self._fps = fps
    
    def reset(self):
        self._progress = 0
    
    def copy(self):
        frame_count = len(self.frames)
        frame_dim = self.rect.size
        return type(self)(self._framesheet, frame_count, frame_dim, self._fps)
    
    def scale(self, width, height):
        super().scale(width, height)
        self._frames = list(map(
            lambda f: pygame.transform.scale(f, (width, height)),
            self._frames))

    # Returns next frame depending on time passed and fps
    def next_frame(self):
        time_delta = Clock.get_time()
        self._progress += self._fps * time_delta/1000
        if self._progress >= len(self._frames):
            self._animation_ended = True
            self._progress %= len(self._frames)
        elif self._animation_ended:
            self._animation_ended = False
        return self._frames[int(self._progress)]