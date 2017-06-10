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


class Entity:
    def __init__(self, x, y, w, h, cap):
        self.rect = Rect(x, y, w, h)

        self.actual_x = x
        self.actual_y = y

        self.vx = 0
        self.vy = 0

        self.vx_inc = 0.15
        self.vy_inc = 0.5

        self.base_vy = -(cap // 10 + 2.25)

        self.max_vx = cap // 10
        self.max_vy = cap

        self.friction = 0.95

        self.standing = False

        self.surrounding_blocks = []

        self.command = 0
        self.analog_move = False
        self.analog_limit = 0
        self.analog_frame = 0

    def sim_input(self):
        if not self.analog_move:
            self.command = randrange(10)
            if self.command in [1, 2, 4, 5]:
                self.analog_move = True
                self.analog_limit = randint(60, 180)
                self.analog_frame = 0
        else:
            self.analog_frame += 1
            if self.analog_frame == self.analog_limit:
                self.analog_move = False
                self.command = 0

    def control(self):
        # if key.get_pressed()[self.controls[0]] and self.vx > self.max_vx:
        #     self.vx -= self.vx_inc
        # elif self.vx < 0:
        #     self.vx += self.vx_inc
        if self.command in [1, 4] and (self.vx < self.max_vx or self.vx < 0):
            self.vx += self.vx_inc
        elif self.command in [2, 5] and (abs(self.vx) < self.max_vx or self.vx > 0):
            self.vx -= self.vx_inc
        else:
            self.vx *= self.friction

        if self.command in [3, 4, 5] and self.standing:
            self.vy = self.base_vy
            self.standing = False

        if self.command == 4:
            self.command = 1
        elif self.command == 5:
            self.command = 2

    def detect(self):
        self.surrounding_blocks = []

        for shift in surrounding_shifts:
            try:
                self.surrounding_blocks.append(gameWorld[self.rect.centery // self.rect.h + shift[1],
                                                         self.rect.centerx // self.rect.w + shift[0]])
            except IndexError:
                self.surrounding_blocks.append(None)

        for block in self.surrounding_blocks:
            block.around = True

        self.collide(self.surrounding_blocks)

    def collide(self, blocks):
        self.actual_y += self.vy
        self.rect.y = self.actual_y

        for block in blocks:
            if type(block) is Block and self.rect.colliderect(block.rect):
                if self.vy > 0:
                    self.rect.bottom = block.rect.top
                    self.standing = True
                elif self.vy < 0:
                    self.rect.top = block.rect.bottom

                self.actual_y = self.rect.y
                self.vy = 0

        if type(blocks[7]) is Air:
            if self.command == 1:
                self.command = 4
            elif self.command == 2:
                self.command = 5

        if 0 > round(self.vx) > -1:
            self.actual_x += self.vx - 1
        else:
            self.actual_x += self.vx
        self.rect.x = self.actual_x

        for block in blocks:
            if type(block) is Block and self.rect.colliderect(block.rect):
                if self.vx > 0:
                    self.rect.right = block.rect.left
                    if type(blocks[2]) is not Block:
                        self.command = 4
                    else:
                        self.command = choice([0, 2])
                elif self.vx < 0:
                    self.rect.left = block.rect.right
                    if type(blocks[0]) is not Block:
                        self.command = 5
                    else:
                        self.command = choice([0, 1])

                self.actual_x = self.rect.x
                self.vx = 0

        # self.vx = self.max_vx if 0
        self.vy += self.vy_inc if self.vy + self.vy_inc < self.max_vy else 0

    def update(self):
        draw.rect(screen, (255, 0, 0), self.rect)


def make_world(row_num, col_num, world_type):
    world_list = []

    for y in range(row_num):
        row_list = []

        for x in range(col_num):
            if x in [0, col_num - 1] or (y in range(row_num)[-world_type:] and randrange(rows - len(world_list)) == 0):
                row_list.append(Block(b_width * x, b_height * y, b_width, b_height))
            else:
                row_list.append(Air(b_width * x, b_height * y, b_width, b_height))

        world_list.append(row_list)

    world_array = np.array(world_list)

    return world_array


display.set_caption("New Physics Idea!")

screenSize = 960, 540
screen = display.set_mode(screenSize)

complexity = 10 # abs(int(input('Complexity level of world? (Use a positive integer)\n')))
rows = 9 * complexity
columns = 16 * complexity

b_width = screenSize[0] // columns
b_height = screenSize[1] // rows

gameWorld = make_world(rows, columns, 2)

entityList = [Entity((b_width + b_width * (i * 2)) % screenSize[0], (b_height + b_height * (i * 2)) % screenSize[1],
              b_width, b_height, b_height)
              for i in range(4)]

surrounding_shifts = [(-1, -1), (0, -1), (1, -1),
                      (-1, 0), (0, 0), (1, 0),
                      (-1, 1), (0, 1), (1, 1)]

while True:
    for e in event.get():
        if e.type == QUIT:
            break

    else:
        keys = key.get_pressed()
        mouse_pos = mouse.get_pos()

        for r in range(rows):
            for c in range(columns):
                gameWorld[r, c].update()

        for entity in entityList:
            entity.sim_input()
            entity.control()
            entity.detect()
            entity.update()

        clock.tick(60)

        display.set_caption("New Physics Idea! // FPS - {0:.0f}".format(clock.get_fps()))

        display.update()

        continue

    break

display.quit()
exit()
