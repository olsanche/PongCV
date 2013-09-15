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
        print "CalcCollision(a,b,c)=1"
        print "a="+str(a)
        print "b="+str(b)
        print "c="+str(c.centre)
        return 1

    if(CollisionPointCercle(a,c)==1):
        print "CollisionPointCercle(a,c)=1"
        print "a="+str(a)
        print "centre="+str(c.centre)
        return 1

    if(CollisionPointCercle(b,c)==1):
        print "CollisionPointCercle(b,c)=1"
        print "b="+str(b)
        print "centre="+str(c.centre)
        return 1


    return 0

def CalculRebond(v1, N):
    v=Vecteur()
    v.x=v1[0]
    v.y=v1[1]
    pscal=v.x*N.x+v.y*N.y
    v2=Vecteur()
    v2.x=v.x-2*pscal*N.x
    v2.y=v.y-2*pscal*N.y
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
        self.centre=[self.pos[0]+self.ball.get_width()/2,
        self.pos[1]+self.ball.get_height()/2]
        self.r=self.ball.get_width()/2
        print "R="+str(self.r)
        self.v=[5,5]

    def move(self):
        if (self.centre[0]<=0) or (self.centre[0]>=640):
            self.v[0]=-self.v[0]
        if (self.centre[1]<=0) or (self.centre[1]>=480):
            self.v[1]=-self.v[1]

        self.centre[0]+=self.v[0]
        self.centre[1]+=self.v[1]
        self.pos[0]+=self.v[0]
        self.pos[1]+=self.v[1]

        return self.ball.get_rect().move(self.pos[0],self.pos[1])

    def getImage(self):
        return self.ball


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    ball = Ball()
    cam = cv2.VideoCapture(0)

    while 1:

        #result, img = cam.read()
        img=cv2.imread("IMG_1931.JPG")

        greyimg=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        #normImage=cv2.equalizeHist(greyimg)
        gray = cv2.GaussianBlur(greyimg,(5,5),0)
        normImage = cv2.adaptiveThreshold(gray,255,1,1,11,2)
        # Operation de Morphologie pour limiter le bruit de la Webcam
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))
        #imgMorph=cv2.morphologyEx(normImage,cv2.MORPH_CLOSE,kernel)
        imgMorph=cv2.dilate(normImage,kernel)
        #cv2.imshow("Bin",normImage)


        #ret,imgt = cv2.threshold(greyimg,lowThresh,255,1)
        #cv2.imshow("Bin",imgt)
        #ret, imgres=cv2.threshold(normImage,lowThresh,maxThresh,1)

        contours, hierarchy = cv2.findContours(imgMorph,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(img,contours,-1,(0,255,0),2)

        for cnt in contours:
            # On ne selectionne que les contours dont la surface est > ? 1000 pixel pour
            # ne garder que l'objet principal
            if cv2.contourArea(cnt)>500:
                approx = cv2.approxPolyDP(cnt,10,True)
                rect=cv2.minAreaRect(cnt)
                box = cv2.cv.BoxPoints(rect)
                box = np.int0(box)
                for i in range(0,4):
                    if(i==3):
                        line=[[box[i][0],box[i][1]],[box[0][0],box[0][1]]]
                    else:
                        line=[[box[i][0],box[i][1]],[box[i+1][0],box[i+1][1]]]

                    l0=(line[0][0],line[0][1])
                    l1=(line[1][0],line[1][1])
                    cv2.line(img,l0,l1,(0,255,0),2)

                    if(CalcCollision(Point(l0),Point(l1),ball)):
                        cv2.line(img,l0,l1,(255,0,0),2)
                        Vn=GetNormal(Point(l0),Point(l1),ball)
                        ball.v=CalculRebond(ball.v,Vn)
                        print "v="+str(ball.v)
                        break

                #cv2.drawContours(img,[box],0,(0,0,255),2)
                #print cv2.pointPolygonTest(cnt,(ball.X,ball.Y),False)
                #if cv2.pointPolygonTest(line,(ball.X,ball.Y),False)>=0:
                    #print "Angle: "+str(angle)+"; Ball.angle="+str(ball.angle)+"; Reflection="+str(2*(angle+90)-ball.angle)
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
