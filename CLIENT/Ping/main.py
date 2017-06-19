from pygame import *
from random import *

screen=display.set_mode((800,400))

running=True

bx = 400
by = 200
vx = -0.5
vy = randint(1,3)/10

p1y = 200
p2y = 200

while running:
    mx,my = mouse.get_pos()
    
    for evt in event.get():
        if evt.type==quit:
            running=False

    if vx>0:
        if by>p2y:
            p2y += 5
            
        elif by<p2y:
            p2y -= 5

    
    if vx<0:
        if by>p1y:
            p1y += 5
            
        elif by<p1y:
            p1y -= 5

    bx+=vx
    by+=vy

    p1rect = Rect(100,int(p1y-50),1,100)
    p2rect = Rect(700,int(p2y-50),1,100)
        
            
    screen.fill((0,0,0))

    draw.line(screen,(255,255,255),(400,0),(400,400),1)

    draw.circle(screen,(255,0,0),(int(bx),int(by)),10)

    draw.rect(screen,(255,255,255),p1rect)
    draw.rect(screen,(255,255,255),p2rect)

    if not 400>by>0:
        vy *= -randint(10, 11)/10

    if p1rect.collidepoint(bx,by):
        vx *= -randint(10, 11)/10


    if p2rect.collidepoint(bx,by):
        vx *= -randint(10, 11)/10


    display.flip() #Updates screen
quit() #Quits program
            
