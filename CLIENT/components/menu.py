from pygame import *
import json

import CLIENT.components.rahma as rah

button_hover = image.load("textures/menu/button_hover.png")
button_pressed = image.load("textures/menu/button_pressed.png")
button_idle = image.load("textures/menu/button_idle.png")

class Button:
    def __init__(self, x, y, w, h, func, text):
        self.rect = Rect(x, y, w, h)
        self.text = text
        self.func = func

        self.hover_img = transform.scale(button_hover, (w, h))
        self.press_img = transform.scale(button_pressed, (w, h))
        self.idle_img = transform.scale(button_idle, (w, h))

    def highlight(self, surf):
        surf.blit(self.hover_img, self.rect)

    def mouse_down(self, surf):
        surf.blit(self.press_img, self.rect)

    def idle(self, surf):
        surf.blit(self.idle_img, self.rect)

    def update(self, surf, mx, my, m_press, size, release):
        if self.rect.collidepoint(mx, my):
            if m_press[0]:
                self.mouse_down(surf)

            elif release:
                mouse.set_cursor(*cursors.tri_left)

                rah.load_sound(['sound/random/click.ogg'])
                return self.func

            else:
                self.highlight(surf)
        else:
            self.idle(surf)

        text_surf = rah.text(self.text, size)
        surf.blit(text_surf, rah.center(*self.rect, text_surf.get_width(), text_surf.get_height()))

