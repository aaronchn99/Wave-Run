import pygame


# Crops an image with the specified position of the top left corner and the area
def crop(Image, pos, area):
    crop_area = pygame.Surface(area, pygame.SRCALPHA)
    crop_area.blit(Image, (-pos[0], -pos[1]))
    return crop_area