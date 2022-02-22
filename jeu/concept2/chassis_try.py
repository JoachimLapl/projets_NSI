import pygame, time
from math import cos, sin, acos
from random import randint

resolution = (500,500)
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
    def getNorm(cl,v):
        return hypot(v[0], v[1])
    @classmethod
    def setToNorm(cl,v, s):
        n = Vector.getNorm(v)
        s = 0 if n == 0 else s/n
        return Vector.multiply(v,s)
    @classmethod
    def getAngle(cl, v):
        return -acos(v[0]/Vector.getNorm(v)) if v[1]<0 else acos(v[0]/Vector.getNorm(v))
    @classmethod
    def rotate(cl, v, u, trigo = True):
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

class Map:
    def __init__(self):
        self.rect = -500,0,500,250
        self.relative = 0,0
        self.center = mid_screen
    def draw(self):
        self.t = Vector.subtract(self.center, self.relative)
        pygame.draw.rect(
            screen,
            0xff0000,
            pygame.Rect(
                Vector.add(self.rect[:2], self.t) + Vector.subtract(self.rect[2:],self.rect[:2])
            )
        )

class Wheel:
    def __init__(self, mp:Map, pos, r):
        self.pos = pos
        self.r = r
        self.mp = mp
        self.vector = 0,0
        self.weight = 0,.1
    def update(self, keys):
        self.pos = Vector.add(self.pos, self.vector)
        self.vector = Vector.add(self.vector, self.weight)
        if self.pos[1]>-self.r:
            self.pos = self.pos[0],-self.r
            self.vector = self.vector[0], -self.vector[1]*0 + .1
            if self.vector[1]>0:
                self.vector = Vector.Vmul(self.vector, (.9,1))
            if keys[pygame.K_LEFT]:
                self.vector = Vector.add(self.vector, (-.5,0))
            if keys[pygame.K_RIGHT]:
                self.vector = Vector.add(self.vector, (.5,0))
        self.vector = Vector.multiply(self.vector,.99)
    def draw(self):
        pygame.draw.circle(screen, 0, Vector.add(self.pos, self.mp.t), self.r)

class Propeller:
    def __init__(self, mp:Map, chassis, pos):
        self.pos = pos
        self.mp = mp
        self.vector = 0,0
        self.power = 0
        self.direction = 0,1
        self.weight = 0,.1
        self.chassis = chassis
    def update(self,keys):
        self.vector = Vector.add(self.weight, Vector.multiply(Vector.rotate(self.direction,self.chassis.orientation),-self.power))
        # print(self.vector)
    def draw(self):
        if self.power != 0:
            pygame.draw.line(
                screen,
                0x00ffff,
                Vector.add(self.pos,self.mp.t),
                Vector.add(self.pos, self.mp.t, Vector.multiply(Vector.rotate(self.direction,self.chassis.orientation), self.power*1)),
                width=5
            )
            Vector.draw(self.vector, Vector.add(Vector.add(self.pos, self.mp.t)),1)

