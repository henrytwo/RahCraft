import rahma as rah
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

        text_surface = rah.text(self.text, (self.rect.x, self.rect.y), size)

        screen.blit(text_surface, rah.center(self.rect.x, self.rect.y, self.rect.w, self.rect.h, text_surface.get_width(), text_surface.get_height()))

class Menu:
    def __init__(self,button_param, x, y , w, h):
        # button_list <row>, <function>, <text>

        V_SPACE = 10

        BUTTON_W = 400
        BUTTON_H = 40

        ROWS = max([button[0] for button in button_param])

        SET_H = ROWS * (BUTTON_H + V_SPACE) - V_SPACE
        SET_W = BUTTON_W

        X_OFFSET = x + w//2 - SET_W // 2
        Y_OFFSET = y + h//2 - SET_H // 2

        ROW = 0
        FUNCTION = 1
        TEXT = 2

        self.button_list = []

        print(X_OFFSET, Y_OFFSET)


        for button_index in range(len(button_param)):
            button_x = X_OFFSET
            button_y = Y_OFFSET + button_param[button_index][ROW] * (BUTTON_H + V_SPACE)

            function = button_param[button_index][FUNCTION]
            text = button_param[button_index][TEXT]

            print(button_x, button_y, BUTTON_W, BUTTON_H, function, text)

            self.button_list.append(Button(button_x, button_y, BUTTON_W, BUTTON_H, function, text))


    def update(self, screen, release, mx, my, mb):
        for button in self.button_list:
            nav_update = button.update(screen, mx, my, mb, 15, release)

            if nav_update is not None:
                return nav_update