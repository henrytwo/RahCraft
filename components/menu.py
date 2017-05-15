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

        self.allowed = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                        't', 'u',
                        'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                        'O', 'P',
                        'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'A', 'Y', 'Z', '0', '1', '2', '3', '4',
                        '5', '6', '7', '8', '9', '!', '"', '#', '$', '%', '&', "\\", "'", '(', ')', '*', '+', ',', '-',
                        '.', '/',
                        ':', ';', '<', '=', '>', '?', '@', '[', ']', '^', '_', '`', '{', '|', '}', '~', "'", "'"]

    def draw(self, screen):
        screen.blit(self.label, (self.rect.x, self.rect.y - self.label.get_height() - 2))

        draw.rect(screen, (0, 0, 0), self.rect)
        draw.rect(screen, (151, 151, 151), self.rect, 2)

        screen.blit(self.font.render(self.content, True, (255, 255, 255)), (self.rect.x + 10, self.rect.y + 15))

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
