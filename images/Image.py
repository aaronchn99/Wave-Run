import pygame


# Crops an image with the specified position of the top left corner and the area
def crop(Image, pos, area):
    crop_area = pygame.Surface(area, pygame.SRCALPHA)
    crop_area.blit(Image, (-pos[0], -pos[1]))
    return crop_area


class Animation:
    # Animated images, consisting of a list of frames cropped from a frame sheet
    # Params:
    # image_path - Filepath of the frame sheet
    # frame_count - # of frames
    # frame_dim - Width and Height of animation frames
    # fps - Frames Per Second
    def __init__(self, image_path, frame_count, frame_dim, fps):
        Image = pygame.image.load(image_path)
        self._frames = list()
        for i in range(frame_count):
            self._frames.append(crop(Image, (frame_dim[0]*i, 0), frame_dim))
        self.w, self.h = frame_dim
        self._fps = fps
        self._animation_ended = False
        self._progress = 0
    
    @property
    def frames(self):
        return self._frames

    # Returns next frame depending on time passed and fps
    # Params:
    # time_delta - Time passed since last tick (milliseconds)
    def next_frame(self, time_delta):
        self._progress += self._fps * time_delta/1000
        if self._progress >= len(self._frames):
            self._animation_ended = True
            self._progress %= len(self._frames)
        elif self._animation_ended:
            self._animation_ended = False
        return self._frames[int(self._progress)]

    # If animation has reached its last frame
    @property
    def ended(self):
        return self._animation_ended
    
    # Set animation index (animation_i) back to start
    def reset(self):
        self._progress = 0