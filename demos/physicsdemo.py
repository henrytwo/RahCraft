from pygame import *
from random import *
import numpy as np

init()

specs = display.Info()
clock = time.Clock()


class Air:
    def __init__(self, x, y, w, h):
        self.rect = Rect(x, y, w, h)
        self.around = False

    def update(self):
        draw.rect(screen, ((255, 255, 255) if self.around else (25, 25, 185)), self.rect)
        self.around = False


class Block:
    def __init__(self, x, y, w, h):
        self.rect = Rect(x, y, w, h)
        self.around = False

    def update(self):
        draw.rect(screen, ((155, 155, 155) if self.around else (50, 255, 150)), self.rect)
        self.around = False


class Player:
    def __init__(self, x, y, w, h, controls):
        self.rect = Rect(x, y, w, h)

        self.vx = 0
        self.vy = 0

        self.controls = controls

        self.standing = False

        self.surrounding_blocks = []

    def control(self):

        if key.get_pressed()[self.controls[0]]:
            self.vx = -8
        if key.get_pressed()[self.controls[1]]:
            self.vx = 8
        if key.get_pressed()[self.controls[2]] and self.standing:
            self.vy = -23

        self.standing = False

    def detect(self):
        self.surrounding_blocks = []

        for shift in surrounding_shifts:
            try:
                self.surrounding_blocks.append(gameWorld[self.rect.centery // b_height + shift[1],
                                                         self.rect.centerx // b_width + shift[0]])
            except IndexError:
                pass

        for block in self.surrounding_blocks:
            block.around = True

        self.collide(self.surrounding_blocks)

    def collide(self, blocks):

        self.rect.y += self.vy

        for block in blocks:
            if type(block) is Block and self.rect.colliderect(block.rect):
                if self.vy > 0:
                    self.rect.bottom = block.rect.top

                    self.standing = True
                if self.vy < 0:
                    self.rect.top = block.rect.bottom

                self.vy = 0

        self.rect.centerx = (self.rect.centerx + self.vx) % screenSize[0]

        for block in blocks:
            if type(block) is Block and self.rect.colliderect(block.rect):
                if self.vx > 0:
                    self.rect.right = block.rect.left
                if self.vx < 0:
                    self.rect.left = block.rect.right

        self.vx = 0
        self.vy += 2 if self.vy + 1 < b_height else 0

    def update(self):
        draw.rect(screen, (255, 0, 0), self.rect)


def make_world(columns, rows):
    world_list = []

    for y in range(rows):
        row_list = []
        for x in range(columns):
            if randrange(rows - len(world_list)):
                row_list.append(Air(b_width * x, b_height * y, b_width, b_height))
            else:
                row_list.append(Block(b_width * x, b_height * y, b_width, b_height))

        world_list.append(row_list)

    world_array = np.array(world_list)

    return world_array


display.set_caption("New Physics Idea!")

screenSize = 960, 540
screen = display.set_mode(screenSize)

# You can change these (use multiples of 16 and 9 respectively)
columns = 32
rows = 18

b_width = screenSize[0] // columns
b_height = screenSize[1] // rows

gameWorld = make_world(columns, rows)

player = Player(b_width, b_height, b_width, b_height, [K_a, K_d, K_w, K_s])

surrounding_shifts = [(-1, -1), (0, -1), (1, -1),
                      (-1, 0), (0, 0), (1, 0),
                      (-1, 1), (0, 1), (1, 1)]

while True:
    for e in event.get():
        if e.type == QUIT:
            break

    else:

        for c in range(columns):
            for r in range(rows):
                gameWorld[r, c].update()

        player.control()
        player.detect()
        player.update()

        clock.tick(60)

        display.set_caption("New Physics Idea! // FPS - {0:.0f}".format(clock.get_fps()))

        display.update()
        continue

    break

display.quit()
exit()
