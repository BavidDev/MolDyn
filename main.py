## IMPORT ##

import threading
import time
import math
from math import pow as p
import numpy as np
import pygame
import object
idData = object.idTable
import random

## INITALISATION

pause = False
running = True
bondingConstant = -1
pygame.init()

objects = []
bonds = []

## FUNCTIONS ##

def distance2D(a,b):
    dist = math.sqrt(p(a[0]-b[0],2) + p(a[1]-b[1],2))
    return dist

def mag(a):
    mag = math.sqrt(p(a[0],2)+p(a[1],2))
    return mag

def toScreenCoords(a, cenPos, scale, scr):
    a = (a - cenPos)/scale
    width = scr.get_width()
    height = scr.get_height()

    return (-a[0]+(width/2), a[1]+(height/2))

def toPhysCoords(a, cenPos, scale, scr):
    width = scr.get_width()
    height = scr.get_height()

    a -= np.array([width/2, height/2])
    a[0] = -a[0]
    a *= scale
    a += cenPos

    return a


def covalentForce(r, Eb, r0):
    r0 = r0/p(10,12)

    Eb = Eb/(6.02*p(10,20)) ##20

    k=Eb/p(r0,2)
    eTerm = np.exp(-k*(r-r0))
    modR = r/r0

    return -2*Eb*(1-eTerm/modR)*eTerm*(r*k+1)/(r0*p(modR,2))

    

def areBonded(i,j, Eb, r0):
    
    r = distance2D(i.p,j.p)
    r0 = r0/p(10,12)
    if r == 0: r = r0/100
    if r > 5*r0: return False

    Eb = Eb/(6.02*p(10,20)) ##26

    k=Eb/p(r0,2)
    eTerm = np.exp(-k*(r-r0))
    modR = r/r0

    Epot = Eb*(p(1-(eTerm/modR),2)-1)
    Ekin = 0.5*i.m*p(np.linalg.norm(i.v),2)

    return Epot + Ekin < -0.25*Eb

def physicsLoop():
    global running
    global objects
    global pause
    global bonds
    global idData

    timeSpeed = 7*p(10,-14)
    ke = 8.9875 * p(10,9) 
    dt = 0.001

    while running:
        if pause == False:
            positions = []

            for i in objects:

                F = np.array([0,0])
                for j in objects:

                    if i==j: 
                        pass
                    else:
                        dist = distance2D(i.p,j.p)

                        ##COULOMBIC FORCE
                        Fc = np.array([0,0])
                        Fc = -(j.p-i.p)*ke*i.c*j.c/p(dist,3)

                        ##MORSE FORCES

                        Fmor = np.array([0,0])
                        BDE = idData[i.id-1][2][j.id-1]
                        r0 = idData[i.id-1][0][1] + idData[j.id-1][0][1]
                        Fmor = covalentForce(dist, BDE, 62)*(i.p-j.p)/dist ##436

                        ##NET FORCE
                        F = F + Fmor

                a = F/i.m
                i.v = i.v + a*dt*timeSpeed
                positions.append(i.p + i.v*dt*timeSpeed)
            

            for i in range(len(positions)):
                
                objects[i].p = positions[i]

            bonds = []

            for i in objects:
                for j in objects:
                    if i != j:
                            if areBonded(i,j, 436, 62):
                                print("BOND REGISTERED")
                                if objects != []:
                                    bonds.append((objects.index(i),objects.index(j)))
                                    i.BondCount = 1
                                    j.BondCount = 1
            
        time.sleep(dt)
    
    return

def displayLoop():
    global running
    global objects
    global pause
    global bonds

    centerPosition = np.array([0,0])
    scale = p(10,-11) ##default is exponent -16

    scr = pygame.display.set_mode((600,500), pygame.RESIZABLE)
    pygame.display.set_caption('Moldyn')

    while running:
        pygame.display.flip()
        for event in pygame.event.get():  
            if event.type == pygame.QUIT:  
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    scale = scale/1.1
                elif event.button == 5:
                    scale = 1.1*scale
                elif event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    mousePos = toPhysCoords(np.array([float(mouse_x), float(mouse_y)]), centerPosition, scale, scr)

                    id = 1
                    objects.append(object.object(
                        id,
                        mousePos,
                        np.array([0,0])))
                elif event.button == 3:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    mousePos = toPhysCoords(np.array([float(mouse_x), float(mouse_y)]), centerPosition, scale, scr)

                    id = 2
                    objects.append(object.object(
                        id,
                        mousePos,
                        np.array([0,0])))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pause = not pause
                elif event.key == pygame.K_r:
                    objects = []
                    bonds = []


        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            centerPosition = centerPosition - scale*np.array([0,1])

        if keys[pygame.K_s]:
            centerPosition = centerPosition - scale*np.array([0,-1])

        if keys[pygame.K_d]:
            centerPosition = centerPosition - scale*np.array([1,0])

        if keys[pygame.K_a]:
            centerPosition = centerPosition - scale*np.array([-1,0])

        scr.fill((0,0,0))

        for i,j in bonds:
            pygame.draw.line(scr, (250,250,250), toScreenCoords(objects[i].p, centerPosition, scale, scr), toScreenCoords(objects[j].p, centerPosition, scale, scr), 5)
        
        for i in objects:

            screenPosition = toScreenCoords(i.p, centerPosition, scale, scr)

            if i.id == 1:
                pygame.draw.circle(scr, (250,250,250), screenPosition,i.r[0]/scale)
            elif i.id == 2:
                pygame.draw.circle(scr, (250,0,0), screenPosition,i.r[0]/scale)
        
## CORE ##

if __name__ == '__main__':
    DThread = threading.Thread(target=displayLoop)
    PThread = threading.Thread(target=physicsLoop)

    PThread.start()
    DThread.start()
    PThread.join()
    DThread.join()

pygame.quit()
