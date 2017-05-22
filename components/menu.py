import components.rahma as rah
from pygame import *

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
                # mixer.Sound('sound/random/click.ogg').play()

                return self.func

            else:
                self.highlight(surf)
        else:
            self.idle(surf)

        text_surf = rah.text(self.text, size)
        surf.blit(text_surf, rah.center(*self.rect, text_surf.get_width(), text_surf.get_height()))


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


class Menu:
    def __init__(self, button_param, x, y, w, h):
        # button_list <row>, <func>, <text>

        V_SPACE = 5

        BUTTON_W = 400
        BUTTON_H = 40

        ROWS = max([button[0] for button in button_param])

        SET_H = ROWS * (BUTTON_H + V_SPACE) - V_SPACE
        SET_W = BUTTON_W

        X_OFFSET = x + w // 2 - SET_W // 2
        Y_OFFSET = y + h // 2 - SET_H // 2

        ROW = 0
        FUNCTION = 1
        TEXT = 2

        self.button_list = []

        for button_index in range(len(button_param)):
            button_x = X_OFFSET
            button_y = Y_OFFSET + button_param[button_index][ROW] * (BUTTON_H + V_SPACE)

            func = button_param[button_index][FUNCTION]
            text = button_param[button_index][TEXT]

            self.button_list.append(Button(button_x, button_y, BUTTON_W, BUTTON_H, func, text))

    def update(self, surf, release, mx, my, m_press):

        click_cursor_data = ((24, 24), (7, 1), *cursors.compile(click_cursor))

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

        self.allowed = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                        't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                        'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'A', 'Y', 'Z', '0', '1', '2', '3', '4',
                        '5', '6', '7', '8', '9', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.',
                        '/', ' ', ':', ';', '<', '=', '>', '?', '@', '[', ']', '^', '_', '`', '{', '|', '}', '~', "'",
                        "'"]

    def draw(self, surf):
        surf.blit(self.label, (self.rect.x, self.rect.y - self.label.get_height() - 2))

        draw.rect(surf, (0, 0, 0), self.rect)
        draw.rect(surf, (151, 151, 151), self.rect, 2)

        if self.name == 'Password':
            text = '*' * len(self.content)
        else:
            text = self.content

        surf.blit(self.font.render(text, True, (255, 255, 255)), (self.rect.x + 10, self.rect.y + 15))

    def update(self, e):
        if e and e.type == KEYDOWN:
            if e.unicode in self.allowed and len(self.content) < 35:
                self.content += e.unicode

            elif e.key == K_BACKSPACE:
                try:
                    self.content = self.content[:-1]
                except IndexError:
                    pass

        return self.content


class ServerButton:
    def __init__(self, x, y, w, h, title, host, port):
        self.rect = Rect(x, y, w, h)
        self.title = title
        self.host = host
        self.port = port

    def draw_button(self, surf, inner, outer):
        draw.rect(surf, outer, self.rect)
        draw.rect(surf, inner, (self.rect.x + 2, self.rect.y + 2, self.rect.w - 4, self.rect.h - 4))

    def highlight(self, surf):
        self.draw_button(surf, (40, 40, 40), (250, 250, 250))

    def mouse_down(self, surf):
        self.draw_button(surf, (10, 10, 10), (250, 250, 250))

    def idle(self, surf):
        self.draw_button(surf, (20, 20, 20), (250, 250, 250))

    def update(self, surf, mx, my, m_press, release):
        if self.rect.collidepoint(mx, my):
            if m_press[0]:
                self.mouse_down(surf)

            elif release:
                mouse.set_cursor(*cursors.tri_left)

                return ['game', self.host, self.port]

            else:
                self.highlight(surf)
        else:
            self.idle(surf)

        title_text_surf = rah.text(self.title, 20)
        surf.blit(title_text_surf, (self.rect.x + 10, self.rect.y + 10))

        connection_text_surf = rah.text("%s:%i" % (self.host, self.port), 15)
        surf.blit(connection_text_surf, (self.rect.x + 10, self.rect.y + 32))

        if self.host == 'rahmish.com':
            special_text_surf = rah.text("Verified Rahmish Server", 12)
            surf.blit(special_text_surf,
                      (self.rect.x + self.rect.w - special_text_surf.get_width() - 10, self.rect.y + 34))


class ScrollingMenu:
    def __init__(self, button_param, x, y, w, h):
        # button_list <row>, <func>, <title>, <host>, <port>

        V_SPACE = 5

        BUTTON_W = 400
        BUTTON_H = 60

        ROWS = max([button[0] for button in button_param])

        SET_H = ROWS * (BUTTON_H + V_SPACE) - V_SPACE
        SET_W = BUTTON_W

        X_OFFSET = x + w // 2 - SET_W // 2
        Y_OFFSET = y + h // 2 - SET_H // 2

        ROW = 0
        TITLE = 1
        HOST = 2
        PORT = 3

        self.button_list = []

        for button_index in range(len(button_param)):
            button_x = X_OFFSET
            button_y = Y_OFFSET + button_param[button_index][ROW] * (BUTTON_H + V_SPACE)

            title = button_param[button_index][TITLE]
            host = button_param[button_index][HOST]
            port = int(button_param[button_index][PORT])

            self.button_list.append(ServerButton(button_x, button_y, BUTTON_W, BUTTON_H, title, host, port))

    def update(self, surf, release, mx, my, m_press):
        click_cursor_data = ((24, 24), (7, 1), *cursors.compile(click_cursor))

        hover_over_button = False

        for button in self.button_list:
            nav_update = button.update(surf, mx, my, m_press, release)

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
        self.item_slots = []

    def update(self, surf, mx, my, m_press, inventory, hotbar, block_properties):
        surf.blit(self.graphic, (self.x, self.y))

        for row in range(len(inventory)):
            for item in range(len(inventory[row])):

                elif inventory[row][item][1] != 0:
                    surf.blit(transform.scale(block_properties[inventory[row][item][0]][3], (32, 32)),
                              (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

                    surf.blit(rah.text(str(inventory[row][item][1]), 10),
                              (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

        for item in range(len(hotbar)):
            if hotbar[item][1] != 0:
                surf.blit(transform.scale(block_properties[hotbar[item][0]][3], (32, 32)),
                          (self.x + 16 + item * 36, self.y + 283, 32, 32))

                surf.blit(rah.text(str(hotbar[item][1]), 10),
                          (self.x + 16 + item * 36, self.y + 283, 32, 32))


class Crafting:
    def __init__(self, w, h):
        self.graphic = image.load('textures/gui/crafting_table.png').convert_alpha()
        self.x, self.y = w // 2 - self.graphic.get_width() // 2, h // 2 - self.graphic.get_height() // 2
        self.w, self.h = w, h

    def update(self, surf, mx, my, m_press, inventory, hotbar, block_properties):
        surf.blit(self.graphic, (self.x, self.y))

        for row in range(len(inventory)):
            for item in range(len(inventory[row])):

                if inventory[row][item][1] != 0:
                    surf.blit(transform.scale(block_properties[inventory[row][item][0]][3], (32, 32)),
                              (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

                    surf.blit(rah.text(str(inventory[row][item][1]), 10),
                              (self.x + 15 + item * 36, self.y + 168 + row * 36, 32, 32))

        for item in range(len(hotbar)):
            if hotbar[item][1] != 0:
                surf.blit(transform.scale(block_properties[hotbar[item][0]][3], (32, 32)),
                          (self.x + 16 + item * 36, self.y + 283, 32, 32))

                surf.blit(rah.text(str(hotbar[item][1]), 10),
                          (self.x + 16 + item * 36, self.y + 283, 32, 32))



