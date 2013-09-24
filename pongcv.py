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

class Vecteur():

    def __init__(self,x,y):
        self.x=x
        self.y=y

    def __init__(self):
        self.x=0
        self.y=0

    def normalise(self):
        norme=math.sqrt(self.x**2+self.y**2)
        self.x/=norme
        self.y/=norme

    def __str__(self):
        return str(self.x)+","+str(self.y)
class Point():
    def __init__(self,p):
        self.x=p[0]
        self.y=p[1]

    def __str__(self):
        return str(self.x)+","+str(self.y)

def CalcCollision(a,b,c):
    if(CollisionDroite(a,b,c)==0):
        return 0

    AB=Vecteur()
    AC=Vecteur()
    BC=Vecteur()
    AB.x=b.x-a.x
    AB.y=b.y-a.y
    AC.x=c.centre[0]-a.x
    AC.y=c.centre[1]-a.y
    BC.x=c.centre[0]-b.x
    BC.y=c.centre[1]-b.y

    pscal1=AB.x*AC.x+AB.y*AC.y
    pscal2=-AB.x*BC.x-AB.y*BC.y

    if(pscal1>=0 and pscal2>=0):
        return 1

    if(CollisionPointCercle(a,c)==1):
        return 1

    if(CollisionPointCercle(b,c)==1):
        return 1


    return 0

def CalculRebond(v1, N):
    v=Vecteur()
    v.x=v1[0]
    v.y=v1[1]
    pscal=v.x*N.x+v.y*N.y
    v2=Vecteur()
    v2.x=float(v.x-2*pscal*N.x)
    v2.y=float(v.y-2*pscal*N.y)
    return [v2.x,v2.y]

def GetNormal(a,b,c):
    AC=Vecteur()
    u=Vecteur()
    N=Vecteur()

    u.x=b.x-a.x
    u.y=b.y-a.y
    AC.x=c.centre[0]-a.x
    AC.y=c.centre[1]-a.y

    coeff=u.x*AC.y-u.y*AC.x
    N.x=-u.y*coeff
    N.y=u.x*coeff

    norme=math.sqrt(float(N.x)**2+float(N.y)**2)

    N.x/=norme
    N.y/=norme

    return N

def CollisionPointCercle(pt,c):
    test=0
    x=pt.x
    y=pt.y
    d=(x-c.centre[0])**2+(y-c.centre[1])**2
    if(d>c.r**2):
        test=0
    else:
        test=1
    return test

def CollisionDroite(a,b,c):
    Ux=b.x-a.x
    Uy=b.y-a.y
    ACx=c.centre[0]-a.x
    ACy=c.centre[1]-a.y
    num=Ux*ACy-Uy*ACx
    if(num<0):
        num=-num

    denom=math.sqrt(Ux**2+Uy**2)
    ci=num/denom
    if(ci<c.r):
        return 1

    return 0


class Ball:
    def __init__(self):
        self.ball=pygame.image.load('Ball.png').convert()
        self.pos=[10,10]
        self.width=self.ball.get_width()
        self.height=self.ball.get_height()
        self.r=self.width/2
        self.centre=[(self.pos[0]+self.width/2),(self.pos[1]+self.height/2)]
        self.v=[5,5]

    def move(self):
        if (self.pos[0]<=0) or ((self.pos[0]+self.width)>=640):
            self.v[0]=-self.v[0]
        if (self.pos[1]<=0) or (self.pos[1]+self.height>=480):
            self.v[1]=-self.v[1]

        self.pos[0]+=self.v[0]
        self.pos[1]+=self.v[1]
        self.centre=[(self.pos[0]+self.width/2),(self.pos[1]+self.height/2)]
        return self.ball.get_rect().move(self.pos[0],self.pos[1])

    def getImage(self):
        return self.ball


def Collision(box1,box2):
    if((box2.x>=box1.x+box1.width)or
    (box2.x+box2.width<box1.x)or
    (box2.y>=box1.y+box1.height)or
    (box2.y+box2.height<=box1.y)):
        return False
    else:
        return True

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    ball = Ball()
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Bin")
    while 1:
        result, img = cam.read()
        #img=cv2.imread("IMG_1931.JPG")

        greyimg=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        gray = cv2.GaussianBlur(greyimg,(5,5),0)
        normImage = cv2.adaptiveThreshold(gray,255,1,1,11,2)
        # Operation de Morphologie pour limiter le bruit de la Webcam
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))
        imgMorph=cv2.dilate(normImage,kernel)
        cv2.imshow("Bin",gray)

        contours, hierarchy = cv2.findContours(imgMorph,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(img,contours,-1,(0,255,0),2)

        for cnt in contours:
            # On ne selectionne que les contours dont la surface est > ? 500 pixel pour
            # ne garder que l'objet principal
            if cv2.contourArea(cnt)>500:
                #On d?termine les 4 coins entourant la ligne
                approx = cv2.approxPolyDP(cnt,10,True)
                rect=cv2.minAreaRect(cnt)
                box = cv2.cv.BoxPoints(rect)
                box = np.int0(box)

                #Pour chaque contour, on detecte le segment le plus long.
                #Ensuite, on determine le segment median qui va servir pour la collision.
                l1=math.sqrt((box[1][0]-box[0][0])**2+(box[1][1]-box[0][1])**2)
                l2=math.sqrt((box[2][0]-box[1][0])**2+(box[2][1]-box[1][1])**2)

                if(l1<l2):
                    pt1=Point([(box[1][0]+box[0][0])/2,(box[1][1]+box[0][1])/2])
                    pt2=Point([(box[2][0]+box[3][0])/2,(box[2][1]+box[3][1])/2])
                else:
                    pt1=Point([(box[0][0]+box[3][0])/2,(box[0][1]+box[3][1])/2])
                    pt2=Point([(box[2][0]+box[1][0])/2,(box[2][1]+box[1][1])/2])


                #Test de la collision et determination du nouveau vecteur vitesse
                if CalcCollision(pt1,pt2,ball):
                    n=GetNormal(pt1,pt2,ball)
                    ball.v=CalculRebond(ball.v,n)


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
