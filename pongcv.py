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
from pygame.locals import *
from PIL import Image
import numpy as np
import math

class Vecteur():

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __init__(self):
        self.x = 0
        self.y = 0

    def normalise(self):
        norme = math.sqrt(self.x**2 + self.y**2)
        self.x /= norme
        self.y /= norme

    def __str__(self):
        return str(self.x)+","+str(self.y)


class Point():
    def __init__(self, p):
        self.x= p[0]
        self.y= p[1]

    def __str__(self):
        return str(self.x) + "," + str(self.y)


"""
Le fonctions test_collision, get_normal, collision_point_cercle et collision_droite
sont tir?es du tutoriel du site du zero: http://fr.openclassrooms.com/informatique/cours/theorie-des-collisions
"""
def test_collision(a, b, c):
    if(collision_droite(a, b, c) == 0):
        return False

    AB = Vecteur()
    AC = Vecteur()
    BC = Vecteur()
    AB.x = b.x - a.x
    AB.y = b.y - a.y
    AC.x = c.centre[0] - a.x
    AC.y = c.centre[1] - a.y
    BC.x = c.centre[0] - b.x
    BC.y = c.centre[1] - b.y

    pscal1 = AB.x*AC.x + AB.y*AC.y
    pscal2 = -AB.x*BC.x - AB.y*BC.y

    if(pscal1>=0 and pscal2>=0):
        return True

    if collision_point_cercle(a, c):
        return True

    if collision_point_cercle(b, c):
        return True

    return False

"""
Calcul du rebond en fonction du vecteur vitesse et de la normal au point de collision.
:param v1: Vecteur vitesse
:param N: Normale
:
"""
def calcul_rebond(v1, N):
    v = Vecteur()
    v.x = v1[0]
    v.y = v1[1]
    pscal = v.x*N.x + v.y*N.y
    v2 = Vecteur()
    v2.x = float(v.x-2 * pscal * N.x)
    v2.y = float(v.y-2 * pscal * N.y)
    return [v2.x, v2.y]

"""
Caul de la normale
"""
def get_normal(a, b, c):
    AC = Vecteur()
    u = Vecteur()
    N = Vecteur()

    u.x = b.x - a.x
    u.y = b.y - a.y
    AC.x = c.centre[0] - a.x
    AC.y = c.centre[1] - a.y

    coeff = u.x*AC.y - u.y*AC.x
    N.x = -u.y * coeff
    N.y = u.x * coeff

    norme = math.sqrt(float(N.x)**2 + float(N.y)**2)

    N.x /= norme
    N.y /= norme

    return N

def collision_point_cercle(pt, c):
    test=0
    x=pt.x
    y=pt.y
    d=(x-c.centre[0])**2+(y-c.centre[1])**2

    if(d>c.r**2):
        test=0
    else:
        test=1
    return test

def collision_droite(a, b, c):
    Ux = b.x - a.x
    Uy = b.y - a.y
    ACx = c.centre[0] - a.x
    ACy = c.centre[1] - a.y
    num = Ux*ACy - Uy*ACx

    if num < 0:
        num=-num

    denom=math.sqrt(Ux**2+Uy**2)
    ci=num/denom

    if ci < c.r:
        return True

    return False


class Ball:

    def __init__(self):
        self.ball = pygame.image.load('Ball.png').convert()
        self.ball.set_colorkey((0,255,0)) #Couleur transparente
        self.pos = [10, 10]                    # Position initiale
        self.width=self.ball.get_width()    # Largeur du sprite
        self.height=self.ball.get_height()  # Hauteur du sprite
        self.r=self.width/2                 # Rayon de la balle
        self.centre=[(self.pos[0]+self.width/2),(self.pos[1]+self.height/2)] # Centre
        self.v=[5,5]    # Vecteur vitesse initial

    """Deplace la balle en fonction de son vecteur vitesse"""
    def move(self):
        if self.pos[0] <= 0 or self.pos[0]+self.width >= 640:
            self.v[0] = -self.v[0]
        if self.pos[1] <= 0 or self.pos[1]+self.height >= 480:
            self.v[1] = -self.v[1]

        self.pos[0] += self.v[0]
        self.pos[1] += self.v[1]
        self.centre = [self.pos[0]+self.width/2, self.pos[1]+self.height/2]

        return self.ball.get_rect().move(self.pos[0], self.pos[1])

    """Retourne l'image de la balle"""
    def get_image(self):
        return self.ball


def main():
    # Initialisation
    pygame.init()
    screen = pygame.display.set_mode((640,480))
    ball = Ball()
    cam = cv2.VideoCapture(0)

    # Boucle principale
    while 1:
        # Gestion des evenements
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        result, img = cam.read()
        #img=cv2.imread("IMG_1931.JPG")

        grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        gray = cv2.GaussianBlur(grey_img, (5,5), 0)
        normImage = cv2.adaptiveThreshold(gray, 255, 1, 1, 11, 2)
        # Operation de Morphologie pour limiter le bruit de la Webcam
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10,10))
        imgMorph = cv2.dilate(normImage, kernel)

        contours, hierarchy = cv2.findContours(imgMorph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


        for cnt in contours:
            # On ne selectionne que les contours dont la surface est > ? 500 pixel pour
            # ne garder que l'objet principal
            if cv2.contourArea(cnt) > 1000:
                #On d?termine les 4 coins entourant la ligne
                approx = cv2.approxPolyDP(cnt, 10, True)
                rect = cv2.minAreaRect(cnt)
                box = cv2.cv.BoxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(img, cnt, -1, (0,255,0), 2)
                #Pour chaque contour, on detecte le segment le plus long.
                #Ensuite, on determine le segment median qui va servir pour la collision.
                l1 = math.sqrt((box[1][0]-box[0][0])**2 + (box[1][1]-box[0][1])**2)
                l2=math.sqrt((box[2][0]-box[1][0])**2 + (box[2][1]-box[1][1])**2)

                if l1<l2:
                    pt1=Point([(box[1][0]+box[0][0])/2, (box[1][1]+box[0][1])/2])
                    pt2=Point([(box[2][0]+box[3][0])/2, (box[2][1]+box[3][1])/2])
                else:
                    pt1=Point([(box[0][0]+box[3][0])/2, (box[0][1]+box[3][1])/2])
                    pt2=Point([(box[2][0]+box[1][0])/2, (box[2][1]+box[1][1])/2])


                #Test de la collision et determination du nouveau vecteur vitesse
                if test_collision(pt1, pt2, ball):
                    n = get_normal(pt1, pt2, ball)
                    ball.v = calcul_rebond(ball.v, n)


        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.array(img)
        img = Image.fromarray(img)
        pg_img = pygame.image.frombuffer(img.tostring(), img.size, img.mode)
        pg_img = pg_img.convert()
        pg_img.blit(ball.get_image(), ball.move())
        screen.blit(pg_img, (0,0))
        pygame.display.flip()




if __name__ == '__main__':
    main()