class Slider:
    def __init__(self, x, y, w, h, position, text):
        self.rect = Rect(x, y, w, h)
        self.text = text
        self.pos = position

        self.texture = {'hover':transform.scale(button_hover, (20, h - 3)),
                        'idle':transform.scale(button_idle, (20, h - 3))}

    def update(self, surf, mx, my, m_press, size, release):
        draw.rect(surf, (0, 0, 0), self.rect)
        draw.rect(surf, (200, 200, 200), self.rect, 1)

        if self.rect.collidepoint(mx, my):
            mouse_state =  'hover'
            if m_press[0]:
                self.pos = (mx - self.rect.x)/self.rect.w

            if release:
                rah.load_sound(['sound/random/click.ogg'])

        else:
            mouse_state = 'idle'

        surf.blit(self.texture[mouse_state], (self.rect.x + min(max(self.pos, ((self.texture[mouse_state].get_width() + 2)//2)/self.rect.w), 1 - ((self.texture[mouse_state].get_width() + 3)//2)/self.rect.w) * self.rect.w - self.texture[mouse_state].get_width()//2, self.rect.y + 1))

        text_surf = rah.text(self.text, size)
        surf.blit(text_surf, rah.center(*self.rect, text_surf.get_width(), text_surf.get_height()))

class Toggle:
    def __init__(self, x, y, w, h, state, text):
        self.rect = Rect(x, y, w, h)
        self.text = text
        self.state = state

        self.texture = {'idle':transform.scale(button_idle, (w, h)),
                        'press':transform.scale(button_pressed, (w, h))}

    def draw_button(self, surf, type, size):

        surf.blit(self.texture[type], (self.rect.x, self.rect.y))

        text_surf = rah.text(self.text, size)
        surf.blit(text_surf, rah.center(*self.rect, text_surf.get_width(), text_surf.get_height()))


    def update(self, surf, mx, my, m_press, size, release):

        if self.rect.collidepoint(mx, my):
            if release:
                mouse.set_cursor(*cursors.tri_left)

                rah.load_sound(['sound/random/click.ogg'])

                self.state = not self.state

        if self.state:
            self.draw_button(surf, 'press', size)
        else:
            self.draw_button(surf, 'idle', size)



class Switch:
    def __init__(self, x, y, w, h, state, text):
        self.rect = Rect(x, y, w, h)
        self.text = text
        self.state = state

        self.slider_x = 0
        self.slider_v = 0

        slider_w = self.rect.w//2 - 5
        slider_h = self.rect.h - 6

        self.texture = {'hover':transform.scale(button_hover, (slider_w, slider_h)),
                        'idle':transform.scale(button_idle, (slider_w, slider_h))}

    def draw_button(self, surf, offset, type, size):
        draw.rect(surf, (200, 200, 200), self.rect)
        draw.rect(surf, (20,20,20), (self.rect.x + 2, self.rect.y + 2, self.rect.w - 4, self.rect.h - 4))

        surf.blit(self.texture[type], (self.rect.x + 3 + offset, self.rect.y + 3))

        text_surf = rah.text(self.text, size)
        surf.blit(text_surf, rah.center(self.rect.x + 3 + offset, self.rect.y + 3, *self.texture['idle'].get_size(),\
                                        text_surf.get_width(), text_surf.get_height()))


    def turn_on(self):
        self.state = True
        self.slider_v = 15

    def turn_off(self):
        self.state = False
        self.slider_v = -15

    def update(self, surf, mx, my, m_press, size, release):

        self.slider_x += self.slider_v

        if self.slider_x <= 0 or self.slider_x > self.rect.w//2:
            self.slider_v = 0

        if self.slider_x < 0:
            self.slider_x = 0

        elif self.slider_x > self.rect.w//2:
            self.slider_x = self.rect.w//2

        if self.rect.collidepoint(mx, my):

            if release:
                mouse.set_cursor(*cursors.tri_left)

                rah.load_sound(['sound/random/click.ogg'])

                if self.state:
                    self.turn_off()
                else:
                    self.turn_on()

            else:
                 self.draw_button(surf, self.slider_x, 'hover', size)

        else:
            self.draw_button(surf, self.slider_x, 'idle', size)


click_cursor = ["      ..                ",
                "     .XX.               ",
                "     .XX.               ",
                "     .XX.               ",
                "     .XX.               ",
                "     .XX.               ",
                "     .XX...             ",
                "     .XX.XX...          ",
                "     .XX.XX.XX.         ",
                "     .XX.XX.XX...       ",
                "     .XX.XX.XX.XX.      ",
                "     .XX.XX.XX.XX.      ",
                "...  .XX.XX.XX.XX.      ",
                ".XX...XXXXXXXXXXX.      ",
                ".XXXX.XXXXXXXXXXX.      ",
                " .XXX.XXXXXXXXXXX.      ",
                "  .XXXXXXXXXXXXXX.      ",
                "  .XXXXXXXXXXXXXX.      ",
                "   .XXXXXXXXXXXXX.      ",
                "    .XXXXXXXXXXX.       ",
                "    .XXXXXXXXXXX.       ",
                "     .XXXXXXXXX.        ",
                "     .XXXXXXXXX.        ",
                "     ...........        "]

click_cursor_data = ((24, 24), (7, 1), *cursors.compile(click_cursor))


class Menu:
    def __init__(self, button_param, x, y, w, h, ):
        # # button_list <row>, <func>, <text>
        #
        # V_SPACE = 5
        #
        # BUTTON_W = 400
        # BUTTON_H = 40
        #
        # ROWS = max([button[0] for button in button_param])
        #
        # SET_H = ROWS * (BUTTON_H + V_SPACE) - V_SPACE
        # SET_W = BUTTON_W
        #
        # X_OFFSET = x + w // 2 - SET_W // 2
        # Y_OFFSET = y + h // 2 - SET_H // 2
        #
        # ROW = 0
        # FUNCTION = 1
        # TEXT = 2
        #
        # self.button_list = []
        #
        # for button_index in range(len(button_param)):
        #     button_x = X_OFFSET
        #     button_y = Y_OFFSET + button_param[button_index][ROW] * (BUTTON_H + V_SPACE)
        #
        #     func = button_param[button_index][FUNCTION]
        #     text = button_param[button_index][TEXT]
        #
        #     self.button_list.append(Button(button_x, button_y, BUTTON_W, BUTTON_H, func, text))

        row_num = max([button_row for button_row, *trash in button_param])

        group_w = 400
        group_h = row_num * 50 - 10

        group_x = x + w // 2 - group_w // 2
        group_y = y + h // 2 - group_h // 2

        self.button_list = []

        sorted_button_param = [[button for button in button_param if button[0] == row] for row in range(row_num + 1)]

        for button_row in range(len(sorted_button_param)):
            if sorted_button_param[button_row]:
                b_w = int(group_w / len(sorted_button_param[button_row]) - 10)
                b_h = 40
                b_y = group_y + ((b_h + 10) * button_row)

                for button_index in range(len(sorted_button_param[button_row])):
                    b_x = group_x + ((b_w + 10) * button_index)

                    func = sorted_button_param[button_row][button_index][1]
                    text = sorted_button_param[button_row][button_index][2]

                    self.button_list.append(Button(b_x, b_y, b_w, b_h, func, text))

    def update(self, surf, release, mx, my, m_press):
        hover_over_button = False

        for button in self.button_list:
            nav_update = button.update(surf, mx, my, m_press, 15, release)

            if nav_update is not None:
                return nav_update

            if button.rect.collidepoint(mx, my):
                hover_over_button = True

        if hover_over_button:
            mouse.set_cursor(*click_cursor_data)

        else:
            mouse.set_cursor(*cursors.tri_left)


class TextBox:
    def __init__(self, x, y, w, h, label):
        self.rect = Rect(x, y, w, h)
        self.content = ""
        self.font = font.Font("fonts/minecraft.ttf", 14)
        self.label = self.font.render(label, True, (255, 255, 255))
        self.name = label
        self.charwidth = self.font.render("X", True, (255, 255, 255)).get_width()

        self.allowed = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                        't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                        'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'A', 'Y', 'Z', '0', '1', '2', '3', '4',
                        '5', '6', '7', '8', '9', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.',
                        '/', ' ', ':', ';', '<', '=', '>', '?', '@', '[', ']', '^', '_', '`', '{', '|', '}', '~', "'",
                        "'"]

    def draw(self, surf, selected):

        surf.blit(self.label, (self.rect.x, self.rect.y - self.label.get_height() - 2))

        draw.rect(surf, (0, 0, 0), self.rect)
        draw.rect(surf, (151, 151, 151), self.rect, 2)

        if self.name == 'Password':
            text = '*' * len(self.content)
        else:
            text = self.content

        surf.blit(self.font.render(text, True, (255, 255, 255)), (self.rect.x + 10, self.rect.y + 15))

        if selected == self.name:
            draw.rect(surf, (255, 255, 255), self.rect, 2)

    def update(self, e):

        if e and e.type == KEYDOWN:
            if e.unicode in self.allowed and len(self.content) < self.rect.w//self.charwidth - 1:
                self.content += e.unicode

            elif e.key == K_BACKSPACE:
                try:
                    self.content = self.content[:-1]
                except IndexError:
                    pass

        return self.content


class ServerButton:
    def __init__(self, x, y, w, h, title, host, port, motd, strength):
        self.rect = Rect(x, y, w, h)
        self.title = title
        self.host = host
        self.port = port
        self.motd = motd
        self.strength = strength

        self.do_not_destroy = ['Rahmish Imperial', 'Localhost']

    def draw_button(self, surf, inner, outer):
        draw.rect(surf, outer, self.rect)
        draw.rect(surf, inner, (self.rect.x + 2, self.rect.y + 2, self.rect.w - 4, self.rect.h - 4))

    def highlight(self, surf):
        self.draw_button(surf, (40, 40, 40), (250, 250, 250))

    def mouse_down(self, surf):
        self.draw_button(surf, (10, 10, 10), (250, 250, 250))

    def idle(self, surf):
        self.draw_button(surf, (20, 20, 20), (250, 250, 250))

    def update(self, surf, mx, my, m_press, release, right_release, size):
        if self.rect.collidepoint(mx, my):
            if m_press[0]:
                self.mouse_down(surf)

            elif release and my < size[1] - 80:
                mouse.set_cursor(*cursors.tri_left)

                rah.load_sound(['sound/random/click.ogg'])

                return ['game', self.host, self.port]


            elif right_release and my < size[1] - 80:
                if self.title not in self.do_not_destroy:
                    return ['remove', self.title, self.host, self.port]
                else:
                    return ['remove fail']

            else:
                self.highlight(surf)
        else:
            self.idle(surf)

        title_text_surf = rah.text(self.title, 20)
        surf.blit(title_text_surf, (self.rect.x + 10, self.rect.y + 10))

        connection_text_surf = rah.text("%s:%i" % (self.host, self.port), 15)
        surf.blit(connection_text_surf, (self.rect.x + 10, self.rect.y + 50))

        motd_text_surf = rah.text("%s" % (self.motd), 12)
        surf.blit(motd_text_surf, (self.rect.x + 10, self.rect.y + 34))

        if self.host == 'rahmish.com':
            special_text_surf = rah.text("Verified Rahmish Server", 12)
            surf.blit(special_text_surf,
                      (self.rect.x + self.rect.w - special_text_surf.get_width() - 10, self.rect.y + 50))

        signal_strength = self.strength//100

        for bar in range(5):
            if bar == 4 and signal_strength >= 5:
                colour = (255, 0, 0)
            elif bar >= signal_strength:
                if signal_strength > 2:
                    colour = (200, 255, 0)
                else:
                    colour = (0, 255, 0)
            else:
                colour = (0, 0, 0)

            draw.rect(surf, colour, (self.rect.x + self.rect.w - 10 - bar * 5, self.rect.y + 25, 3, - 15 + bar * 2))

class ScrollingMenu:
    def __init__(self, button_param, x, y, w):
        # button_list <row>, <func>, <title>, <host>, <port>

        V_SPACE = 5

        BUTTON_W = 400
        BUTTON_H = 75

        ROWS = max([button[0] for button in button_param])

        SET_H = ROWS * (BUTTON_H + V_SPACE) - V_SPACE
        SET_W = BUTTON_W

        X_OFFSET = x + w // 2 - SET_W // 2
        Y_OFFSET = 50

        ROW = 0
        TITLE = 1
        HOST = 2
        PORT = 3
        MOTD = 4
        STRENGTH = 5

        self.button_list = []

        for button_index in range(len(button_param)):
            button_x = X_OFFSET
            button_y = Y_OFFSET + button_param[button_index][ROW] * (BUTTON_H + V_SPACE)

            title = button_param[button_index][TITLE]
            host = button_param[button_index][HOST]
            port = int(button_param[button_index][PORT])
            motd = button_param[button_index][MOTD]
            strength = int(button_param[button_index][STRENGTH])

            self.button_list.append(ServerButton(button_x, button_y, BUTTON_W, BUTTON_H, title, host, port, motd, strength))

    def update(self, surf, release, right_release, mx, my, m_press, y_offset, size):

        click_cursor_data = ((24, 24), (7, 1), *cursors.compile(click_cursor))

        hover_over_button = False

        for button in self.button_list:
            nav_update = button.update(surf, mx, my, m_press, release, right_release, size)

            button.rect.y = y_offset + self.button_list.index(button) * (button.rect.h + 5)

            if nav_update is not None:
                return nav_update

            if button.rect.collidepoint(mx, my):
                hover_over_button = True

        if hover_over_button:
            mouse.set_cursor(*click_cursor_data)

        else:
            mouse.set_cursor(*cursors.tri_left)


class Window:
    def __init__(self, x, y, w, h):
        pass


class Inventory:
    def __init__(self, x, y, w, h):
        self.graphic = image.load('textures/gui/inventory.png')
        self.x, self.y = w // 2 - self.graphic.get_width() // 2, h // 2 - self.graphic.get_height() // 2
        self.w, self.h = w, h
        self.highlight = Surface((32, 32))
        self.highlight.fill((255, 255, 255))
        self.highlight.set_alpha(150)
        self.item_slots = []
        self.holding = [0, 0]

        self.recipes = json.load(open("data/tucrafting.json"))

        self.crafting_grid = [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]
        self.result = [0, 0]

    def recipe_check(self):
        current_recipe = [self.crafting_grid[x][y][0] for x in range(2) for y in range(2)]
        current_recipe = " ".join(list(map(str, current_recipe)))

        if current_recipe in self.recipes:
            self.resulting_item = [self.recipes[current_recipe]['result'], self.recipes[current_recipe]['quantity']]
        else:
            self.resulting_item = [0, 0]

    def craft(self, item_lib):
        if self.resulting_item != [0, 0]:
            if self.holding[0] == 0:
                self.holding = self.resulting_item
                for x in range(len(self.crafting_grid)):
                    for y in range(2):
                        if self.crafting_grid[x][y][0] != 0:
                            if self.crafting_grid[x][y][1] == 1:
                                self.crafting_grid[x][y] = [0, 0]
                            else:
                                self.crafting_grid[x][y][1] -= 1

            elif self.holding[0] == self.resulting_item[0] and self.holding[1] + self.resulting_item[1] <= item_lib[self.holding[0]][-1]:
                self.holding[1] += self.resulting_item[1]
                for x in range(len(self.crafting_grid)):
                    for y in range(2):
                        if self.crafting_grid[x][y][0] != 0:
                            if self.crafting_grid[x][y][1] == 1:
                                self.crafting_grid[x][y] = [0, 0]
                            else:
                                self.crafting_grid[x][y][1] -= 1

    def check_stacking(self, item, item_lib):
        if self.holding[0] != item[0] or item[1] == item_lib[item[0]][-1]:
            previous_holding = self.holding[:]
            self.holding = item[:]
            return previous_holding

        else:
            calculate_stack = item_lib[item[0]][-1] - self.holding[1] - item[1]
            amount_holding = self.holding[1]

            if calculate_stack >= 0:
                self.holding = [0, 0]
                return [item[0], item[1] + amount_holding]
            else:
                self.holding = [item[0], abs(calculate_stack)]
                return [item[0], item_lib[item[0]][-1]]

    def single_add(self, inv, item_lib):
        if self.holding[0] != 0 and inv[1] < item_lib[self.holding[0]][-1]:
            if self.holding[0] == inv[0] or inv[0] == 0:
                inv[0] = self.holding[0]
                self.holding[1] -= 1
                inv[1] += 1

        elif self.holding[0] == 0:
            half = inv[1] // 2

            self.holding = [inv[0], half]
            inv[1] -= half

        if self.holding[1] == 0:
            self.holding = [0, 0]

        return inv

    def update(self, surf, mx, my, m_press, l_click, r_click, inventory, hotbar, item_lib):
        surf.blit(self.graphic, (self.x, self.y))

        for row in range(len(inventory)):
            for item in range(len(inventory[row])):
                if inventory[row][item][1] != 0:
                    surf.blit(item_lib[inventory[row][item][0]][1], (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))
                    surf.blit(rah.text(str(inventory[row][item][1]), 10), (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

                if Rect((self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32)).collidepoint(mx, my):
                    surf.blit(self.highlight, (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

                    if l_click:
                        inventory[row][item] = self.check_stacking(inventory[row][item][:], item_lib)
                    elif r_click:
                        inventory[row][item] = self.single_add(inventory[row][item][:], item_lib)

        for item in range(len(hotbar)):
            if hotbar[item][1] != 0:
                surf.blit(item_lib[hotbar[item][0]][1], (self.x + 16 + item * 36, self.y + 283, 32, 32))
                surf.blit(rah.text(str(hotbar[item][1]), 10), (self.x + 16 + item * 36, self.y + 283, 32, 32))

            if Rect((self.x + 16 + item * 36, self.y + 283, 32, 32)).collidepoint(mx, my):
                surf.blit(self.highlight, (self.x + 16 + item * 36, self.y + 283, 32, 32))

                if l_click:
                    hotbar[item] = self.check_stacking(hotbar[item][:], item_lib)
                elif r_click:
                    hotbar[item] = self.single_add(hotbar[item][:], item_lib)

        for row in range(len(self.crafting_grid)):
            for item in range(len(self.crafting_grid[row])):
                if self.crafting_grid[row][item][1] != 0:
                    surf.blit(item_lib[self.crafting_grid[row][item][0]][1], (self.w//2 + 19 + 36 * item, self.h//2 - 130 + 36 * row, 32, 32))
                    surf.blit(rah.text(str(self.crafting_grid[row][item][1]), 10), (self.w//2 + 19 + 36 * item, self.h//2 - 130 + 36 * row, 32, 32))

                if Rect((self.w//2 + 19 + 36 * item, self.h//2 - 130 + 36 * row, 32, 32)).collidepoint(mx, my):
                    surf.blit(self.highlight, (self.w//2 + 19 + 36 * item, self.h//2 - 130 + 36 * row, 32, 32))
                    if l_click:
                        self.crafting_grid[row][item] = self.check_stacking(self.crafting_grid[row][item][:], item_lib)
                    elif r_click:
                        self.crafting_grid[row][item] = self.single_add(self.crafting_grid[row][item][:], item_lib)

        self.recipe_check()

        if self.resulting_item[0] != 0:
            surf.blit(item_lib[self.resulting_item[0]][1], (self.w//2 + 131, self.h//2 - 110, 32, 32))
            surf.blit(rah.text(str(self.resulting_item[1]), 10), (self.w//2 + 131, self.h//2 - 110, 32, 32))

            if Rect((self.w//2 + 131, self.h//2 - 110, 32, 32)).collidepoint(mx, my) and l_click:
                self.craft(item_lib)

        if self.holding[0] > 0:
            surf.blit(item_lib[self.holding[0]][1], (mx - 10, my - 10))
            surf.blit(rah.text(str(self.holding[1]), 10), (mx - 10, my - 10))


class Crafting:
    def __init__(self, w, h):
        self.graphic = image.load('textures/gui/crafting_table.png').convert_alpha()
        self.x, self.y = w // 2 - self.graphic.get_width() // 2, h // 2 - self.graphic.get_height() // 2
        self.w, self.h = w, h
        self.highlight = Surface((32, 32))
        self.highlight.fill((255, 255, 255))
        self.highlight.set_alpha(150)
        self.holding = [0, 0]

        self.crafting_grid = [[[0, 0] for _ in range(3)] for __ in range(3)]
        self.recipes = json.load(open('data/crafting.json'))

        rah.rahprint(self.recipes)

        self.current_recipe = []
        self.resulting_item = [0, 0]

    def recipe_check(self):
        current_recipe = [self.crafting_grid[x][y][0] for x in range(3) for y in range(3)]
        current_recipe = " ".join(list(map(str, current_recipe)))
        if current_recipe in self.recipes:
            self.resulting_item = [self.recipes[current_recipe]['result'], self.recipes[current_recipe]['quantity']]

        else:
            self.resulting_item = [0, 0]

    def craft(self, item_lib):
        if self.resulting_item != [0, 0]:
            if self.holding[0] == 0:
                self.holding = self.resulting_item
                for x in range(len(self.crafting_grid)):
                    for y in range(3):
                        if self.crafting_grid[x][y][0] != 0:
                            if self.crafting_grid[x][y][1] == 1:
                                self.crafting_grid[x][y] = [0, 0]
                            else:
                                self.crafting_grid[x][y][1] -= 1
            elif self.holding[0] == self.resulting_item[0] and self.holding[1] + self.resulting_item[1] <= item_lib[self.holding[0]][-1]:
                self.holding[1] += self.resulting_item[1]
                for x in range(len(self.crafting_grid)):
                    for y in range(3):
                        if self.crafting_grid[x][y][0] != 0:
                            if self.crafting_grid[x][y][1] == 1:
                                self.crafting_grid[x][y] = [0, 0]
                            else:
                                self.crafting_grid[x][y][1] -= 1

            # self.holding = self.recipes[" ".join(list(map(str, [self.crafting_grid[x][y][0] for x in range(3) for y in range(3)])))][:]

    def check_stacking(self, item, item_lib):
        if self.holding[0] != item[0] or item[1] == item_lib[item[0]][-1]:
            previous_holding = self.holding[:]
            self.holding = item[:]
            return previous_holding
        else:
            calculate_stack = item_lib[item[0]][-1] - self.holding[1] - item[1]
            amount_holding = self.holding[1]

            if calculate_stack >= 0:
                self.holding = [0, 0]
                return [item[0], item[1] + amount_holding]
            else:
                self.holding = [item[0], abs(calculate_stack)]
                return [item[0], item_lib[item[0]][-1]]

    def single_add(self, inv, item_lib):
        if self.holding[0] != 0 and inv[1] < item_lib[self.holding[0]][-1]:
            if self.holding[0] == inv[0] or inv[0] == 0:
                inv[0] = self.holding[0]
                self.holding[1] -= 1
                inv[1] += 1

        elif self.holding[0] == 0:
            half = inv[1] // 2

            self.holding = [inv[0], half]
            inv[1] -= half

        if self.holding[1] == 0:
            self.holding = [0, 0]

        return inv

    def update(self, surf, mx, my, m_press, l_click, r_click, inventory, hotbar, item_lib):
        surf.blit(self.graphic, (self.x, self.y))

        for row in range(len(inventory)):
            for item in range(len(inventory[row])):
                if inventory[row][item][1] != 0:
                    surf.blit(item_lib[inventory[row][item][0]][1],
                              (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

                    surf.blit(rah.text(str(inventory[row][item][1]), 10),
                              (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

                if Rect((self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32)).collidepoint(mx, my):
                    surf.blit(self.highlight, (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

                    if l_click:
                        inventory[row][item] = self.check_stacking(inventory[row][item][:], item_lib)
                    elif r_click:
                        inventory[row][item] = self.single_add(inventory[row][item][:], item_lib)

        for item in range(len(hotbar)):
            if hotbar[item][1] != 0:
                surf.blit(item_lib[hotbar[item][0]][1], (self.x + 16 + item * 36, self.y + 283, 32, 32))

                surf.blit(rah.text(str(hotbar[item][1]), 10), (self.x + 16 + item * 36, self.y + 283, 32, 32))

            if Rect((self.x + 16 + item * 36, self.y + 283, 32, 32)).collidepoint(mx, my):
                surf.blit(self.highlight, (self.x + 16 + item * 36, self.y + 283, 32, 32))

                if l_click:
                    hotbar[item] = self.check_stacking(hotbar[item][:], item_lib)
                elif r_click:
                    hotbar[item] = self.single_add(hotbar[item][:], item_lib)

        for row in range(len(self.crafting_grid)):
            for item in range(3):
                if self.crafting_grid[row][item][1] != 0:
                    surf.blit(item_lib[self.crafting_grid[row][item][0]][1],
                              (self.x + item * 36 + 60, self.y + 36 * row + 33, 32, 32))

                    surf.blit(rah.text(str(self.crafting_grid[row][item][1]), 10),
                              (self.x + item * 36 + 60, self.y + 36 * row + 33, 32, 32))

                if Rect((self.x + item * 36 + 60, self.y + 36 * row + 33, 32, 32)).collidepoint(mx, my):
                    surf.blit(self.highlight, (self.x + item * 36 + 60, self.y + 36 * row + 34, 32, 32))

                    if l_click:
                        self.crafting_grid[row][item] = self.check_stacking(self.crafting_grid[row][item][:], item_lib)
                    elif r_click:
                        self.crafting_grid[row][item] = self.single_add(self.crafting_grid[row][item][:], item_lib)

        self.recipe_check()

        if self.resulting_item[0] != 0:
            surf.blit(transform.scale(item_lib[self.resulting_item[0]][1], (48, 48)), (self.w//2 + 63, self.h//2 - 104, 48, 48))
            surf.blit(rah.text(str(self.resulting_item[1]), 10), (self.w//2 + 63, self.h//2 - 104, 48, 48))

        if Rect((463, 146, 48, 48)).collidepoint(mx, my):
            surf.blit(rah.text(str(self.resulting_item[1]), 10), (463, 146, 48, 48))

            if l_click:
                self.craft(item_lib)

        if self.holding[0] > 0:
            surf.blit(item_lib[self.holding[0]][1], (mx - 10, my - 10))
            surf.blit(rah.text(str(self.holding[1]), 10), (mx - 10, my - 10))


class Chest:
    def __init__(self, x, y, w, h):

        self.graphic = image.load('textures/gui/small_chest.png')

        self.x, self.y = w // 2 - self.graphic.get_width() // 2, h // 2 - self.graphic.get_height() // 2
        self.w, self.h = w, h

        self.highlight = Surface((32, 32))
        self.highlight.fill((255, 255, 255))
        self.highlight.set_alpha(150)
        self.item_slots = []
        self.holding = [0, 0]

    def check_stacking(self, item, item_lib):
        if self.holding[0] != item[0] or item[1] == item_lib[item[0]][-1]:
            previous_holding = self.holding[:]
            self.holding = item[:]
            return previous_holding
        else:
            calculate_stack = item_lib[item[0]][-1] - self.holding[1] - item[1]
            amount_holding = self.holding[1]

            if calculate_stack >= 0:
                self.holding = [0, 0]
                return [item[0], item[1] + amount_holding]
            else:
                self.holding = [item[0], abs(calculate_stack)]
                return [item[0], item_lib[item[0]][-1]]

    def single_add(self, inv, item_lib):
        if self.holding[0] != 0 and inv[1] < item_lib[self.holding[0]][-1]:
            if self.holding[0] == inv[0] or inv[0] == 0:
                inv[0] = self.holding[0]
                self.holding[1] -= 1
                inv[1] += 1

        elif self.holding[0] == 0:
            half = inv[1] // 2

            self.holding = [inv[0], half]
            inv[1] -= half

        if self.holding[1] == 0:
            self.holding = [0, 0]

        return inv

    def update(self, surf, mx, my, m_press, l_click, r_click, inventory, hotbar, chest_inv, item_lib):
        surf.blit(self.graphic, (self.x, self.y))

        for row in range(len(chest_inv)):
            for item in range(len(chest_inv[row])):
                if chest_inv[row][item][1] != 0:
                surf.blit(item_lib[chest_inv[row][item][0]][1],
                          (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

                surf.blit(rah.text(str(chest_inv[row][item][1]), 10),
                          (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

            if Rect((self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32)).collidepoint(mx, my):
                surf.blit(self.highlight, (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

                if l_click:
                    chest_inv[row][item] = self.check_stacking(chest_inv[row][item][:], item_lib)
                elif r_click:
                    chest_inv[row][item] = self.single_add(chest_inv[row][item][:], item_lib)

        for row in range(len(inventory)):
            for item in range(len(inventory[row])):
                if inventory[row][item][1] != 0:
                    surf.blit(item_lib[inventory[row][item][0]][1],
                              (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

                    surf.blit(rah.text(str(inventory[row][item][1]), 10),
                              (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

                if Rect((self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32)).collidepoint(mx, my):
                    surf.blit(self.highlight, (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

                    if l_click:
                        inventory[row][item] = self.check_stacking(inventory[row][item][:], item_lib)
                    elif r_click:
                        inventory[row][item] = self.single_add(inventory[row][item][:], item_lib)

        for item in range(len(hotbar)):
            if hotbar[item][1] != 0:
                surf.blit(item_lib[hotbar[item][0]][1], (self.x + 16 + item * 36, self.y + 283, 32, 32))

                surf.blit(rah.text(str(hotbar[item][1]), 10), (self.x + 16 + item * 36, self.y + 283, 32, 32))

            if Rect((self.x + 16 + item * 36, self.y + 283, 32, 32)).collidepoint(mx, my):
                surf.blit(self.highlight, (self.x + 16 + item * 36, self.y + 283, 32, 32))

                if l_click:
                    hotbar[item] = self.check_stacking(hotbar[item], item_lib)

        if self.holding[0] > 0:
            surf.blit(item_lib[self.holding[0]][1], (mx - 10, my - 10))
