from pygame import *
from math import *
import numpy

import components.rahma as rah

font.init()

normal_font = font.Font("fonts/minecraft.ttf", 14)
index_font = font.Font("fonts/minecraft.ttf", 10)


class Player:
    def __init__(self, x, y, w, h, cap, reach, controls):
        self.rect = Rect(x, y, w, h)

        self.actual_x = x
        self.actual_y = y

        self.vx = 0
        self.vy = 0

        self.vx_inc = 0.15
        self.vy_inc = 0.5

        self.base_vy = -(cap // 10 + 4)

        self.max_walk_vx = cap // 10
        self.max_dash_vx = cap // 5
        self.max_sneak_vx = 1

        self.max_vx = self.max_walk_vx
        self.max_vy = cap

        self.vfly = cap

        self.friction = 0.8

        self.reach = reach

        self.controls = controls

        self.dir = 0
        self.standing = False
        self.sneaking = False

        self.surrounding_shifts = [(sx, sy) for sy in range(-2, 3) for sx in range(-1, 2)]

        # self.frame = 0
        # self.frame_additive = 0.5
        #
        # head = image.load('textures/player_head.png')
        # body = image.load('textures/player_body.png')
        #
        # self.texture = {
        #     'head': transform.scale(head, (int(w * 0.5), int((w * 0.5) / head.get_width() * head.get_height()))),
        #     'body': transform.scale(body, (int(w * 0.9), int((w * 0.9) / body.get_width() * body.get_height())))
        # }

        self.base_limb = Surface((w // 2, int(h * 3 // 16)), SRCALPHA)
        self.left_limb = self.right_limb = self.base_limb.copy()

        self.base_head = Surface((w, w), SRCALPHA)
        self.head = self.base_head.copy()

        self.torso = self.base_limb.copy()

        self.limb_raises = {
            'standing': [80, 100],
            'walking': [50, 130],
            'running': [30, 150],
            'sneaking': [85, 95],
        }

        self.state = 'standing'

        self.angle_front = self.angle_back = 90
        self.view_angle = 0

        self.head_pos = self.rect.centerx, self.rect.y + (h // 8)
        self.neck_pos = self.rect.centerx, self.rect.y + (h // 4)
        self.centre_pos = self.rect.centerx, self.rect.centery - (h // 16)
        self.bottom_pos = self.rect.centerx, self.rect.bottom - (h * 8 / 3)

    def get_state(self, keys):
        self.state = 'standing'

        if True in [keys[self.controls[i]] for i in [0, 1]]:
            if keys[K_LCTRL]:
                self.state = 'running'
            elif keys[K_LSHIFT]:
                self.state = 'sneaking'
            else:
                self.state = 'walking'

    def animate(self, surf, x_offset, y_offset, x_focus, y_focus):
        if self.angle_front < self.limb_raises[self.state][0]:
            self.angle_front += 0.005
            self.angle_back -= 0.005

        elif self.angle_front > self.limb_raises[self.state][0]:
            self.angle_front -= 0.005
            self.angle_back += 0.005

        elif self.angle_front == self.limb_raises[self.state][0]:
            self.limb_raises[self.state] = self.limb_raises[self.state][::-1]

        self.left_limb = rah.joint_rotate(self.base_limb, self.angle_front, True)
        self.right_limb = rah.joint_rotate(self.base_limb, self.angle_back, True)

        self.view_angle = atan2(x_focus - self.rect.centerx - x_offset, y_focus - self.rect.centery - y_offset)

        self.head = rah.joint_rotate(self.base_head, self.view_angle, False)

        surf.blit(self.left_limb, rah.point_center(self.bottom_pos[0] - x_offset, self.bottom_pos[1] - y_offset,
                                                   *self.left_limb.get_size()))
        surf.blit(self.right_limb, rah.point_center(self.bottom_pos[0] - x_offset, self.bottom_pos[1] - y_offset,
                                                    *self.right_limb.get_size()))
        surf.blit(self.torso, rah.point_center(self.centre_pos[0] - x_offset, self.centre_pos[1] - y_offset,
                                               *self.torso.get_size()))
        surf.blit(self.right_limb, rah.point_center(self.neck_pos[0] - x_offset, self.neck_pos[1] - y_offset,
                                                    *self.left_limb.get_size()))
        surf.blit(self.left_limb, rah.point_center(self.neck_pos[0] - x_offset, self.neck_pos[1] - y_offset,
                                                   *self.left_limb.get_size()))
        surf.blit(self.head, rah.point_center(self.head_pos[0] - x_offset, self.head_pos[1] - y_offset,
                                              *self.head.get_size()))

    def control(self, keys, fly):
        if fly:
            if keys[self.controls[0]]:
                self.vx = -self.vfly
            if keys[self.controls[1]]:
                self.vx = self.vfly

            if keys[self.controls[2]] or keys[self.controls[4]]:
                self.vy = -self.vfly
            if keys[self.controls[3]]:
                self.vy = self.vfly

        else:
            self.dir = 0
            self.sneaking = False

            if keys[K_LSHIFT] != keys[K_LCTRL]:
                if keys[K_LSHIFT]:
                    self.max_vx = self.max_sneak_vx
                    self.sneaking = True
                elif keys[K_LCTRL]:
                    self.max_vx = self.max_dash_vx
            else:
                self.max_vx = self.max_walk_vx

            if keys[self.controls[0]] != keys[self.controls[1]]:
                if keys[self.controls[0]] and (abs(self.vx) < self.max_vx or self.vx > 0):
                    self.dir = -1
                if keys[self.controls[1]] and (self.vx < self.max_vx or self.vx < 0):
                    self.dir = 1
            else:
                self.dir = 0

            if self.dir:
                self.vx += self.vx_inc * self.dir
            else:
                self.vx *= self.friction

            if (keys[self.controls[2]] or keys[self.controls[4]]) and self.standing:
                self.vy = self.base_vy
                self.standing = False

    def collide(self, blocks, fly):
        if self.sneaking and type(blocks[4]) is not Rect:
            if (self.dir == -1 and blocks[3].__class__ == Rect and self.rect.right == blocks[3].left) \
                    or (self.dir == 1 and blocks[5].__class__ == Rect and self.rect.left == blocks[5].right):
                self.actual_x -= self.vx

            else:
                self.actual_x += self.vx

        else:
            self.actual_x += self.vx

        self.rect.x = self.actual_x

        for block in blocks:
            if type(block) is Rect and self.rect.colliderect(block):
                if self.vx > 0:
                    self.rect.right = block.left
                elif self.vx < 0:
                    self.rect.left = block.right

                self.actual_x = self.rect.x
                self.vx = 0

        if fly:
            self.vx = 0

        self.actual_y += self.vy
        self.rect.y = self.actual_y

        for block in blocks:
            if type(block) is Rect and self.rect.colliderect(block):
                if self.vy >= 0:
                    self.rect.bottom = block.top
                    self.standing = True
                elif self.vy < 0:
                    self.rect.top = block.bottom

                self.actual_y = self.rect.y
                self.vy = 0

        if fly:
            self.vy = 0
        else:
            self.vy += self.vy_inc if self.vy + self.vy_inc < self.max_vy else 0

    def detect(self, world, block_size, block_clip, block_properties):
        surrounding_blocks = []

        for x_shift, y_shift in self.surrounding_shifts:
            block_id = world[(block_clip[0] - x_shift * block_size) // block_size, (
                block_clip[1] - y_shift * block_size) // block_size]

            if block_id == -1 or block_properties[block_id]['collision'] == 'collide':
                surrounding_blocks.append(
                    Rect(block_clip[0] - x_shift * block_size, block_clip[1] - y_shift * block_size, block_size,
                         block_size))
            else:
                surrounding_blocks.append((block_clip[0] - x_shift * block_size, block_clip[1] - y_shift * block_size,
                                           block_size, block_size))

        return surrounding_blocks

    def update(self, surf, x_offset, y_offset, fly, ui, block_clip, world, block_size, block_properties,
               selected_texture):

        keys = key.get_pressed()
        m_pos = mouse.get_pos()

        collision_blocks = self.detect(world, block_size, block_clip, block_properties)

        if not ui:
            self.get_state(keys)
            self.control(keys, fly)

        self.collide(collision_blocks, fly)
        self.animate(surf, x_offset, y_offset, *m_pos)

        # for block in collision_blocks:
        #     if type(block) is Rect:
        #         draw.rect(surf, (200, 200, 200), (block.x - x_offset, block.y - y_offset, *block.size))
        #     if (self.dir == -1 and collision_blocks.index(block) == 3) or (self.dir == 1 and collision_blocks.index(block) == 5):
        #         draw.rect(surf, (255, 0, 0), (block[0] - x_offset, block[1] - y_offset, block[2], block[3]))
        #     surf.blit(index_font.render("{0}".format(collision_blocks.index(block)), True, (0, 0, 0)),
        #               (block[0] - x_offset, block[1] - y_offset))

        # draw.rect(surf, (255, 255, 255), (self.rect.x - x_offset, self.rect.y - y_offset, self.rect.w, self.rect.h))

        # self.frame += self.frame_additive
        #
        # if self.frame <-5 or self.frame > 5:
        #     self.frame_additive *= -1
        #
        # surf.blit(self.texture['head'], (self.rect.x - x_offset + self.rect.w//2 - (self.texture['head'].get_width() * 1.1)//2, self.rect.y - y_offset - int(self.frame)))
        # surf.blit(self.texture['body'], (self.rect.x - x_offset + self.rect.w//2 - self.texture['body'].get_width()//2, self.rect.y - y_offset + self.rect.h - self.texture['body'].get_height()))
        #
        # surf.blit(selected_texture, (0,0))
        #
        # surf.blit(selected_texture, (self.rect.x + self.rect.w - selected_texture.get_width(), self.rect.y + self.rect.h//2 - selected_texture.get_height()//2))


class RemotePlayer:
    def __init__(self, username, x, y, w, h):
        self.x = x
        self.y = y

        self.vx = 0
        self.vy = 0

        self.w = w
        self.h = h

        self.username = username
        self.name_tag = normal_font.render(username, True, (255, 255, 255))
        self.name_back = Surface((self.name_tag.get_width() + 10, self.name_tag.get_height() + 10), SRCALPHA)
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

        draw.rect(surf, (125, 125, 125), (self.x - x_offset, self.y - y_offset, self.w, self.h))
        surf.blit(self.name_back, rah.center(self.x - x_offset, self.y - 40 - y_offset, 20, 20,
                                             self.name_back.get_width(), self.name_back.get_height()))
        surf.blit(self.name_tag, rah.center(self.x - x_offset, self.y - 40 - y_offset, 20, 20,
                                            self.name_tag.get_width(), self.name_tag.get_height()))

# Lighting
# draw.circle(self.reach_surf, Color(255, 255, 255, (reach * 20 - a) * 2), (reach * 20, reach * 20), a)

# self.reach_surf = Surface((reach * 40, reach * 40), SRCALPHA)
# for a in range(reach * 10, 0, -5):
#     draw.circle(self.reach_surf, Color(255, 255, 255, a), (reach * 20, reach * 20), a * 2)

# KKK model
# triangle = [(self.rect.x - x_offset, self.rect.y - y_offset + self.rect.h // 2),
#             (self.rect.x - x_offset + self.rect.w//2, self.rect.y - y_offset),
#             (self.rect.x - x_offset + self.rect.w, self.rect.y - y_offset + self.rect.h // 2)]
#
# draw.polygon(surf, (255, 255, 255), triangle)
# draw.rect(surf, (255, 255, 255), (self.rect.x - x_offset, self.rect.y - y_offset + self.rect.h//2, self.rect.w, self.rect.h//2))
# center = (self.rect.x - x_offset + self.rect.w // 2, self.rect.y - y_offset + self.rect.h // 2)
# draw.circle(surf, (0, 0, 0), center, reach * 20, 3)

# surf.blit(self.reach_surf,
#           ((self.rect.centerx - self.reach * 20) - x_offset, (self.rect.centery - self.reach * 20) - y_offset))
