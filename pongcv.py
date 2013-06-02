#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Olivier
#
# Created:     14-05-2013
# Copyright:   (c) Olivier 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, sys
import cv2
import pygame
from PIL import Image
import numpy as np
import math

class Ball:
    def __init__(self):
        self.ball=pygame.image.load('Ball.png').convert()
        self.X=300
        self.Y=200
        self.V=20
        self.angle=45
        vx = self.V*math.cos(math.radians(self.angle))
        vy = self.V*math.sin(math.radians(self.angle))

    def move(self):

        x = self.X
        y = self.Y
        
        vx = self.V*math.cos(math.radians(self.angle))
        vy = self.V*math.sin(math.radians(self.angle))

        

        if ((x+vx)<=0) or ((x+vx)>=640):
            vx=-vx
            self.angle = math.degrees(math.atan2(vx,vy))
        if ((y+vy)<=0) or ((y+vy)>=480):
            vy=-vy
            self.angle = math.degrees(math.atan2(vx,vy))

        self.X += vx
        self.Y += vy
        
        
        print "Vx: "+str(vx)+"; Vy: "+str(vy)
        print "X: "+str(self.X)+"; y: "+str(self.Y)+"; t: "+str(self.angle)
        return self.ball.get_rect().move(self.X,self.Y)

    def getImage(self):
        return self.ball

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    ball = Ball()
    cam = cv2.VideoCapture(0)

    while 1:

        result, img = cam.read()
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        img = np.array(img)
        img = Image.fromarray(img)
        pg_img = pygame.image.frombuffer(img.tostring(), img.size, img.mode)
        pg_img = pg_img.convert()
        pg_img.blit(ball.getImage(),ball.move())
        screen.blit(pg_img, (0,0))
        pygame.display.flip()


if __name__ == '__main__':
    main()
