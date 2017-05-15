from pygame import *


class Player:

    def __init__(self, x, y, w, h, controls):

        self.rect = Rect(x, y, w, h)
        self.screenSize = (800, 500)
        self.vx = 0
        self.vy = 0

        self.run_speed = int(self.rect.w * 0.3)
        self.jump_height = -(self.rect.h // 2)
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
        self.rect.y += int(self.vy)
        self.rect.x += int(self.vx)

        bumped = False

        for block in blocks:
            if self.rect.colliderect(block):
                if self.vy > 0:
                    self.rect.bottom = block.top
                    self.standing = True

                elif self.vy < 0:
                    self.rect.top = block.bottom

                self.vy = 0
                bumped = True

        if fly:
            self.gravity = 0
        else:
            self.gravity = self.rect.h * 2 / 45

        for block in blocks:
            if self.rect.colliderect(block):
                if self.vx > 0:
                    self.rect.right = block.left

                elif self.vx < 0:
                    self.rect.left = block.right

        self.vx = 0

        if fly:
            self.vy = 0

        if self.vy + self.gravity < self.rect.h and not bumped:
            self.vy += self.gravity
        else:
            self.vy -= 0

    def update(self, screen, collision_blocks, x_offset, y_offset, fly):
        self.control(fly)
        self.collide(collision_blocks, fly)
        draw.rect(screen, (255, 0, 0), (self.rect.x - x_offset, self.rect.y - y_offset, self.rect.w, self.rect.h))


class RemotePlayer:
    def __init__(self, x, y, player_size):
        self.x = x
        self.y = y

        self.vx = 0
        self.vy = 0

        self.player_size = player_size
        print(self.x, self.y)

    def calculate_velocity(self, ncord, fpt):
        self.vy = (ncord[1] - self.y)//fpt
        self.vx = (ncord[0] - self.x)//fpt

        if self.vx == 0 and ncord[0] - self.x != 0:
            self.x = ncord[0]

        if self.vy == 0 and ncord[1] - self.y != 0:
            self.y = ncord[1]

    def update(self, screen, x_offset, y_offset):
        self.y += self.vy
        self.x += self.vx

        draw.rect(screen, (10, 10, 10), (self.x - x_offset, self.y - y_offset, self.player_size, self.player_size))


