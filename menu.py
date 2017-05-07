
class Button:
    def __init__(self, x, y, w, h, function, text):
        self.rect = Rect(x, y, w, h)
        self.text = text
        self.function = function

    def highlight(self):
        button_hover = transform.scale(image.load("textures/menu/button_hover.png"), (self.rect.w, self.rect.h))
        screen.blit(button_hover, (self.rect.x, self.rect.y))

    def mouse_down(self):
        button_pressed = transform.scale(image.load("textures/menu/button_pressed.png"), (self.rect.w, self.rect.h))
        screen.blit(button_pressed, (self.rect.x, self.rect.y))

    def idle(self):
        button_idle = transform.scale(image.load("textures/menu/button_idle.png"), (self.rect.w, self.rect.h))
        screen.blit(button_idle, (self.rect.x, self.rect.y))

    def update(self, mx, my, mb, size, release):

        minecraft_font = font.Font("fonts/minecraft.ttf", size)

        if self.rect.collidepoint(mx, my):

            if mb[0] == 1:
                self.mouse_down()

            elif release:
                mouse.set_cursor(*cursors.tri_left)
                return self.function

            else:
                self.highlight()
        else:
            self.idle()

        text_surface = minecraft_font.render(self.text, True, (255, 255, 255))
        text_shadow = minecraft_font.render(self.text, True, (0, 0, 0))
        shadow_surface = Surface((text_surface.get_width(), text_surface.get_height()))
        shadow_surface.blit(text_shadow, (0, 0))
        shadow_surface.set_alpha(100)
        text_pos = center(self.rect.x, self.rect.y, self.rect.w, self.rect.h, text_surface.get_width(),
                          text_surface.get_height())
        screen.blit(text_shadow, (text_pos[0] + 2, text_pos[1] + 2))
        screen.blit(text_surface, text_pos)



class Menu:
    def __init__(self,button_param, x, y , w, h):
        # button_list <row>, <function>, <text>

        V_SPACE = 10

        BUTTON_W = 400
        BUTTON_H = 40

        ROWS = max([button[0] for button in button_param])

        SET_H = ROWS * (BUTTON_W + V_SPACE) - V_SPACE
        SET_W = BUTTON_W

        X_OFFSET = w - SET_W // 2
        Y_OFFSET = h - SET_H // 2

        ROW = 0
        FUNCTION = 1
        TEXT = 2

        self.button_list = []

        for button_index in range(len(button_param)):
            button_x = X_OFFSET + button_param[button_index][ROW] * BUTTON_W
            button_y = Y_OFFSET
            function = button_param[button_index][FUNCTION]
            text = button_param[button_index][TEXT]

            self.button_list.append(Button(button_x, button_y, BUTTON_W, BUTTON_H, function, text))


    def update(self):
        for button in self.button_list:
            nav_update = button.update(mx, my, mb, 15, release)

            if nav_update is not None:
                return nav_update