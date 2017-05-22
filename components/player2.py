from pygame import *
import components.rahma as rah

font.init()

normal_font = font.Font("fonts/minecraft.ttf", 14)

surrounding_shifts = [(x, y) for x in range(-2, 3) for y in range(-2, 4)]


class Player:

    def __init__(self, x, y, w, h, controls):

        self.rect = Rect(x, y, w, h)
        self.surfSize = (800, 500)

        self.vx = 0
        self.vy = 0

        self.run_speed = int(self.rect.w * 0.3)
        self.jump_height = -(self.rect.h  //  2)
        self.gravity = self.rect.h * 2 / 45

        self.controls = controls
        self.standing = False

    def control(self, fly):
        if key.get_pressed()[self.controls[0]]:
            self.vx = -self.run_speed
        if key.get_pressed()[self.controls[1]]:
            self.vx = self.run_speed

        if fly:
            if key.get_pressed()[self.controls[2]]:
                self.vy = -self.run_speed
            if key.get_pressed()[self.controls[3]]:
                self.vy = self.run_speed

        if key.get_pressed()[self.controls[2]] and self.standing:
            self.vy = self.jump_height

        self.standing = False

    def collide(self, blocks, fly):
        self.rect.y += self.vy

        for block in blocks:
            if self.rect.colliderect(block):
                if self.vy > 0:
                    self.rect.bottom = block.top
                    self.standing = True
                elif self.vy < 0:
                    self.rect.top = block.bottom

                self.vy = 0

        if fly:
            self.vy = 0
        else:
            self.vy += self.gravity if self.vy + self.gravity < self.rect.h else 0

        self.rect.x += self.vx

        for block in blocks:
            if self.rect.colliderect(block):
                if self.vx > 0:
                    self.rect.right = block.left
                elif self.vx < 0:
                    self.rect.left = block.right

        self.vx = 0

        # self.rect.y += int(self.vy)
        # self.rect.x += int(self.vx)
        #
        # bumped = False
        #
        # for block in blocks:
        #     if self.rect.colliderect(block):
        #         if self.vy > 0:
        #             self.rect.bottom = block.top
        #             self.standing = True
        #
        #         elif self.vy < 0:
        #             self.rect.top = block.bottom
        #
        #         self.vy = 0
        #         bumped = True
        #
        # if fly:
        #     self.gravity = 0
        # else:
        #     self.gravity = self.rect.h * 2 / 45
        #
        # for block in blocks:
        #     if self.rect.colliderect(block):
        #         if self.vx > 0:
        #             self.rect.right = block.left
        #
        #         elif self.vx < 0:
        #             self.rect.left = block.right
        #
        # self.vx = 0
        #
        # if fly:
        #     self.vy = 0
        #
        # if self.vy + self.gravity < self.rect.h and not bumped:
        #     self.vy += self.gravity
        # else:
        #     self.vy -= 0

    def update(self, surf, collision_blocks, x_offset, y_offset, fly, paused, reach=5):

        if not paused:
            self.control(fly)

        self.collide(collision_blocks, fly)

        draw.rect(surf, (255, 255, 255), (self.rect.x - x_offset, self.rect.y - y_offset, self.rect.w, self.rect.h))


        center = (self.rect.x - x_offset + self.rect.w // 2, self.rect.y - y_offset + self.rect.h // 2)
        draw.circle(surf, (0, 0, 0), center, reach*20, 3)


class RemotePlayer:
    def __init__(self, username, x, y, player_size):
        self.x = x
        self.y = y

        self.vx = 0
        self.vy = 0

        self.player_size = player_size

        self.username = username
        self.name_tag = normal_font.render(username, True, (255, 255, 255))
        self.name_back = Surface((self.name_tag.get_width() + 10, self.name_tag.get_height + 10), SRCALPHA)
        self.name_back.fill(Color(75, 75, 75, 150))

    def calculate_velocity(self, ncord, fpt):
        self.vy = (ncord[1] - self.y) // fpt
        self.vx = (ncord[0] - self.x) // fpt

        if self.vx == 0 and ncord[0] - self.x != 0:
            self.x = ncord[0]

        if self.vy == 0 and ncord[1] - self.y != 0:
            self.y = ncord[1]

    def update(self, surf, x_offset, y_offset):
        self.y += self.vy
        self.x += self.vx

        draw.rect(surf, (10, 10, 10), (self.x - x_offset, self.y - y_offset, self.player_size, self.player_size))
        surf.blit(self.name_back, rah.center(self.x - 10 - x_offset, self.y - 40 - y_offset, 20, 20,
                                             self.name_back.get_width(), self.name_back.get_height()))
        surf.blit(self.name_tag, rah.center(self.x - 10 - x_offset, self.y - 40 - y_offset, 20, 20,
                                            self.name_tag.get_width(), self.name_tag.get_height()))
