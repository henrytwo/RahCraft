from pygame import *
from random import *
import numpy as np
init()

clock = time.Clock()


class Player:
    def __init__(self, x, y, w, h, controls, colour):
        self.rect = Rect(x, y, w, h)

        self.vx = 0
        self.vy = 0

        self.run_speed = int(self.rect.w * 0.3)
        self.jump_height = -(self.rect.h // 2)
        self.gravity = self.rect.h * 2 / 45

        print(self.run_speed, self.jump_height, self.gravity)

        self.controls = controls

        self.standing = False

        self.plr_relation = {'left': 0, 'right': 0, 'top': 0}
        self.plr_surround = {'left': [], 'right': [], 'top': []}

        self.surrounding_block_data = []

        self.colour = colour

    def control(self):
        if key.get_pressed()[self.controls[0]]:
            if self.plr_relation['left']:
                self.vx = -(self.run_speed // 2)
                for player in self.plr_surround['left']:
                    player.vx = -(self.run_speed // 2)
            else:
                self.vx = -self.run_speed
        if key.get_pressed()[self.controls[1]]:
            if self.plr_relation['right']:
                self.vx = self.run_speed // 2
                for player in self.plr_surround['right']:
                    player.vx = self.run_speed // 2
            else:
                self.vx = self.run_speed
        if key.get_pressed()[self.controls[2]] and self.standing:
            if self.plr_relation['top']:
                self.vy = self.jump_height // 4
                for player in self.plr_surround['top']:
                    player.vy = self.jump_height // 4
            else:
                self.vy = self.jump_height

        self.standing = False
        self.plr_relation = {'left': 0, 'right': 0, 'top': 0}
        self.plr_surround = {'left': [], 'right': [], 'top': []}

    def detect(self):
        self.surrounding_block_data = []

        for shift in surrounding_shifts:
            try:
                self.surrounding_block_data.append(gameWorld[self.rect.centery // self.rect.h + shift[1],
                                                             self.rect.centerx // self.rect.w + shift[0]])
            except IndexError:
                pass

        self.collide(self.surrounding_block_data)

    def collide(self, block_data):
        self.rect.y += int(self.vy)

        for block, block_type in block_data:
            if block_type and self.rect.colliderect(block):
                if self.vy > 0:
                    self.rect.bottom = block.top
                    self.standing = True
                elif self.vy < 0:
                    self.rect.top = block.bottom

                self.vy = 0

        for player in playerList:
            if self is not player and self.rect.colliderect(player.rect):
                if self.vy > 0:
                    self.rect.bottom = player.rect.top
                    self.standing = True
                elif self.vy < 0:
                    self.plr_relation['top'] = 1
                    self.plr_surround['top'].append(player)

        self.rect.centerx = (self.rect.centerx + self.vx) % screenSize[0]

        for block, block_type in block_data:

            if block_type and self.rect.colliderect(block):
                if self.vx > 0:
                    self.rect.right = block.left
                elif self.vx < 0:
                    self.rect.left = block.right

        for player in playerList:
            if self is not player and self.rect.colliderect(player.rect):
                if self.vx > 0:
                    self.rect.right = player.rect.left
                    self.plr_relation['right'] = 1
                    self.plr_surround['right'].append(player)
                elif self.vx < 0:
                    self.rect.left = player.rect.right
                    self.plr_relation['left'] = 1
                    self.plr_surround['left'].append(player)

        self.vy += self.gravity if self.vy + self.gravity < self.rect.h else 0

    def update(self):
        draw.rect(screen, self.colour, self.rect)


def make_world(row_num, col_num):
    world_list = []

    for y in range(row_num):
        row_list = []

        for x in range(col_num):

            if randrange(rows - len(world_list)):
                row_list.append((Rect(b_width * x, b_height * y, b_width, b_height), 0))
            else:
                row_list.append((Rect(b_width * x, b_height * y, b_width, b_height), 1))

        world_list.append(row_list)

    world_array = np.array(world_list)

    return world_array


display.set_caption("New Physics Idea!")

screenSize = 960, 540
screen = display.set_mode(screenSize)

complexity = abs(int(input('Complexity level of world? (Use a positive integer)\n')))
rows = 9 * complexity
columns = 16 * complexity

playerNum = abs(int(input("Number of players? (max 4)\n")))
playerNum = 4 if playerNum > 4 else (1 if not playerNum else playerNum)

b_width = screenSize[0] // columns
b_height = screenSize[1] // rows

gameWorld = make_world(rows, columns)

playerList = [Player(b_width, b_height, b_width, b_height, [K_a, K_d, K_w, K_s], (225, 25, 50)),
              Player(b_width * 2, b_height * 2, b_width, b_height, [K_LEFT, K_RIGHT, K_UP, K_DOWN], (255, 95, 0)),
              Player(b_width * 3, b_height * 3, b_width, b_height, [K_v, K_n, K_g, K_b], (191, 220, 0)),
              Player(b_width * 4, b_height * 4, b_width, b_height, [K_j, K_l, K_i, K_k], (0, 63, 191))][:playerNum]

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

                draw.rect(screen, ((50, 255, 150) if gameWorld[r, c][1] else (150, 15, 135)), gameWorld[r, c][0])

        for player in playerList:
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
