from pygame import *
import components.rahma as rah

font.init()

normal_font = font.Font("fonts/minecraft.ttf", 14)


class Player:
    def __init__(self, x, y, w, h, name, block_type, screen_size):
        self.rect = Rect((x, y, w, h))

        self.vx = 0
        self.vy = 0
        self.max_fall = h
        self.standing = False

        self.name = name
        self.name_tag = normal_font.render(name, True, (255, 255, 255))
        self.name_back = Surface((self.name_tag.get_width() + 10, self.name_tag.get_height + 10), SRCALPHA)
        self.name_back.fill(Color(75, 75, 75, 150))

        self.block_type = block_type
        self.screen_size = screen_size

    def control(self):

        if key.get_pressed()[K_a]:
            self.vx = -8
        if key.get_pressed()[K_d]:
            self.vx = 8
        if key.get_pressed()[K_w] and self.standing:
            self.vy = -23

        self.standing = False

    def detect(self, blocks):

        self.rect.y += self.vy

        for block in blocks:
            if type(block) is self.block_type and self.rect.colliderect(block.rect):
                if self.vy > 0:
                    self.rect.bottom = block.rect.top

                    self.standing = True
                if self.vy < 0:
                    self.rect.top = block.rect.bottom

                self.vy = 0

        self.rect.centerx = (self.rect.centerx + self.vx) % self.screen_size[0]

        for block in blocks:
            if type(block) is self.block_type and self.rect.colliderect(block.rect):
                if self.vx > 0:
                    self.rect.right = block.rect.left
                if self.vx < 0:
                    self.rect.left = block.rect.right

        self.vx = 0
        self.vy += 2 if self.vy + 1 < self.max_fall else 0

    def debug(self, surf):
        draw.rect(surf, (0, 0, 0), self.rect, 2)
        draw.circle(surf, (0, 0,0 ), (self.rect.x, self.rect.y), 5, 2)

    def update(self, surf, de = False):
        if de:
            self.debug(surf)
        self.control()
        draw.rect(surf, (255, 0, 0), self.rect)
        surf.blit(self.name_back, rah.center(self.rect.x - 10, self.rect.y - 40, 20, 20, self.name_back.get_width(), self.name_back.get_height()))
        surf.blit(self.name_tag, rah.center(self.rect.x - 10, self.rect.y - 40, 20, 20, self.name_tag.get_width(), self.name_tag.get_height()))
