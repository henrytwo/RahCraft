from pygame import *
from random import *
import pickle

#Loads the world from pickle file
with open('world.pkl', 'rb') as f:
    world = pickle.load(f)
    
clock = time.Clock()

# ----- Pre-Gameloop Preparation
# Make the block size and block offset
block_size = 20
y_offset = 0
x_offset = 0

def draw_block(x,y,size,colour,colourIn):
    draw.rect(screen,colour,(x,y,block_size,block_size))
    draw.rect(screen,colourIn,(x,y,block_size,block_size),1)

# Create the game screen
display.set_caption("SquareRoot")
screen = display.set_mode((800, 500))

# ----- Gameloop
while True:

    for e in event.get():
        if e.type == QUIT:
            with open('world.pkl', 'wb') as f:
                pickle.dump(world, f)

            break

        '''
            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 4:
                    block_size += 4
                    
                elif e.button == 5:
                    block_size -= 4

         '''   

    else:
        display.set_caption("SquareRoot Beta v0.01 FPS: " + str(round(clock.get_fps(), 2)) + " X: " + str(x_offset//block_size) + " Y:" +str(y_offset//block_size) + " Size:" + str(block_size))

        keys = key.get_pressed()

        if keys[K_d]:
            x_offset += 80//block_size
        if keys[K_a]:
            x_offset -= 80//block_size


        if keys[K_w] and y_offset//block_size>0:
                y_offset -= 80//block_size
                
        if keys[K_s] and y_offset//block_size<75:
                y_offset += 80//block_size


        mb = mouse.get_pressed()

        mx,my = mouse.get_pos()

        if mb[0] == 1:
            world[((mx - block_size//2) + x_offset)//block_size][((my - block_size//2) + y_offset)//block_size] = " "

        if mb[1] == 1:
            world[((mx - block_size//2) + x_offset)//block_size][((my - block_size//2) + y_offset)//block_size] = "2"

        if mb[2] == 1:
            world[((mx - block_size//2) + x_offset)//block_size][((my - block_size//2) + y_offset)//block_size] = "3"

        # Clear the screen
        #screen.fill((30,144,255))
        for y in range(500):
            draw.line(screen,(max(30-y,0),max(144-y,100),max(255-y,100)),(0,y),(800,y))

        # Redraw the level onto the screen
        for x in range(0,800,block_size): #Render blocks
            for y in range(0,500,block_size):
                if world[(x+x_offset)//block_size][(y+y_offset)//block_size] == "1":
                    draw_block(x,y,block_size,(0,150,0),(0,100,0))

                elif world[(x+x_offset)//block_size][(y+y_offset)//block_size] == "2":
                    draw_block(x,y,block_size,(129,68,32),(99,38,12))

                elif world[(x+x_offset)//block_size][(y+y_offset)//block_size] == "3":
                    draw_block(x,y,block_size,(150,150,150),(100,100,100))


        clock.tick(120)
        display.update()
        continue

    break

display.quit()
raise SystemExit
