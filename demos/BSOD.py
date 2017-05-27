import pygame
import time

pygame.init()

monitor = pygame.display.Info()

screen = pygame.display.set_mode((monitor.current_w, monitor.current_h))#, pygame.FULLSCREEN, pygame.NOFRAME)

text = ["A problem has been detected and Rahcraft has been shutdown to prevent damage to your computer.",
        "",
        "RAHMA_IRQL_NOT_LES_OR_EQUAL",
        "",
        "If this is the first time you've seen this stop error screen, restart your computer, If this screen appears again, follow these steps:",
        "",
        "Check to make sure any new hardware or software is properly installed. If this is a new installation, ask your hardware or software manufacturer for any windows updates you might need.",
        "",
        "If problems continue, disable or remove any newly installed hardware or software. Disable BIOS memory options such as caching or shadowing. If you need to use Safe Mode to remove or disable components, restart your computer, press F8 to select Advanced Startup Options, and then select Safe Mode.",
        "",
        "Technical information:",
        "",
        "*** STOP: 0x00D1 (0x000000000000000000000000C,0x0000000000000000000000002,0x00000000000000000000000000,0x000000000000000000000F86B5A89)",
        "",
        "***  RAHMA.SYS - Address F86B5A89 base at F86B5000, DateStamp 3dd9919eb",
        "",
        "Collecting data for crash dump ...",
        "Initializing disk for crash dump ...",
        "Beginning dump of physical memory",
        "Dumping Physical memory to disk: 100",
        "Physical memory dump complete.",
        "Contact your system administrator or technical support group for further assistance."]

screen.fill((0, 0, 136))
current_line = 1

text_font = pygame.font.Font("fonts/LUCON.TTF", 20)
font_space = text_font.size(" ")

for line in text:
    current_x = 10

    for word in line.split():
        if current_x + text_font.size(word)[0] < monitor.current_w - 10:
            screen.blit(text_font.render(word, False, (255, 255, 255)), (current_x, font_space[1] * current_line))
            current_x += text_font.size(word)[0] + font_space[0]
        else:
            current_x = 10
            current_line += 1

    current_line += 1

pygame.display.update()

time.sleep(10)
quit()
