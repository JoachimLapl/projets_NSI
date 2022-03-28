import pygame

resolution = (400,400)
mid_screen = tuple(i/2 for i in resolution)

mi,ma = sorted(resolution)

screen = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()