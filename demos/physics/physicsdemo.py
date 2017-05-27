from pygame import *
from random import *
import numpy as np

init()

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

        self.run_speed = int(self.rect.w * 0.3)
        self.jump_height = -(3 * self.rect.h // 4)
        self.gravity = 0.5

        self.controls = controls

        self.standing = False

        self.surrounding_blocks = []

    def control(self):
        if key.get_pressed()[self.controls[0]]:
            self.vx = -self.run_speed
        if key.get_pressed()[self.controls[1]]:
            self.vx = self.run_speed
        if key.get_pressed()[self.controls[2]] and self.standing:
            self.vy = self.jump_height

        self.standing = False

    def detect(self):
        self.surrounding_blocks = []

        for shift in surrounding_shifts:
            try:
                self.surrounding_blocks.append(gameWorld[self.rect.centery // self.rect.h + shift[1],
                                                         self.rect.centerx // self.rect.w + shift[0]])
            except IndexError:
                pass

        for block in self.surrounding_blocks:
            block.around = True

        self.collide(self.surrounding_blocks)

    def collide(self, blocks):
        self.rect.y += int(self.vy)

        for block in blocks:
            if type(block) is Block and self.rect.colliderect(block.rect):
                if self.vy > 0:
                    self.rect.bottom = block.rect.top
                    self.standing = True
                elif self.vy < 0:
                    self.rect.top = block.rect.bottom

                self.vy = 0

        self.rect.centerx = (self.rect.centerx + self.vx) % screenSize[0]

        for block in blocks:
            if type(block) is Block and self.rect.colliderect(block.rect):
                if self.vx > 0:
                    self.rect.right = block.rect.left
                elif self.vx < 0:
                    self.rect.left = block.rect.right

        self.vx = 0
        if self.vy / self.gravity < self.rect.h:
            if self.vy < 0:
                self.vy *= self.gravity
                self.vy = round(self.vy)
            else:
                if int(self.vy) == 0:
                    self.vy = 1
                    print("run")

                self.vy = self.vy / self.gravity

    def update(self):
        draw.rect(screen, (255, 0, 0), self.rect)


def make_world(row_num, col_num):
    world_list = []

    for y in range(row_num):
        row_list = []

        for x in range(col_num):
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

complexity = abs(int(input('Complexity level of world? (Use a positive integer)\n')))
rows = 9 * complexity
columns = 16 * complexity

b_width = screenSize[0] // columns
b_height = screenSize[1] // rows

gameWorld = make_world(rows, columns)

player = Player(b_width, b_height, b_width, b_height, [K_a, K_d, K_w, K_s])

surrounding_shifts = [(-1, -1), (0, -1), (1, -1),
                      (-1, 0), (0, 0), (1, 0),
                      (-1, 1), (0, 1), (1, 1)]

while True:

    for e in event.get():
        if e.type == QUIT:
            break

    else:
        for r in range(rows):
            for c in range(columns):
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
