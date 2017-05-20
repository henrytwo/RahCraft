import components.rahma as rah
from pygame import *


class Button:
    def __init__(self, x, y, w, h, function, text):
        self.rect = Rect(x, y, w, h)
        self.text = text
        self.function = function

    def highlight(self, screen):
        button_hover = transform.scale(image.load("textures/menu/button_hover.png"), (self.rect.w, self.rect.h))
        screen.blit(button_hover, (self.rect.x, self.rect.y))

    def mouse_down(self, screen):
        button_pressed = transform.scale(image.load("textures/menu/button_pressed.png"), (self.rect.w, self.rect.h))
        screen.blit(button_pressed, (self.rect.x, self.rect.y))

    def idle(self, screen):
        button_idle = transform.scale(image.load("textures/menu/button_idle.png"), (self.rect.w, self.rect.h))
        screen.blit(button_idle, (self.rect.x, self.rect.y))

    def update(self, screen, mx, my, mb, size, release):

        if self.rect.collidepoint(mx, my):

            if mb[0] == 1:
                self.mouse_down(screen)

            elif release:
                mouse.set_cursor(*cursors.tri_left)
                #mixer.Sound('sound/random/click.ogg').play()

                return self.function

            else:
                self.highlight(screen)
        else:
            self.idle(screen)

        text_surface = rah.text(self.text, size)

        screen.blit(text_surface,
                    rah.center(self.rect.x, self.rect.y, self.rect.w, self.rect.h, text_surface.get_width(),
                               text_surface.get_height()))

class Menu:
    def __init__(self, button_param, x, y, w, h):
        # button_list <row>, <function>, <text>

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

            function = button_param[button_index][FUNCTION]
            text = button_param[button_index][TEXT]

            self.button_list.append(Button(button_x, button_y, BUTTON_W, BUTTON_H, function, text))

    def update(self, screen, release, mx, my, mb):

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

        hover_over_button = False

        for button in self.button_list:
            nav_update = button.update(screen, mx, my, mb, 15, release)

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
                        't', 'u',
                        'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                        'O', 'P',
                        'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'A', 'Y', 'Z', '0', '1', '2', '3', '4',
                        '5', '6', '7', '8', '9', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-',
                        '.', '/',' ',
                        ':', ';', '<', '=', '>', '?', '@', '[', ']', '^', '_', '`', '{', '|', '}', '~', "'", "'"]

    def draw(self, screen):
        screen.blit(self.label, (self.rect.x, self.rect.y - self.label.get_height() - 2))

        draw.rect(screen, (0, 0, 0), self.rect)
        draw.rect(screen, (151, 151, 151), self.rect, 2)

        if self.name == 'Password':
            text = '*' * len(self.content)
        else:
            text = self.content

        screen.blit(self.font.render(text, True, (255, 255, 255)), (self.rect.x + 10, self.rect.y + 15))

    def update(self, screen, mouse, e):
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

    def draw_button(self, screen, inner, outer):
        draw.rect(screen, outer, self.rect)
        draw.rect(screen, inner, (self.rect.x + 2, self.rect.y + 2, self.rect.w - 4, self.rect.h - 4))


    def highlight(self, screen):
        self.draw_button(screen, (40,40,40), (250,250,250))

    def mouse_down(self, screen):
        self.draw_button(screen, (10, 10, 10), (250, 250, 250))

    def idle(self, screen):
        self.draw_button(screen, (20, 20, 20),(250, 250, 250))

    def update(self, screen, mx, my, mb, release):

        if self.rect.collidepoint(mx, my):

            if mb[0] == 1:
                self.mouse_down(screen)

            elif release:
                mouse.set_cursor(*cursors.tri_left)

                return ['game', self.host, self.port]

            else:
                self.highlight(screen)
        else:
            self.idle(screen)

        title_text_surface = rah.text(self.title, 20)
        screen.blit(title_text_surface, (self.rect.x + 10, self.rect.y + 10))

        connection_text_surface = rah.text("%s:%i"%(self.host, self.port), 15)
        screen.blit(connection_text_surface, (self.rect.x + 10, self.rect.y + 32))

        if self.host == 'rahmish.com':
            special_text_surface = rah.text("Verified Rahmish Server", 12)
            screen.blit(special_text_surface, (self.rect.x + self.rect.w - special_text_surface.get_width() - 10, self.rect.y + 34))


class ScrollingMenu:
    def __init__(self, button_param, x, y, w, h):
        # button_list <row>, <function>, <title>, <host>, <port>

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

    def update(self, screen, release, mx, my, mb):

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

        hover_over_button = False

        for button in self.button_list:
            nav_update = button.update(screen, mx, my, mb, release)

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
        self.x, self.y = w//2 - self.graphic.get_width()//2, h//2 - self.graphic.get_height()//2

    def update(self, screen, mx, my, mb, inventory, hotbar):
        screen.blit(self.graphic, (self.x, self.y))

        for y in range(len(inventory)):
            for x in range(len(inventory[y])):
                draw.rect(screen, (255,0,0), (self.x + 15 + x * 36, self.y + 168 + y * 36, 32, 32), 2)

        for x in range(len(hotbar)):
            draw.rect(screen, (255,0,0), (self.x + 15 + x * 36, self.y + 282, 32, 32), 2)


