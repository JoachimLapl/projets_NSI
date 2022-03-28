import pygame
from math import pi,cos,sin,acos,asin

resolution = 400,400
mid_screen = tuple(i/2 for i in resolution)
mi,ma = sorted(resolution)

screen = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()

def sumTuple(t, callback = lambda x : x):
    S = type(tuple(t)[0])()
    for i in t:
        S += callback(i)
    return S

def hypot(*v):
    return sumTuple(v, lambda x : x ** 2) ** .5

class Vector:
    @classmethod
    def add(cl,*v):
        return tuple(map(lambda *a: sumTuple(a), *v))
    @classmethod
    def subtract(cl,v, u):
        return v[0]-u[0],v[1]-u[1]
    @classmethod
    def multiply(cl,v, n):
        return v[0]*n,v[1]*n
    @classmethod
    def Vmul(cl,v,u):
        return v[0]*u[0],v[1]*u[1]
    @classmethod
    def isOpposite(cl,v, u, m = 0):
        return sumTuple(Vector.add(v, u), lambda x : x ** 2) < sumTuple(v, lambda x : x ** 2) + sumTuple(u, lambda x : x ** 2) + m
    @classmethod
    def getNorm(cl,v):
        return hypot(v[0], v[1])
    @classmethod
    def setToNorm(cl,v, s):
        n = Vector.getNorm(v)
        s = 0 if n == 0 else s/n
        return Vector.multiply(v,s)
    @classmethod
    def getAngle(cl, v):
        return acos(v[0]/Vector.getNorm(v)) if v[1]<0 else -acos(v[0]/Vector.getNorm(v))
    @classmethod
    def rotate(cl, v, u, trigo = True):
        if type(u) is float: u = cos(u),sin(u)
        coef = 1 if trigo else -1
        return u[0]*v[0]-u[1]*v[1]*coef, u[0]*v[1]+u[1]*v[0]*coef
    @classmethod
    def draw(cl,v,p,w=.5,c=0x000000):
        q = Vector.add(p,v)
        pygame.draw.line(screen, c, p, q, int(w))
        u = Vector.setToNorm(v, 1)
        pts = (
            Vector.add(Vector.multiply(u,w*1.5),q),
            Vector.add(Vector.multiply((-(u[0]+u[1]),u[0]-u[1]), w*1.25),q),
            Vector.add(Vector.multiply((u[1]-u[0],-(u[0]+u[1])), w*1.25),q)
        )
        pygame.draw.polygon(screen, c, pts)
    @classmethod
    def setAngle(cl, a):
        return cos(a),sin(a)


class Chassis:
    def __init__(self, x,y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotateInertia = 1,0
        self.orientation = 1,0
        self.speed = 0
        # self.absolutepath = sumTuple(tuple((tuple((i*j*.5*width, j*.5*height) for i in (-1,1)) for j in (-1,1))))
        self.absolutepath = ((10,0),(-10,-10),(-10,10))
    def getPath(self):
        return tuple(
            map(
                lambda v:Vector.add(Vector.rotate(v, self.orientation),(self.x,self.y), mid_screen),
                self.absolutepath
            )
        )
    def draw(self):
        pygame.draw.polygon(screen, 0xff0000, self.getPath())
    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rotateInertia = Vector.rotate(self.rotateInertia, (cos(.02),-sin(.02)))
        if keys[pygame.K_RIGHT]:
            self.rotateInertia = Vector.rotate(self.rotateInertia, (cos(.02),sin(.02)))
        dist = int(keys[pygame.K_UP]) - int(keys[pygame.K_DOWN])
        self.speed+=dist*.3
        self.x += self.speed*self.orientation[0]
        self.y += self.speed*self.orientation[1]
        self.orientation = Vector.rotate(self.orientation, self.rotateInertia)
        self.rotateInertia = Vector.setToNorm(Vector.add(self.rotateInertia,(.3,0)),1)
        self.speed*=.95

chassis = Chassis(0,0,50,50)

RUN = True

while RUN:
    screen.fill(0xffffff)
    # chassis.orientation = Vector.rotate(chassis.orientation, (cos(.01),sin(.01)))
    chassis.update(pygame.key.get_pressed())
    chassis.draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN = False
    pygame.display.flip()
    clock.tick(60)
pygame.quit()