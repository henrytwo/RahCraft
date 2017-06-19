"""
This file contains the player classes, player.Player and player.RemotePlayer. These two classes are responsible for
handling all the players in the game. These classes handle animation, physics and other interactions for the player.

Main Player Developer: Syed Safwaan
"""

# ----- Pre-Program Initializations and Imports

# Stock modules to import
from pygame import *  # to allow use of graphics
from math import *  # to allow use of trigomometric functions

# Game modules to import
import CLIENT.components.rahma as rah  # to allow use of general convenience functions

# Initlalization of modules
font.init()  # allowing use of fonts

# Creating Font objects to use for text
normal_font = font.Font("fonts/minecraft.ttf", 14)  # used for nametags

# Surrounding shifts list to detect blocks around player
surrounding_shifts = [(sx, sy) for sy in range(-2, 3) for sx in range(-1, 2)]


# ----- Player Classes

# ~ Main Player Class ~

# This class is used to make the main player, the player the user controls.

# Define class name as Player
class Player:
    # Method to initialize player in game
    def __init__(self, x, y, w, h, cap, controls):

        """ Initalizes the main player. """

        # Note - When naming the attributes:
        # 'self.<...>' indicates private attribute (cannot be accessed in outer scope)
        # 'self.<...>' indicates public

        # - Player Positional Attributes
        # These attributes help with positioning and collision.

        # Player rect
        self.rect = Rect(x, y, w, h)

        # Float positional coordinates (because pygame rects don't like floats)
        self.actual_x = x  # x-coordinate
        self.actual_y = y  # y-coordinate

        # List to hold surrounding blocks for collision
        self.surrounding_blocks = []  # initially empty

        # - Player Movement Attributes
        # These attributes help with player physics and movement.

        # Velocity attributes (to give player movement)
        self.vx = 0  # x-velocity
        self.vy = 0  # y-velocity

        # Acceleration attributes (to change the player's velocity)
        self.vx_inc = 0.15  # x-acceleration
        self.vy_inc = 0.5  # y-acceleration

        # Base y-velocity on jump
        self.base_vy = -(cap // 10 + 4)

        # Max movement speeds
        self.max_walk_vx = cap // 10  # max walking speed
        self.max_run_vx = cap // 5  # max running speed
        self.max_sneak_vx = 1  # max sneaking speed

        # General max movement
        self.max_vx = self.max_walk_vx  # max x speed, walking by default
        self.max_vy = cap  # max fall speed, to prevent player from falling through blocks

        # Fly speed (when fly mode is enabled)
        self.vfly = cap  # set to the cap value to prevent flying through blocks

        # Friction attribute (to slow down play to a stop)
        self.friction = 0.8

        # List containing the keys for controlling the player
        self.controls = controls  # standard WASD controls, can be configured in options

        # - Player Status Attributes
        # These attributes help define current player state.

        # Player direction attributes
        self.dir = 0  # to indicate direction of movement
        self.flipped = 0  # to indicate if player is flipped or not
        self.pointing = 1  # to indicate direction player last faced

        # Player movement states
        self.standing = False  # to indicate if player is standing on ground
        self.sneaking = False  # to indicate if player is sneaking

        # Fall distance attribute to deal fall damage
        self.fall_distance = 0

        # - Player Sprite & Body Attributes
        # These attributes help create the player's sprite.

        # Base limb of player

        # In order to make the limbs swivel around a joint, the limbs are twice their normal length, and one half
        # of the surface is transparent. Since the surfaces rotate around their centre, an illusion of joint movement
        # is gven.

        self.base_limb = Surface((int(h * 3 / 4), (w // 2)), SRCALPHA)  # create the surface
        self.base_limb.fill(Color(125, 125, 125, 125))  # fill the background with a light grey
        self.base_limb.fill(Color(0, 0, 0, 0), (
            0, 0, self.base_limb.get_width() // 2, self.base_limb.get_height()))  # make half transparent
        self.base_limb.fill(Color(255, 255, 255, 255),
                            (self.base_limb.get_width() // 2 + 2, 2,  # fill the inner area with white
                             self.base_limb.get_width() // 2 - 4,
                             self.base_limb.get_height() - 4))

        # Actual limbs in use (base is used for rotation, is never changed)
        self.back_limb = self.base_limb.copy()  # back limbs (far side of player)
        self.front_limb = self.base_limb.copy()  # front limbs  (close side of player)

        # Torso of player
        self.torso = Surface((w // 2, int(h * 3 / 8)), SRCALPHA)  # create the surface
        self.torso.fill(Color(125, 125, 125, 125))  # fill surface with a light grey
        self.torso.fill(Color(255, 255, 255, 255), (2, 2,  # fill the inner area with white
                                                    self.torso.get_width() - 4,
                                                    self.torso.get_height() - 4))

        # Base head of player
        self.base_head = Surface((w, w), SRCALPHA)  # create the surface
        self.base_head.fill(Color(125, 125, 125, 125))  # fill surface with a light grey
        self.base_head.fill(Color(255, 255, 255, 255), (2, 2, w - 4, w - 4))  # fill inner area with white

        # Actual head in use (base is used for rotation, is never changed)
        self.head = self.base_head.copy()

        # - Player Body State Attributes
        # These attributes are used to define what state the player is in and how to animate based on that.

        # Dictionary to hold states
        # The keys are strings, and the values are lists containing maximum angles and movement increment
        self.limb_raises = {
            'standing': [[radians(95), radians(85)], 0.005],  # standing state
            'walking': [[radians(50), radians(130)], 0.06],  # walking state
            'running': [[radians(30), radians(150)], 0.1],  # running state
            'sneaking': [[radians(85), radians(95)], 0.005],  # sneaking state
        }

        # State attribute (changes based on conditions)
        self.state = 'standing'  # default state is standing

        # Angle attributes to rotate the limbs and head
        self.angle_back = radians(90)  # back arm angle
        self.angle_front = radians(90)  # front arm angle
        self.view_angle = 0  # head angle

        # Positional tuples to place limbs and body parts
        self.head_pos = self.rect.centerx, self.rect.y + (h // 8)
        self.neck_pos = self.rect.centerx, self.rect.y + (h // 4)
        self.centre_pos = self.rect.centerx, self.rect.centery - (h // 16)
        self.bottom_pos = self.rect.centerx, self.rect.bottom - (h * 8 / 3)

        # Attributes to control head bobbing
        self.head_bob = 0  # additive to player y-value
        self.head_bob_dir = -1  # direction head is bobbing (+ is down, - is up)

    # Method to control the player
    def control(self, keys, fly):

        """ Handles input from user to control player."""

        # There are 2 modes: flying and not flying. Flying is enabled by pressing 'F' on the keyboard.

        # Check to see if player is flying
        if fly:  # if flying boolean is true

            # Check to see which direction the player wants to fly

            # Horizontal movement logic
            if keys[self.controls[0]] != keys[
                self.controls[1]]:  # if only one button in the horizontal axis is being hit
                if keys[self.controls[0]]:  # if player is pressing left
                    self.vx = -self.vfly  # x-velocity is now equal to max flying velocity in the negative direction
                elif keys[self.controls[1]]:  # if player is pressing right
                    self.vx = self.vfly  # x-velocity is now equal to max flying velocity in the positive direction

            # Vertical movement logic
            if keys[self.controls[2]] != keys[
                self.controls[3]]:  # if only one button in the vertical axis is being hit
                if keys[self.controls[2]]:  # if player is pressing up
                    self.vy = -self.vfly  # y-velocity is now equal to max flying velocity in the negative direction
                elif keys[self.controls[3]]:  # if player is pressing down
                    self.vy = self.vfly

                    # If player is not flying, this block executes
        else:

            # Check to see what speed the player wants to move at

            if keys[K_LSHIFT] != keys[K_LCTRL]:  # if player is either sneaking XOR running
                if keys[K_LSHIFT]:  # if player is pressing the sneak button
                    self.max_vx = self.max_sneak_vx  # the player now is limited to sneak speed
                    self.sneaking = True  # the player is now sneaking
                elif keys[K_LCTRL]:  # if player is pressing the run button
                    self.max_vx = self.max_run_vx  # the player is now limited to run speed
                    self.sneaking = False  # the player is not sneaking

            # If both keys are being pressed, or neither are, this block executes
            else:

                # The player is now limited to walk speed
                self.max_vx = self.max_walk_vx

            # Check to see what direction the player wants to move in

            if keys[self.controls[0]] != keys[self.controls[1]]:  # if player is either moving left XOR right
                if keys[self.controls[0]] and (
                        abs(self.vx) < self.max_vx or self.vx > 0):  # if player is hitting left and is moving left
                    self.dir = -1  # player is moving left
                    self.flipped = 1  # player is facing left (flipped)
                    self.pointing = -1  # player is pointing left
                if keys[self.controls[1]] and (
                        self.vx < self.max_vx or self.vx < 0):  # if player is hitting right and is moving right
                    self.dir = 1  # player is moving right
                    self.flipped = 0  # player is facing right (not flipped)
                    self.pointing = 1  # player is pointing right

            # If both keys are being pressed, or neither are, this block executes
            else:

                # Reset direction to 0
                self.dir = 0  # player is not moving

            # Check to see if the player has a direction

            if self.dir and -self.max_vx < self.vx < self.max_vx:  # if player has a direction other than 0
                self.vx += self.vx_inc * self.dir  # accelerate the player's velocity
            else:  # if player has no direction, is not moving
                self.vx *= self.friction  # slow down the player's velocity using friction

            # Check to see if player is jumping

            if (keys[self.controls[2]] or keys[
                self.controls[4]]) and self.standing:  # if player is on the ground and hit jump
                self.vy = self.base_vy  # set player y-velocity to base value
                self.standing = False  # player is no longer standing

    # Method to detect surrounding blocks for collision
    def detect(self, world, block_size, block_clip, block_properties):

        """ Detects and returns blocks around player to be used for collision."""

        # List to hold surrounding blocks
        self.surrounding_blocks = []

        # For loop to run through all possible blocks around the player
        for x_shift, y_shift in surrounding_shifts:  # for x- and y- shifts in the tuples in the shifts list

            # Get the current block ID using the shifts
            block_id = world[(block_clip[0] - x_shift * block_size) // block_size,
                             (block_clip[1] - y_shift * block_size) // block_size]

            # Check to see if the block is meant to have collision with the player

            if block_id == -1 or block_properties[block_id][
                'collision'] == 'collide':  # if the block is meant to be collided with

                # Add the current block to the block list
                self.surrounding_blocks.append(Rect(block_clip[0] - x_shift * block_size,
                                                    block_clip[1] - y_shift * block_size,
                                                    block_size, block_size))

    # Method to handle collision with other blocks
    def collide(self, fly):

        """ Handles collision with other blocks. """

        # ~ MODEL EXPLANATION
        # - Move the player in the x-direction
        # - Handle collision in the x-direction
        # - Move the player in the y-direction
        # - Handle collision in the y-direction

        # Move the player in the x-direction
        self.actual_x += self.vx  # add the accurate float value to the flat coordinate attribute
        self.rect.x = self.actual_x  # set the rect's x-value to the float value (will be rounded)

        # For loop to detect collision in the x-direction
        for block in self.surrounding_blocks:  # for every block in the block list

            # Check to see if the block is colliding with player
            if self.rect.colliderect(block):  # if block is colliding with player

                # Check to see which direction the player is moving

                if self.vx < 0:  # if the player is moving left
                    self.rect.left = block.right  # align the player's left side with the block's right
                elif self.vx > 0:  # if player is moving right
                    self.rect.right = block.left  # align the player's right side with the block's left

                # Set the actual x value to the rect's x-value, since it may have been altered in collision
                self.actual_x = self.rect.x

                # Set player x-velocity to 0 (not moving horizontally anymore)
                self.vx = 0

        # If player was flying, set x-velocity to 0 every time
        if fly:
            self.vx = 0

        # # Move the player in the y-direction
        self.actual_y += self.vy  # add the accurate float value to the flat coordinate attribute
        self.rect.y = self.actual_y  # set the rect's y-value to the float value (will be rounded)

        # For loop to detect collision in the y-direction
        for block in self.surrounding_blocks:  # for every block in the block list
            # Check to see if the block is colliding with player
            if self.rect.colliderect(block):  # if block is colliding with player

                # Check to see which direction the player is moving

                if self.vy >= 0:  # if player is still or moving down
                    self.rect.bottom = block.top  # align the player's bottom side with the block's top
                    self.standing = True  # player is now standing
                elif self.vy < 0:  # if player is moving down
                    self.rect.top = block.bottom  # align the player's top side with the block's bottom

                # Set the actual x value to the rect's x-value, since it may have been altered in collision
                self.actual_y = self.rect.y

                # Set the fall distance to the velocity at which the player is moving
                self.fall_distance = self.vy

                # Set player y-velocity to 0 (not moving vertically anymore)
                self.vy = 0

        # If player was flying, set x-velocity to 0 every time and set fall distance to y-velocity
        if fly:
            self.fall_distance = self.vy
            self.vy = 0

        # Else, apply gravity normally
        else:
            self.vy += self.vy_inc if self.vy + self.vy_inc < self.max_vy else 0

    # Method to get current player state
    def get_state(self, keys):

        """ Gets the current state of the player. """

        # Set the player state to standing by default.
        self.state = 'standing'

        # Check to see if player was moving in a direction
        if self.dir != 0 and self.vx != 0:  # if player was moving in a direction and had velocity other than 0

            # Check to see if player wanted to change current speed

            if keys[K_LSHIFT]:  # if player is hitting the sneak key
                self.state = 'sneaking'  # player state is now sneaking
            elif keys[K_LCTRL]:  # if player is hitting the run key
                self.state = 'running'  # player state is now running
            else:  # if player is not sneaking or running
                self.state = 'walking'  # player state is now walking

    # Method to animate the player
    def animate(self, surf, x_offset, y_offset, x_focus, y_focus, selected_texture):

        """ Animates the player using current player state. """

        # Define angles for logic (current angle of limb, limit angle specified in the limb raises dict)
        current_angle = round(self.angle_front, int(str(self.limb_raises[self.state][1]).find('.')))
        limit_angle = round(self.limb_raises[self.state][0][0],
                            int(str(self.limb_raises[self.state][1]).find('.')))

        # Check to see how current angle should change

        if current_angle < limit_angle:  # if current angle is less that the limit angle
            self.angle_front += self.limb_raises[self.state][1]  # increase the current angle
            self.angle_back -= self.limb_raises[self.state][1]  # decrease the back angle

        elif current_angle > limit_angle:  # if the current anl=gle is greater than the limit angle
            self.angle_front -= self.limb_raises[self.state][1]  # decrease the current angle
            self.angle_back += self.limb_raises[self.state][1]  # increase the back angle

        else:  # if the current angle is the same as the limit angle

            # Switch the limit angles so arm swing back the other way.
            self.limb_raises[self.state][0] = self.limb_raises[self.state][0][::-1]

        # Check to see if head bob needs to change direction
        if round(self.head_bob) in [3, -1]:  # if the head additive is at one of the limits
            self.head_bob_dir *= -1  # reverse bob direction

        # Move head depending on bob direction and size
        self.head_bob += 0.1 * self.head_bob_dir

        # Create positional tuples to place limbs on
        self.head_pos = self.rect.centerx, self.rect.y + (self.rect.h // 8) + self.head_bob  # for head
        self.neck_pos = self.rect.centerx, self.rect.y + (self.rect.h // 4)  # for arms
        self.centre_pos = self.rect.centerx, self.rect.centery - (self.rect.h // 16)  # for torso
        self.bottom_pos = self.rect.centerx, self.rect.bottom - (self.rect.h * 3 // 8)  # for legs

        # Recreate the back and front limbs for the current frame, using the rah rotation function
        self.back_limb = rah.joint_rotate(self.base_limb, self.angle_back)  # back limb
        self.front_limb = rah.joint_rotate(self.base_limb, self.angle_front)  # front limb

        # Get the current angle that the head is viewing at
        self.view_angle = atan2(y_focus - (self.head_pos[1] - y_offset), x_focus - (self.head_pos[0] - x_offset))

        # Rotate the player head to the view angle
        self.head = rah.joint_rotate(self.base_head, self.view_angle)

        # Blit all the 'back' limbs and body parts onto the screen

        # Back leg
        surf.blit(self.back_limb, rah.point_center(self.bottom_pos[0] - x_offset, self.bottom_pos[1] - y_offset,
                                                   *self.back_limb.get_size()))

        # Back arm
        surf.blit(self.back_limb, rah.point_center(self.neck_pos[0] - x_offset, self.neck_pos[1] - y_offset,
                                                   *self.back_limb.get_size()))

        # Torso
        surf.blit(self.torso, rah.point_center(self.centre_pos[0] - x_offset, self.centre_pos[1] - y_offset,
                                               *self.torso.get_size()))

        # Head
        surf.blit(self.head, rah.point_center(self.head_pos[0] - x_offset, self.head_pos[1] - y_offset,
                                              *self.head.get_size()))

        # Check to see if there is a selected item or tool in player's hand
        if selected_texture:  # if the player had a selected texture in hand

            # Check to see which way the player is pointing at
            if self.pointing == 1:  # if the player is pointing right
                held_angle = self.angle_front - 45  # angle is based in front angle
            else:  # if the player is pointing left
                held_angle = self.angle_back - 45  # angle is based on back angle

            # Scale, rotate and flip the texture according to previous variables
            held_texture = transform.flip(rah.joint_rotate(transform.smoothscale(selected_texture, (30, 30)),
                                                           held_angle), self.flipped, False)

            # Get the position that the item will be centred on (x and y)
            held_x = self.bottom_pos[0] - x_offset + (10 * self.pointing) + self.base_limb.get_width() // 2 * cos(
                self.angle_front)
            held_y = self.bottom_pos[1] - y_offset - 5 - self.base_limb.get_height() // 2 * sin(self.angle_front)

            # Blit the selected tool to the screen (using the rah point centre function to place)
            surf.blit(held_texture, rah.point_center(held_x, held_y, *held_texture.get_size()))

        # Blit all the 'front' limbs and body parts

        # Front leg
        surf.blit(self.front_limb, rah.point_center(self.bottom_pos[0] - x_offset, self.bottom_pos[1] - y_offset,
                                                    *self.front_limb.get_size()))

        # Front arm
        surf.blit(self.front_limb, rah.point_center(self.neck_pos[0] - x_offset, self.neck_pos[1] - y_offset,
                                                    *self.back_limb.get_size()))

    # Method to handle and update player on screen
    def update(self, surf, x_offset, y_offset, fly, ui, block_clip, world, block_size, block_properties,
               selected_texture):

        """ Handles and updates player on screen. """

        # Get the necessary user input details
        keys = key.get_pressed()  # key states
        m_pos = mouse.get_pos()  # mouse position

        # Check to see if any menu is active in game

        if ui:  # if a menu is active

            # Stop player from moving at all
            self.state = "standing"  # player is standing
            self.dir = 0  # player has no direction
        else:  # if no menus are active

            # Collect user input for controls and states data
            self.control(keys, fly)
            self.get_state(keys)

        # Handle collision for the player
        self.detect(world, block_size, block_clip, block_properties)  # get surrounding blocks for collision
        self.collide(fly)  # handle collision with surrounding blocks

        # Animate and blit the player to the screen
        self.animate(surf, x_offset, y_offset, *m_pos, selected_texture)


class RemotePlayer:
    def __init__(self, username, x, y, w, h):
        self.x = x
        self.y = y

        self.vx = 0
        self.vy = 0

        self.w = w
        self.h = h

        self.rect = Rect(x, y, w, h)
        self.target = [x, y]

        self.username = username
        self.name_tag = normal_font.render(username, True, (255, 255, 255))
        self.name_back = Surface((self.name_tag.get_width() + 10, self.name_tag.get_height() + 10), SRCALPHA)
        self.name_back.fill(Color(75, 75, 75, 150))

        self.base_limb = Surface((int(h * 3 / 4), (w // 2)), SRCALPHA)
        self.base_limb.fill(Color(125, 125, 125, 125))
        self.base_limb.fill(Color(0, 0, 0, 0),
                            (0, 0, self.base_limb.get_width() // 2, self.base_limb.get_height()))
        self.base_limb.fill(Color(200, 200, 200, 255), (self.base_limb.get_width() // 2 + 2, 2,
                                                        self.base_limb.get_width() // 2 - 4,
                                                        self.base_limb.get_height() - 4))

        self.back_limb = self.base_limb.copy()
        self.front_limb = self.base_limb.copy()

        self.torso = Surface((w // 2, int(h * 3 / 8)), SRCALPHA)
        self.torso.fill(Color(125, 125, 125, 125))
        self.torso.fill(Color(200, 200, 200, 200), (2, 2,
                                                    self.torso.get_width() - 4,
                                                    self.torso.get_height() - 4))

        self.base_head = Surface((w, w), SRCALPHA)
        self.base_head.fill(Color(125, 125, 125, 125))
        self.base_head.fill(Color(200, 200, 200, 255), (2, 2, w - 4, w - 4))
        self.head = self.base_head.copy()

        self.limb_raises = {
            'standing': [[radians(93), radians(87)], 0.008],
            'walking': [[radians(50), radians(130)], 0.06],
            'running': [[radians(30), radians(150)], 0.1],
            'sneaking': [[radians(85), radians(95)], 0.005],
        }

        self.state = 'standing'

        self.angle_front = self.angle_back = radians(90)

        self.head_pos = self.rect.centerx, self.rect.y + (h // 8)
        self.neck_pos = self.rect.centerx, self.rect.y + (h // 4)
        self.centre_pos = self.rect.centerx, self.rect.centery - (h // 16)
        self.bottom_pos = self.rect.centerx, self.rect.bottom - (h * 8 / 3)

        self.head_bob = 0
        self.head_bob_dir = -1

    def calculate_velocity(self, ncord, fpt):
        self.target = ncord[:]
        self.vy = (ncord[1] - self.y) // fpt
        self.vx = (ncord[0] - self.x) // fpt

        if self.vx == 0 and ncord[0] - self.x != 0:
            self.x = ncord[0]

        if self.vy == 0 and ncord[1] - self.y != 0:
            self.y = ncord[1]

    def get_state(self):
        if self.vx == 0:
            self.state = 'standing'
        elif abs(self.vx) > (self.h // 10):
            self.state = 'running'
        elif abs(self.vx) > 1:
            self.state = 'walking'
        else:
            self.state = 'sneaking'

        print(self.state)

    def animate(self, surf, x_offset, y_offset):
        if round(self.angle_front, int(str(self.limb_raises[self.state][1]).find('.'))) \
                < round(self.limb_raises[self.state][0][0],
                        int(str(self.limb_raises[self.state][1]).find('.'))):
            self.angle_front += self.limb_raises[self.state][1]
            self.angle_back -= self.limb_raises[self.state][1]

        elif round(self.angle_front, int(str(self.limb_raises[self.state][1]).find('.'))) \
                > round(self.limb_raises[self.state][0][0],
                        int(str(self.limb_raises[self.state][1]).find('.'))):
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

        self.back_limb = rah.joint_rotate(self.base_limb, self.angle_front)
        self.front_limb = rah.joint_rotate(self.base_limb, self.angle_back)

        surf.blit(self.back_limb, rah.point_center(self.bottom_pos[0], self.bottom_pos[1],
                                                   *self.back_limb.get_size()))

        surf.blit(self.back_limb, rah.point_center(self.neck_pos[0], self.neck_pos[1],
                                                   *self.back_limb.get_size()))
        surf.blit(self.torso, rah.point_center(self.centre_pos[0], self.centre_pos[1],
                                               *self.torso.get_size()))
        surf.blit(self.head, rah.point_center(self.head_pos[0], self.head_pos[1],
                                              *self.head.get_size()))
        surf.blit(self.front_limb, rah.point_center(self.bottom_pos[0], self.bottom_pos[1],
                                                    *self.front_limb.get_size()))
        surf.blit(self.front_limb, rah.point_center(self.neck_pos[0], self.neck_pos[1],
                                                    *self.back_limb.get_size()))

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

        self.rect = Rect(self.x - x_offset, self.y - y_offset, self.w, self.h)

        # draw.rect(surf, (125, 125, 125), self.rect)

        surf.blit(self.name_back, rah.center(self.x - x_offset, self.y - 40 - y_offset, 20, 20,
                                             self.name_back.get_width(), self.name_back.get_height()))
        surf.blit(self.name_tag, rah.center(self.x - x_offset, self.y - 40 - y_offset, 20, 20,
                                            self.name_tag.get_width(), self.name_tag.get_height()))
        self.get_state()
        self.animate(surf, self.x - x_offset, self.y - y_offset)
