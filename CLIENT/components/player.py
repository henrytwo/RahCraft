from pygame import *
from math import *
import numpy

import CLIENT.components.rahma as rah

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
        self.facing = 0
        self.pointing = 1
        self.standing = False
        self.sneaking = False

        self.fall_distance = 0

        self.surrounding_shifts = [(sx, sy) for sy in range(-2, 3) for sx in range(-1, 2)]

        self.base_limb = Surface((int(h * 3 / 4), (w // 2)), SRCALPHA)
        self.base_limb.fill(Color(125, 125, 125, 125))
        self.base_limb.fill(Color(0, 0, 0, 0), (0, 0, self.base_limb.get_width() // 2, self.base_limb.get_height()))
        self.base_limb.fill(Color(255, 255, 255, 255), (self.base_limb.get_width() // 2 + 2, 2,
                                                        self.base_limb.get_width() // 2 - 4,
                                                        self.base_limb.get_height() - 4))

        self.left_limb = self.base_limb.copy()
        self.right_limb = self.base_limb.copy()

        self.torso = Surface((w // 2, int(h * 3 / 8)), SRCALPHA)
        self.torso.fill(Color(125, 125, 125, 125))
        self.torso.fill(Color(255, 255, 255, 255), (2, 2,
                                                    self.torso.get_width() - 4,
                                                    self.torso.get_height() - 4))

        self.base_head = Surface((w, w), SRCALPHA)
        self.base_head.fill(Color(125, 125, 125, 125))
        self.base_head.fill(Color(255, 255, 255, 255), (2, 2, w - 4, w - 4))
        self.head = self.base_head.copy()

        self.limb_raises = {
            'standing': [[radians(93), radians(87)], 0.008],
            'walking': [[radians(50), radians(130)], 0.06],
            'running': [[radians(30), radians(150)], 0.1],
            'sneaking': [[radians(85), radians(95)], 0.005],
        }

        self.state = 'standing'

        self.angle_front = self.angle_back = radians(90)
        self.view_angle = 0

        self.head_pos = self.rect.centerx, self.rect.y + (h // 8)
        self.neck_pos = self.rect.centerx, self.rect.y + (h // 4)
        self.centre_pos = self.rect.centerx, self.rect.centery - (h // 16)
        self.bottom_pos = self.rect.centerx, self.rect.bottom - (h * 8 / 3)

        self.head_bob = 0
        self.head_bob_dir = -1

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
                    self.facing = 1
                    self.pointing = -1
                if keys[self.controls[1]] and (self.vx < self.max_vx or self.vx < 0):
                    self.dir = 1
                    self.facing = 0
                    self.pointing = 1
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
                self.fall_distance = self.vy
                self.vy = 0

        if fly:
            self.fall_distance = self.vy
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

    def get_state(self, keys):
        self.state = 'standing'

        if self.dir != 0 and self.vx != 0:
            if keys[K_LCTRL]:
                self.state = 'running'
            elif keys[K_LSHIFT]:
                self.state = 'sneaking'
            else:
                self.state = 'walking'

    def animate(self, surf, x_offset, y_offset, x_focus, y_focus, selected_texture):
        if round(self.angle_front, int(str(self.limb_raises[self.state][1]).find('.'))) \
                < round(self.limb_raises[self.state][0][0], int(str(self.limb_raises[self.state][1]).find('.'))):
            self.angle_front += self.limb_raises[self.state][1]
            self.angle_back -= self.limb_raises[self.state][1]

        elif round(self.angle_front, int(str(self.limb_raises[self.state][1]).find('.'))) \
                > round(self.limb_raises[self.state][0][0], int(str(self.limb_raises[self.state][1]).find('.'))):
            self.angle_front -= self.limb_raises[self.state][1]
            self.angle_back += self.limb_raises[self.state][1]

        else:
            self.limb_raises[self.state][0] = self.limb_raises[self.state][0][::-1]

        if round(self.head_bob) in [3, -1]:
            self.head_bob_dir *= -1

        self.head_bob += 0.1 * self.head_bob_dir

        self.head_pos = self.rect.centerx, self.rect.y + (self.rect.h // 8) + self.head_bob
        self.neck_pos = self.rect.centerx, self.rect.y + (self.rect.h // 4)
        self.centre_pos = self.rect.centerx, self.rect.centery - (self.rect.h // 16)
        self.bottom_pos = self.rect.centerx, self.rect.bottom - (self.rect.h * 3 // 8)

        self.left_limb = rah.joint_rotate(self.base_limb, self.angle_front, True)
        self.right_limb = rah.joint_rotate(self.base_limb, self.angle_back, True)

        self.view_angle = atan2(y_focus - (self.head_pos[1] - y_offset), x_focus - (self.head_pos[0] - x_offset))

        self.head = rah.joint_rotate(self.base_head, self.view_angle, False)

        surf.blit(self.left_limb, rah.point_center(self.bottom_pos[0] - x_offset, self.bottom_pos[1] - y_offset,
                                                   *self.left_limb.get_size()))

        surf.blit(self.left_limb, rah.point_center(self.neck_pos[0] - x_offset, self.neck_pos[1] - y_offset,
                                                   *self.left_limb.get_size()))
        surf.blit(self.torso, rah.point_center(self.centre_pos[0] - x_offset, self.centre_pos[1] - y_offset,
                                               *self.torso.get_size()))
        surf.blit(self.head, rah.point_center(self.head_pos[0] - x_offset, self.head_pos[1] - y_offset,
                                              *self.head.get_size()))
        if selected_texture:
            if self.pointing == 1:
                held_angle = self.angle_back - 45
            else:
                held_angle = self.angle_front - 45
            held_texture = transform.flip(rah.joint_rotate(transform.smoothscale(selected_texture, (30, 30)),
                                                           held_angle, False), self.facing, False)
            surf.blit(held_texture, rah.point_center(
                self.bottom_pos[0] - x_offset + (10 * self.pointing) + self.base_limb.get_width() // 2 * cos(self.angle_back),
                self.bottom_pos[1] - y_offset - 5 - self.base_limb.get_height() // 2 * sin(self.angle_back),
                *held_texture.get_size()))

        surf.blit(self.right_limb, rah.point_center(self.bottom_pos[0] - x_offset, self.bottom_pos[1] - y_offset,
                                                    *self.right_limb.get_size()))
        surf.blit(self.right_limb, rah.point_center(self.neck_pos[0] - x_offset, self.neck_pos[1] - y_offset,
                                                    *self.left_limb.get_size()))

    def update(self, surf, x_offset, y_offset, fly, ui, block_clip, world, block_size, block_properties,
               selected_texture):

        keys = key.get_pressed()
        m_pos = mouse.get_pos()

        collision_blocks = self.detect(world, block_size, block_clip, block_properties)

        if not ui:
            self.get_state(keys)
            self.control(keys, fly)

        self.collide(collision_blocks, fly)
        self.animate(surf, x_offset, y_offset, *m_pos, selected_texture)

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


class RemotePlayer:
    def __init__(self, username, x, y, w, h):
        self.x = x
        self.y = y

        self.vx = 0
        self.vy = 0

        self.w = w
        self.h = h

        self.frame = 0
        self.frame_additive = 0.5

        head = image.load('textures/player_head.png')
        body = image.load('textures/player_body.png')

        self.texture = {'head': transform.scale(head, (int(w * 0.5), int((w * 0.5) / head.get_width() * head.get_height()))),
                        'body':transform.scale(body, (int(w * 0.9), int((w * 0.9)/body.get_width() * body.get_height())))}

        self.target = [x, y]

        self.username = username
        self.name_tag = normal_font.render(username, True, (255, 255, 255))
        self.name_back = Surface((self.name_tag.get_width() + 10, self.name_tag.get_height() + 10), SRCALPHA)
        self.name_back.fill(Color(75, 75, 75, 150))

    def calculate_velocity(self, ncord, fpt):
        self.target = ncord[:]
        self.vy = (ncord[1] - self.y) // fpt
        self.vx = (ncord[0] - self.x) // fpt

        if self.vx == 0 and ncord[0] - self.x != 0:
            self.x = ncord[0]

        if self.vy == 0 and ncord[1] - self.y != 0:
            self.y = ncord[1]

    def update(self, surf, x_offset, y_offset):
        if self.vy > 0 and self.y + self.vy < self.target[1]:
            self.y += self.vy
        elif self.vy < 0 and self.y + self.vy > self.target[1]:
            self.y += self.vy
        else:
            self.vy = 0
            self.y = self.target[1]

        if self.vx > 0 and self.x + self.vx < self.target[0]:
            self.x += self.vx
        elif self.vx < 0 and self.x + self.vx > self.target[0]:
            self.x += self.vx
        else:
            self.vx = 0
            self.x = self.target[0]

        self.frame += self.frame_additive

        if self.frame <-5 or self.frame > 5:
            self.frame_additive *= -1

        surf.blit(self.texture['head'], (self.x - x_offset + self.w//2 - (self.texture['head'].get_width() * 1.1)//2, self.y - y_offset - int(self.frame)))
        surf.blit(self.texture['body'], (self.x - x_offset + self.w//2 - self.texture['body'].get_width()//2, self.y - y_offset + self.h - self.texture['body'].get_height()))


        surf.blit(self.name_back, rah.center(self.x - x_offset, self.y - 40 - y_offset, 20, 20,
                                             self.name_back.get_width(), self.name_back.get_height()))
        surf.blit(self.name_tag, rah.center(self.x - x_offset, self.y - 40 - y_offset, 20, 20,
                                            self.name_tag.get_width(), self.name_tag.get_height()))

