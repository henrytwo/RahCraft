from pygame import *
from random import *
from math import *
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


class EntityPassive:
    def __init__(self, x, y, w, h, cap, activity, main_list):
        self.x = x
        self.y = y

        self.top = y
        self.bottom = y + h

        self.left = x
        self.right = y + w

        self.w = w
        self.h = h

        self.vx = 0
        self.vy = 0

        self.vx_inc = 0.15
        self.vy_inc = 0.5

        self.base_vy = -(cap // 10 + 2.25)

        self.max_vx = cap // 10
        self.max_vy = cap

        self.friction = 0.95

        self.standing = False

        self.surrounding_shifts = [(-1, -1), (0, -1), (1, -1),
                              (-1, 0), (0, 0), (1, 0),
                              (-1, 1), (0, 1), (1, 1)]

        self.surrounding_top = []
        self.surrounding_bottom = []
        self.surrounding_left = []
        self.surrounding_right = []



        self.command = 0
        self.analog_move = False
        self.analog_limit = 0
        self.analog_frame = 0

        self.activity = activity

        main_list.append(self)
        entityList.append(self)

    def sim_input(self):
        if not self.analog_move:
            self.command = randrange(self.activity)
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
        self.surrounding_top = []
        self.surrounding_bottom = []
        self.surrounding_left = []
        self.surrounding_right = []

        for shift in range(2):
            try: # top
                if not gameWorld[self.rect.centery // self.rect.h + self.surrounding_shifts[0][shift][1], self.rect.centerx // self.rect.w + self.surrounding_shifts[0][shift][0]] != Air:
                    self.surrounding_top.append([self.rect.centery // self.rect.h + self.surrounding_shifts[0][shift][1], self.rect.centerx // self.rect.w + self.surrounding_shifts[0][shift][0]])
            except IndexError:
                pass

            try: # bottom
                if not gameWorld[self.rect.centery // self.rect.h + self.surrounding_shifts[2][shift][1], self.rect.centerx // self.rect.w + self.surrounding_shifts[2][shift][0]] is Air:
                    self.surrounding_bottom.append([self.rect.centery // self.rect.h + self.surrounding_shifts[2][shift][1], self.rect.centerx // self.rect.w + self.surrounding_shifts[2][shift][0]])
            except IndexError:
                pass

            try: # left
                if not gameWorld[self.rect.centery // self.rect.h + self.surrounding_shifts[shift][0][1], self.rect.centerx // self.rect.w + self.surrounding_shifts[shift][0][0]] is Air:
                    self.surrounding_top.append([self.rect.centery // self.rect.h + self.surrounding_shifts[shift][0][1], self.rect.centerx // self.rect.w + self.surrounding_shifts[shift][0][0]])
            except IndexError:
                pass

            try: # right
                if not gameWorld[self.rect.centery // self.rect.h + self.surrounding_shifts[shift][0][1], self.rect.centerx // self.rect.w + self.surrounding_shifts[shift][0][0]] != Air:
                    self.surrounding_top.append([self.rect.centery // self.rect.h + self.surrounding_shifts[shift][0][1], self.rect.centerx // self.rect.w + self.surrounding_shifts[shift][0][0]])
            except IndexError:
                pass

        self.collide(self.surrounding_top, self.surrounding_bottom, self.surrounding_top, self.surrounding_left, self.surrounding_right)

    def collide(self, blocks_top, block_bottom, block_left, block_right):
        self.y += self.vy
        self.top = self.y
        self.bottom = self.y + self.h

        for block in blocks_top:
            if self.vy > 0 and self.bottom <= block[0]:
                self.y = block[0]
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

        self.vy += self.vy_inc if self.vy + self.vy_inc < self.max_vy else 0

    def update(self):
        draw.rect(screen, (125, 0, 125), self.rect)


class EntityAggressive:
    def __init__(self, x, y, w, h, cap, activity, target, sight, main_list, block_size):
        self.rect = Rect(x, y, w, h)

        self.actual_x = x
        self.actual_y = y

        self.vx = 0
        self.vy = 0

        self.vx_inc = 0.15 / block_size
        self.vy_inc = 0.5 / block_size

        self.base_vy = -(cap // 10 + 2.25) / block_size

        self.max_vx = cap // 15 / block_size
        self.max_vy = cap / block_size

        self.friction = 0.95

        self.standing = False

        self.surrounding_blocks = []

        self.command = 0
        self.analog_move = False
        self.analog_limit = 0
        self.analog_frame = 0

        self.activity = activity

        self.targeting = False
        self.target = target

        self.sight = sight

        main_list.append(self)
        entityList.append(self)

    def sim_input(self):
        if self.target.__class__ is EntityPassive:
            target_loc = self.target.rect.center
        else:
            target_loc = self.target

        if abs(hypot(*np.subtract(self.rect.center, target_loc))) > self.sight:
            self.targeting = True
            print("hi")
            if not self.analog_move:
                self.command = randrange(self.activity)
                if self.command in [1, 2, 4, 5]:
                    self.analog_move = True
                    self.analog_limit = randint(60, 180)
                    self.analog_frame = 0
            else:
                self.analog_frame += 1
                if self.analog_frame == self.analog_limit:
                    self.analog_move = False
                    self.command = 0
        else:
            self.targeting = False
            print('die')
            if self.rect.x < target_loc[0] and self.command not in [1, 4]:
                self.command = 1
            elif self.rect.x > target_loc[0] and self.command not in [2, 5]:
                self.command = 2
            elif self.rect.y > target_loc[1]:
                self.command = 3

    def control(self):
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
                self.surrounding_blocks.append([self.rect.centery // self.rect.h + shift[1], self.rect.centerx // self.rect.w + shift[0]])
            except IndexError:
                self.surrounding_blocks.append(None)

        for block in self.surrounding_blocks:
            if block is not None:
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

complexity = 2  # abs(int(input('Complexity level of world? (Use a positive integer)\n')))
rows = 9 * complexity
columns = 16 * complexity

b_width = screenSize[0] // columns
b_height = screenSize[1] // rows

gameWorld = make_world(rows, columns, 2)

passiveList = []
aggroList = []

entityList = []

for i in range(1):
    EntityPassive((b_width + b_width * (i * 2)) % screenSize[0], (b_height + b_height * (i * 2)) % screenSize[1],
                  b_width, b_height, b_height, 500, passiveList)


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
