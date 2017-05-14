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

    def control(self):

        if key.get_pressed()[self.controls[0]]:
            self.vx = -self.run_speed
        if key.get_pressed()[self.controls[1]]:
            self.vx = self.run_speed
        if key.get_pressed()[self.controls[2]] and self.standing:
            self.vy = self.jump_height

        self.standing = False

    def collide(self, blocks):
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

        for block in blocks:
            if self.rect.colliderect(block):
                if self.vx > 0:
                    self.rect.right = block.left

                elif self.vx < 0:
                    self.rect.left = block.right

        self.vx = 0
        if self.vy + self.gravity < self.rect.h and not bumped:
            self.vy += self.gravity
        else:
            self.vy -= 0

    def update(self, screen, collision_blocks, x_offset, y_offset):
        self.control()
        self.collide(collision_blocks)
        draw.rect(screen, (255, 0, 0), (self.rect.x - x_offset, self.rect.y - y_offset, self.rect.w, self.rect.h))