class Chassis:
    def __init__(self, mp:Map, path, wheels_positions, wheels_radius, propellers_positions=(), pos=(0,0)):
        self.pts = path;
        self.w = tuple(map(lambda p : Wheel(mp, Vector.add(p,pos), wheels_radius), wheels_positions))
        self.w_pos = wheels_positions
        self.p = tuple(map(lambda p: Propeller(mp, self, Vector.add(p,pos)), propellers_positions))
        self.p_pos = propellers_positions
        self.rotateIndex = 0
        self.orientation = 1,0
        self.angle = 0
        self.pos = pos
        self.weight = 0,.5
        self.vector = 0,0
        self.mp = mp
        self.elas = 1
    def update(self, keys):
        if keys[pygame.K_UP]:
            self.p[0].power = 1 if keys[pygame.K_RIGHT] else .75
            self.p[1].power = 1 if keys[pygame.K_LEFT ] else .75
        else: self.p[0].power = self.p[1].power = 0
        for w in self.w+self.p:
            w.update(keys)
        # self.vector = Vector.add(
        # self.vector,*map(lambda w: Vector.draw(w.vector, Vector.add(w.pos, self.mp.t),1) or w.vector, self.w+self.p))
        # self.pos = Vector.add(self.pos,self.vector)
        # # for i in self.p:
        # #     print(Vector.getAngle(Vector.add(i.pos,i.vector))-Vector.getAngle(i.pos))
        # offset_Angle = (
        #         sumTuple(tuple(map(lambda i:Vector.getAngle(Vector.subtract(i.pos,self.pos)), self.w+self.p)))
        #         -sumTuple(tuple(map(lambda i:Vector.getAngle(Vector.add(Vector.subtract(i.pos,self.pos),i.vector)), self.w+self.p)))
        #     )
        # offset_Angle /= len(self.w)+len(self.p)
        # self.rotationIndex += offset_Angle
        # print(offset_Angle)
        # self.angle += self.rotationIndex*.1 + offset_Angle
        # self.orientation = Vector.rotate(self.orientation,
        #     (cos(self.angle), sin(self.angle))
        # )
        # self.vector = Vector.add(self.vector, self.weight)
        # self.w_aimed = tuple(map(lambda p:Vector.add(Vector.rotate(p,self.orientation),self.pos), self.w_pos))
        # w_actual = tuple(map(lambda w:w.pos,self.w))
        # for i in range(len(self.w)):
        #     v = Vector.subtract(self.w_aimed[i], w_actual[i])
        #     self.w[i].vector = Vector.add(self.w[i].vector,Vector.multiply(v,self.elas/2))
        #     self.vector = Vector.add(self.vector,Vector.multiply(v,-self.elas/2))
        # for i in range(len(self.p)):
        #     self.p[i].pos = Vector.add(Vector.rotate(self.p_pos[i],self.orientation),self.pos)
        # self.vector = Vector.multiply(self.vector,.99)
        # self.rotationIndex *= .95
        self.vector = Vector.add(
            self.vector,
            *map(lambda p: p.vector, self.p),
            self.weight)
        self.pos = Vector.add(
            Vector.multiply(self.vector,.1),
            Vector.multiply(
                Vector.add(*map(lambda p: Vector.add(p.pos,p.vector), self.p),self.pos, self.weight),
                1/(len(self.p)+1)
            )
        )
        offset_Angle = sumTuple(tuple(map(lambda p: Vector.getAngle(Vector.subtract(p.pos,self.pos)),self.p)))-sumTuple(tuple(map(lambda p: Vector.getAngle(Vector.subtract(Vector.add(p.pos,p.vector),self.pos)),self.p)))
        self.rotateIndex += offset_Angle
        self.angle += self.rotateIndex*.1 + offset_Angle
        self.orientation = cos(self.angle), sin(self.angle)
        self.vector = Vector.multiply(self.vector, .99)
        self.rotateIndex *= .95
    def draw(self):
        pygame.draw.polygon(screen, 0x0000ff, tuple(map(lambda pt: Vector.add(Vector.rotate(pt,self.orientation),self.pos, self.mp.t) ,self.pts)))
        for w in self.w+self.p:
            w.draw()
            # print(Vector.add(self.pos,self.mp.t))
        Vector.draw(Vector.multiply(self.vector, 1), Vector.add(self.pos, self.mp.t), 1)

mp = Map()
chassis = Chassis(
    mp,
    ((-20,0),(0,-10),(20,0)),
    (),
    # ((-5,5),(5,5),(-15,5),(15,5), (0,-10)),
    5,
    ((-20,0),(20,0)),
    pos=(0,-100)
)
wheel = Wheel(mp, (0,-100), 10)

RUN = True

while RUN:
    screen.fill(0xffffff)
    mp.draw()
    keys = pygame.key.get_pressed()
    chassis.update(keys)
    mp.relative = chassis.pos
    chassis.draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN = False
    pygame.display.flip()
    clock.tick(60)
pygame.quit()