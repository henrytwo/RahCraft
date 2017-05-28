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
    def __init__(self, x, y, w, h, cap, controls):
        self.rect = Rect(x, y, w, h)

        self.actual_x = x
        self.actual_y = y

        self.vx = 0
        self.vy = 0

        self.vx_inc = 0.15
        self.vy_inc = 0.5

        self.base_vy = -(cap // 10 + 3)

        self.max_vx = cap // 10
        self.max_vy = cap

        self.friction = 0.95

        self.controls = controls
        self.standing = False

        self.moving_left = False
        self.moving_right = False

        self.surrounding_blocks = []

    def control(self):
        # old
        # if key.get_pressed()[self.controls[0]] and self.vx > self.max_vx:
        #     self.vx -= self.vx_inc
        # elif self.vx < 0:
        #     self.vx += self.vx_inc

        # if key.get_pressed()[self.controls[1]] and (self.vx < self.max_vx or self.vx < 0):
        #     self.vx += self.vx_inc
        # elif key.get_pressed()[self.controls[0]] and (abs(self.vx) < self.max_vx or self.vx > 0):
        #     self.vx -= self.vx_inc
        # else:
        #     self.vx *= self.friction
        #
        # if key.get_pressed()[self.controls[2]] and self.standing:
        #     self.vy = self.base_vy

        for e in event.get(playerEventList):
            if e.type == KEYDOWN:
                if e.key == self.controls[0] and not self.moving_right:
                    self.moving_left = True
                    print('start left')
                elif e.key == self.controls[1] and not self.moving_left:
                    self.moving_right = True
                    print('start right')
                elif e.key in [self.controls[2], self.controls[4]]:
                    print('attempting jump')
                    if self.standing:
                        self.vy += self.base_vy
                        print('jump')

            elif e.type == KEYUP:
                if e.key == self.controls[0]:
                    self.moving_left = False
                    print('stop left')
                elif e.key == self.controls[1]:
                    self.moving_right = False
                    print('stop right')

        if self.moving_left and (abs(self.vx) < self.max_vx or self.vx > 0):
            self.vx -= self.vx_inc
        elif self.moving_right and (self.vx < self.max_vx or self.vx < 0):
            self.vx += self.vx_inc
        else:
            self.vx *= self.friction

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

        if 0 > round(self.vx) > -1:
            self.actual_x += self.vx - 1
        else:
            self.actual_x += self.vx
        self.rect.x = self.actual_x

        for block in blocks:
            if type(block) is Block and self.rect.colliderect(block.rect):
                if self.vx > 0:
                    self.rect.right = block.rect.left
                elif self.vx < 0:
                    self.rect.left = block.rect.right

                self.actual_x = self.rect.x
                self.vx = 0

        # self.vx = self.max_vx if 0
        self.vy += self.vy_inc if self.vy + self.vy_inc < self.max_vy else 0

    def respawn(self, pos):
        self.actual_x, self.actual_y = pos

    def update(self):
        draw.rect(screen, (255, 0, 0), self.rect)


def make_world(row_num, col_num, levels):
    world_list = []

    for y in range(row_num):
        row_list = []

        for x in range(col_num):
            if y not in range(row_num)[-levels:] or randrange(rows - len(world_list)):
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

gameWorld = make_world(rows, columns, 1)

player = Player(b_width, b_height, b_width, b_height, b_height, [K_a, K_d, K_w, K_s, K_SPACE])

surrounding_shifts = [(-1, -1), (0, -1), (1, -1),
                      (-1, 0), (0, 0), (1, 0),
                      (-1, 1), (0, 1), (1, 1)]

screenEventList = [QUIT]
playerEventList = [KEYDOWN, KEYUP]
uselessEventList = [MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN,
                    JOYAXISMOTION, JOYBALLMOTION, JOYHATMOTION, JOYBUTTONUP, JOYBUTTONDOWN,
                    VIDEORESIZE, VIDEOEXPOSE]

event.set_blocked(uselessEventList)

while True:
    # event.clear(uselessEventList)
    for e in event.get(screenEventList):
        if e.type == QUIT:
            break

    else:
        keys = key.get_pressed()
        mouse_pos = mouse.get_pos()

        for r in range(rows):
            for c in range(columns):
                gameWorld[r, c].update()

        player.control()
        player.detect()
        player.update()

        if keys[K_e]:
            player.respawn(mouse_pos)

        clock.tick(60)

        display.set_caption("New Physics Idea! // FPS - {0:.0f}".format(clock.get_fps()))

        display.update()

        continue

    break

display.quit()
exit()
