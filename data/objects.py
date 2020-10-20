import pygame
import data.engine as e
import math

bullet_vel = 10

class Bullet:
    def __init__(self, start, dir):
        self.rot = dir
        self.start = start
        self.img = pygame.image.load("data/Graphics/bullet.png").convert_alpha()
        self.pos = self.start

    def display(self, display):
        e.blit_center(display, pygame.transform.rotate(self.img, self.rot), [self.pos[0], self.pos[1] + 3], 1)

    def move(self):
        self.pos[1] -= math.cos(math.radians(self.rot)) * bullet_vel
        self.pos[0] -= math.sin(math.radians(self.rot)) * bullet_vel

    def destroy(self, WIN_SIZE):
        if (self.pos[0] <= 0 or self.pos[0] >= WIN_SIZE[0]) and (self.pos[1] <= 0 or self.pos[1] >= WIN_SIZE[1]):
            return True
        else:
            return False