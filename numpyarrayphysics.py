from pygame import *
from random import *
import numpy as np

init()
specs = display.Info()

clock = time.Clock()


class Air:
    def __init__(self, rect):
        self.rect = Rect(*rect)
        self.around = False

    def update(self):
        draw.rect(screen, ((255, 255, 255) if self.around else (25, 25, 185)), self.rect)
        self.around = False


class Block:
    def __init__(self, rect):
        self.rect = Rect(*rect)
        self.around = False

    def update(self):
        draw.rect(screen, ((155, 155, 155) if self.around else (50, 255, 150)), self.rect)
        self.around = False


class Player:
    def __init__(self, rect, controls):
        self.rect = Rect(*rect)

        self.vx = 0
        self.vy = 0

        self.controls = controls

        self.standing = False

    def control(self):

        if key.get_pressed()[self.controls[0]]:
            self.vx = -8
        if key.get_pressed()[self.controls[1]]:
            self.vx = 8
        if key.get_pressed()[self.controls[2]] and self.standing:
            self.vy = -23
        # if key.get_pressed()[self.controls[3]]:
        #     self.vy = 5

        self.standing = False

    def detect(self, blocks):

        self.rect.x = (self.rect.x + self.vx) % screenSize[0]

        for block in blocks:
            if type(block) is Block and self.rect.colliderect(block.rect):
                if self.vx > 0:
                    self.rect.right = block.rect.left
                if self.vx < 0:
                    self.rect.left = block.rect.right

        self.rect.y = (self.rect.y + self.vy) % screenSize[1]

        for block in blocks:
            if type(block) is Block and self.rect.colliderect(block.rect):
                if self.vy > 0:
                    self.rect.bottom = block.rect.top
                    self.vy = 0
                    self.standing = True
                if self.vy < 0:
                    self.rect.top = block.rect.bottom
                    self.vy = 1

        self.vx = 0

        self.vy += 2 if self.vy + 1 < b_height else 0

    def update(self):
        draw.rect(screen, (255, 0, 0), self.rect)


def make_world(columns, rows):

    wrld_list = [[(Air((b_width * x, b_height * y, b_width, b_height)) if randrange(8) else
                   Block((b_width * x, b_height * y, b_width, b_height))) for x in range(columns)] for y in range(rows)]

    wrld_array = np.array(wrld_list)

    return wrld_array


display.set_caption("New Physics Idea!")

screenSize = 960, 540
screen = display.set_mode(screenSize)

# You can change these (use multiples of 16 and 9 respectively)
columns = 32
rows = 18

b_width = screenSize[0] // columns
b_height = screenSize[1] // rows

gameWorld = make_world(columns, rows)

player = Player((b_width, b_height, b_width, b_height), [K_a, K_d, K_w, K_s])

surrounding_shifts = [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

while True:
    for e in event.get():
        if e.type == QUIT:
            break

    else:

        surrounding_blocks = []

        for shift in surrounding_shifts:
            try:
                surrounding_blocks.append(gameWorld[player.rect.y // b_height + shift[1],
                                                    player.rect.x // b_width + shift[0]])
            except IndexError: pass

        for block in surrounding_blocks:
            block.around = True

        for c in range(columns):
            for r in range(rows):
                gameWorld[r, c].update()

        player.control()
        player.detect(surrounding_blocks)
        player.update()

        clock.tick(60)

        display.set_caption("New Physics Idea! // FPS - {0:.0f}".format(clock.get_fps()))

        display.update()
        continue

    break

display.quit()
exit()
