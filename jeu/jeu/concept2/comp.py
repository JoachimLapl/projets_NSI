import pygame
from math import floor, pi, asin, acos, sin, cos, log


resolution = (500,500)
mid_screen = tuple(i/2 for i in resolution)

mi,ma = sorted(resolution)

screen = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()

pygame.font.init()
fontName = pygame.font.get_default_font()
font = pygame.font.SysFont(fontName, 23)
def render_text(txt):
    txt = font.render(txt, True, 0)
    screen.blit(txt,(2,2))


def sumTuple(t, callback = lambda x : x):
    S = type(tuple(t)[0])()
    for i in t:
        S += callback(i)
    return S

def polynomial(a, b, c):
    Delta = b ** 2 - 4 * a * c
    if (Delta < 0): return ()
    if (Delta == 0): return -b / a / 2,
    Dsqrt = Delta**.5
    return -(Dsqrt + b) / a / 2, (Dsqrt - b) / a / 2,

def mp(itera, callback=lambda x,i:x):
    return tuple(callback(itera[i],i) for i in range(len(itera)))

def hypot(*v):
    return sumTuple(v, lambda x : x ** 2) ** .5

def removeDoublons(itera):
    def getBool(j,e):
        for k in range(j):
            if itera[k][0] == e[0] and itera[k][1] == e[1]:
                return False
        return True
    return tuple(itera[i] for i in range(len(itera)) if getBool(i, itera[i]))

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

class Point(Vector):
    @classmethod
    def distance(cl, p, q):
        return hypot(p[0] - q[0], p[1] - q[1])
    @classmethod
    def translate(cl, p, v):
        return Vector.add(p, v)
    @classmethod
    def homothetia(cl, p, n, rel=(0,0)):
        return Vector.add(Vector.multiply(Vector.subtract(p,rel),n),rel)
    @classmethod
    def rotate(cl, p, r:float, rel=(0,0)):
        p = Vector.subtract(p,rel)
        c,s = cos(r),sin(r)
        return Vector.add((c*p[0]+s*p[1],c*p[1]-s*p[0]),rel)

class Droite:
    @classmethod
    def Point_Vector(cl, p, v):
        return Droite(v[1], -v[0], v[0] * p[1] - v[1] * p[0])
    @classmethod
    def Point_Point(cl, p, q):
        return Droite(q[1] - p[1], p[0] - q[0], q[0] * p[1] - q[1] * p[0])
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
    def intersection(self, l):
        if type(l) is Droite:
            c,d,e = l.a,l.b,l.c
        else: c,d,e = l
        a, b = self.a * d, c * self.b
        if (a != b):
            x = (self.b * e - d * self.c) / (a - b)
            y = (self.a * e - c * self.c) / (b - a)
            return x, y
    def PV_intersection(self, P, v):
        b = self.a * v[0] + self.b * v[1]
        if (b):
            a = v[1] * P[0] - v[0] * P[1]
            return (
                (a * self.b - self.c * v[0]) / b,
                (-a * self.a - self.c * v[1]) / b
            )
    def closest(self, point):
        a2, b2, ab = self.a ** 2, self.b ** 2, self.a * self.b
        return (
            (b2 * point[0] - ab * point[1] - self.a * self.c) / (a2 + b2),
            (a2 * point[1] - ab * point[0] - self.b * self.c) / (a2 + b2)
        )
    def distance(self, point):
        return abs(self.a*point[0]+self.b*point[1]+self.c)/(self.a**2+self.b**2)**.5
    def translate(self, t = (0,0)):
        self.c -= t[0] * self.a + t[1] * self.b
    def homothetia(self, k):
        self.c *= k
    def draw(self, color=0,w=1):
        i = (self.intersection((0, -1, 0)),
            self.intersection((1, 0, 0)),
            self.intersection((0, -1, resolution[0])),
            self.intersection((1, 0, -resolution[1]))
            )
        i = tuple(j for j in i if j and j[0] >= 0 and j[1] >= 0 and j[0] <= resolution[0] and j[1] <= resolution[1])
        d=removeDoublons(i)
        if len(d)==2:
            pygame.draw.line(screen, color, d[0],d[1], w)

class Circle:
    def __init__(self, point, radius):
        self.a = point[0]
        self.b = point[1]
        self.c = radius
    def intersectionLine(self, line: Droite):
        return mp(polynomial(
            line.a ** 2 + line.b ** 2,
            2 * (line.b * line.c - line.a ** 2 * self.b),
            -(line.a ** 2) * (self.c ** 2 - self.b ** 2 - self.a ** 2) + 2 * line.a * self.a * (line.b + line.c) + line.c ** 2
        ), lambda y,i: Droite(0, 1, -y).intersection(line))
    def homothetia(self, k):
        self.a *= k
        self.b *= k
        self.c *= k

class Segment:
    def __init__(self, p, v):
        self.p = p
        self.v = v
        q = Vector.add(self.p,self.v)
        self.line = Droite(-v[1],v[0],v[1]*p[0]-v[0]*p[1])
        self.interval = (sorted((p[0],q[0])),sorted((p[1],q[1])))
    def translate(self, t:tuple):
        self.p = Vector.add(self.p, t)
        self.line.translate(t)
        self.interval = tuple(tuple(self.interval[i][j]+t[i] for j in (0,1)) for j in (0,1))
    def getSize(self):
        return Vector.getNorm(self.v)
    def getQ(self):
        return Vector.add(self.p,self.v)

class Force:
    def __init__(self, p, v):
        self.p = p
        self.v = v
        self.line = Droite(-v[1],v[0],v[1]*p[0]-v[0]*p[1])
        self.nextPos = Vector.add(p,v)

class Interval:
    @classmethod
    def union(cl, i1,i2): # si i1 et i2 sont des intervalles continus
        if i2[0]<i1[0]: i1,i2 = i2,i1
        if i1[1]>i2[1]: return i1
        if i1[1]>i2[0]: return (i1[0],i2[1])
        return (i1,i2) # intervalle non continu
    @classmethod
    def intersects(cl, i1,i2):
        if type(i1[0]) is int or type(i1[0]) is float:
            return i1[0]<=i2[1] and i1[1]>=i2[0]
        else:
            if Interval.intersects(i1[0],i2[0]) and Interval.intersects(i1[1],i2[1]):
                return True
            return False

class Triangle:
    @classmethod
    def angleFromSides(cl, a1,a2,o):
        return acos(min(max((a1**2+a2**2-o**2)/(2*a1*a2),-1),1))

def every(itera, callback=lambda x,i:True):
    for i in range(len(itera)):
        if not callback(itera[i],i):
            return False
    return True

def getOffsetVector(v,u,v_n,u_n):
    i = v[0]*u[1]-v[1]*u[0]
    return (v[0]*u_n - u[0]*v_n)/i, (v[1]*u_n - u[1]*v_n)/i

def removeDoublons(l):
    return tuple(l[i] for i in range(len(l)) if l.index(l[i]) == i)


class Block:
    class Radius:
        def __init__(self, lines, circles):
            self.lines = lines # du type Wall.Line
            self.circles = circles   # du type Wall.Circle
            self.walls= (*lines,*circles)
            self.arranged = ( # might be useful to make the getwithinWalls method faster
                sorted(self.walls, key=lambda e: e.interval[0][0]), #left
                sorted(self.walls, key=lambda e: e.interval[0][1]), #right
                sorted(self.walls, key=lambda e: e.interval[1][0]), #top
                sorted(self.walls, key=lambda e: e.interval[1][1])  #bottom
            )
            self.interval= (
                (self.arranged[0][0].interval[0][0],self.arranged[1][-1].interval[0][1]),
                (self.arranged[2][0].interval[1][0],self.arranged[3][-1].interval[1][1])
            )
        def getwithinWalls(self, segment:Segment):
            if not Interval.intersects(self.interval, segment.interval): return ()
            return tuple(w for w in self.lines if Vector.isOpposite(w.v, segment.v))+tuple(w for w in self.circles if Vector.isOpposite(Vector.subtract(segment.p,w.p),segment.v) and Interval.intersects(w.interval, segment.interval))
    def __init__(self,points):
        assert len(points)>2, "les blocks ne peuvent pas être des lines ou des points"
        self.points = points
        self.lineWalls = tuple(Wall.Line(points[i-1],points[i]) for i in range(len(points)))
        checkhole = False
        self.pointWalls = tuple(Wall.Circle(points[i],0) for i in range(len(points)) if not Vector.isOpposite(self.lineWalls[i].vp,Vector.subtract(self.lineWalls[(i+1)%len(points)].v,self.lineWalls[i].v)))
    def elab_walls(self,r:float):
        lines = mp(self.lineWalls, lambda w,j: w.radiusApplyWall(r))
        for i in range(len(self.points)):
            lines+=(Wall.Line(lines[i-1].q, lines[i].p),)
        circles = mp(self.pointWalls, lambda w,j: w.radiusApplyWall(r))
        return Block.Radius(lines,circles)
    def draw(self, t:tuple=(0,0), k:float=1):
        pygame.draw.polygon(screen, 0xaaaaaa, mp(self.points, lambda p,i: Vector.add(p,t)))

class Wall:
    class Line:
        def __init__(self, p, q):
            self.v = p[1]-q[1], q[0]-p[0]
            self.vp = Vector.subtract(q,p)
            self.line = Droite(*self.v, -(self.v[0] * p[0] + self.v[1] * p[1]))
            self.p = p
            self.q = q
            self.interval = sorted((p[0],q[0])),sorted((p[1],q[1]))
            self.u = Vector.setToNorm(self.v,1) #vecteur unitaire
            self.up = Vector.setToNorm(self.vp,1) #vecteur unitaire
        def radiusApplyWall(self, r:float):
            v = Vector.multiply(self.u,r)
            return Wall.Line(Vector.add(self.p, v), Vector.add(self.q, v))
        def collides(self, segment:Segment):
            intersect = self.line.intersection(segment.line)
            return segment.p if not intersect else intersect if Point.distance(segment.p, intersect)<=segment.getSize() else False
        def bounce(self, segment:Segment, intersect, bounciness=1):
            q = segment.getQ()
            dist = self.line.distance(q)
            npos = Vector.add(q, Vector.multiply(self.u, dist*(1+bounciness)))
            k,l = Vector.multiply(((self.up[0]*segment.v[0]+self.up[1]*segment.v[1]),(self.up[1]*segment.v[0]-self.up[0]*segment.v[1])), self.up[0]**2+self.up[1]**2)
            return (
                npos,
                Vector.subtract(Vector.multiply(self.up,k*bounciness),Vector.multiply((self.up[1],-self.up[0]), l*bounciness)),
                self.up,
                self.u,
                k,l
            )
        def draw(self, t:tuple = (0,0), k:float = 1):
            pygame.draw.line(screen, 0, Vector.add(self.p,t), Vector.add(self.q,t), width=1)
        def closeToInterval(self,point, err=.1):
            return self.interval[0][0]-err<point[0]<self.interval[0][1]+err and self.interval[1][0]-err<point[1]<self.interval[1][1]+err
    class Circle:
        def __init__(self, p, r:float):
            self.p = p
            self.r = r
            self.circle = Circle(p,r)
            self.interval = (p[0]-r,p[0]+r),((p[1]-r,p[1]+r))
        def radiusApplyWall(self, r:float):
            return Wall.Circle(self.p, self.r+r)
        def collides(self, segment:Segment):
            intersect = mp(self.circle.intersectionLine(segment.line), lambda p,i: (p,Point.distance(p,segment.p)))
            if len(intersect) == 0: return None
            intersect = min(intersect, key= lambda x:x[1])
            return intersect[0] if intersect[1]<=segment.getSize() else False
        def bounce(self, segment:Segment, intersect, bounciness=1):
            v = Vector.multiply(Vector.subtract(intersect, self.p),1/self.r)
            u = v[1],-v[0]
            drt = Droite(*v, -v[0]*intersect[0]-v[1]*intersect[1])
            q = segment.getQ()
            dist = drt.distance(q)
            npos = Vector.add(q, Vector.multiply(v, dist*(1+bounciness)))
            k,l = Vector.multiply(((u[0]*segment.v[0]+u[1]*segment.v[1]),(u[1]*segment.v[0]-u[0]*segment.v[1])), u[0]**2+u[1]**2)
            return (
                npos,
                Vector.subtract(Vector.multiply(u,k*bounciness),Vector.multiply((u[1],-u[0]), l*bounciness)),
                u,
                v,
                k,l
            )
        def draw(self, t:tuple = (0,0), k:float = 1):
            pygame.draw.circle(screen, 0, Vector.add(self.p,t), self.r)
        def closeToInterval(self,point, err=.01):
            return self.interval[0][0]-err>point[0]>self.interval[0][1]+err and self.interval[1][0]-err>point[1]>self.interval[1][1]+err


class Wheel:
    def __init__(self, chassis, pos, r:float, bounciness:float=.1):
        self.bounciness = bounciness
        self.chassis = chassis
        self.pos = pos
        self.weight = Force(pos, (0,.01))
        self.forces = [self.weight]
        self.vector = 0,0
        self.nextPos = pos
        self.r = r
        self.bounciness = .5
    def update(self, leftArrow, rightArrow):
        seg = self.getSegment()
        self.vector = Vector.add(self.vector, *mp(self.forces, lambda f,i: f.v))
        self.pos = Vector.add(self.pos, self.vector)
        walls = self.chassis.mp.getWithinWalls(self)
        walls1 = tuple((w.collides(seg), w) for w in walls)
        walls2 = tuple(w for w in walls1 if w[0] and w[1].closeToInterval(w[0]))
        if len(walls2)>0:
            for w in sorted(walls2, key= lambda w: w[0]):
                data = w[1].bounce(seg,w[0], self.bounciness)
                if Vector.isOpposite(Vector.add(Vector.multiply(self.weight.v,1), data[1]), data[3]):
                    self.vector = Vector.multiply(data[2],data[4])
                    self.pos = Vector.add(Vector.subtract(w[0],Vector.multiply(data[3],-.0005)),self.vector)
                else:
                    self.pos = data[0] # ou w[0], ça rend plus joli mais ça ne marche pas (pas encore)
                    self.vector = data[1]
                self.vector = Vector.add(self.vector, Vector.multiply(data[2], (leftArrow-rightArrow)))
        self.vector = Vector.multiply(self.vector,.99)
    def addForce(self, force):
        self.forces.append(force)
    def display(self, t:tuple=(0,0), k:float=1):
        pygame.draw.circle(screen, 0, Vector.add(self.pos,t), self.r, 0xff0000)
    def drawVec(self, t:tuple=(0,0), k:float=1):
        Vector.draw(Vector.multiply(self.vector,k*5), Vector.add(Vector.multiply(self.pos,k),t),.1*k,0x00ff00)
    def getSegment(self):
        return Segment(self.pos, self.vector)


class Ressort:
    def __init__(self, p, q, elasticity=.5, distance=None):
        self.p = p
        self.q = q
        self.dist = distance if distance else Point.distance(p.pos,q.pos)
        self.v1 = [0,0]
        p.addForce(self.v1)
        self.v2 = [0,0]
        q.addForce(self.v2)
        self.elas =  1 - elasticity
    def update(self):
        a,b  = Vector.subtract(self.p.pos, self.q.pos)
        h = hypot(a,b)
        if h == 0: return
        s = (h-self.dist)/2 * self.elas/h
        a *= s
        b *= s
        self.v1[0] = -a
        self.v1[1] = -b
        self.v2[0] = a
        self.v2[1] = b
    def display(self, carte=None, color=0, width=1):
        if carte:
            a,b = mp((self.p.pos,self.q.pos), lambda e,i : Vector.subtract(Vector.add(Vector.multiply(e, carte.l), carte.relative), carte.center))
            pygame.draw.line(screen, color, a,b, width)
        else: pygame.draw.line(screen, color, self.p.pos, self.q.pos, width)


class Carte:
    types = (
        (0, 0x888888),
        (.75, 0x00ffff)
    )
    def __init__(self, data, dimensions, tileSize, images:dict={}, centerPosition = mid_screen):
        self.matrix = tuple(tuple([] for j in range(dimensions[0]))for i in range(dimensions[1]))
        self.points = ()
        self.blocks = ()
        self.wheels = ()
        self.chassis = ()
        for d in data:
            l = len(d)//2
            assert l>2, "an error overcome in the building of the map"
            nPts = tuple(
                Vector.multiply((d[i*2],d[i*2+1]),tileSize) for i in range(l)
            )
            self.points += (nPts,)
            if l>2:
                self.blocks += (Block(nPts),)
        self.radBlocks = {}
        self.l = tileSize
        self.center = centerPosition
        self.relative = 0,0
    def getWithinWalls(self, wheel:Wheel):
        seg = wheel.getSegment()
        return sumTuple(tuple(b.getwithinWalls(seg) for b in self.radBlocks[wheel.r]))
    def insert_wheel(self, wheel:Wheel):
        if wheel.r not in self.radBlocks.keys():
            self.radBlocks[wheel.r] = mp(self.blocks, lambda b,i: b.elab_walls(wheel.r))
        self.wheels += (wheel,)
    def insert_chassis(self, chassis):
        if chassis.w_r not in self.radBlocks.keys():
            self.radBlocks[chassis.w_r] = mp(self.blocks, lambda b,i: b.elab_walls(chassis.w_r))
        self.chassis += (chassis,)
    def update(self):
        keys = pygame.key.get_pressed()
        for a in self.wheels:
            a.update(self, keys[pygame.K_LEFT], keys[pygame.K_RIGHT])
        for a in self.chassis:
            a.update(keys)
    def draw(self):
        self.t = Vector.subtract(self.center,self.relative)
        for b in self.blocks:
            b.draw(self.t, self.l)
        for w in self.wheels:
            w.display(t, self.l)
            w.drawVec(t, self.l)
        for c in self.chassis:
            c.draw()

class Propeller:
    def __init__(self, chassis, pos):
        self.power = 0
        self.chassis = chassis
        self.vector = 0,0
        self.pos = pos
    def update(self):
        self.vector = (
            cos(self.chassis.orientation) * self.power,
            -sin(self.chassis.orientation) * self.power
        )
        self.nextpos = Vector.add(self.pos, self.vector)
    def draw(self, vector:bool=False):
        if vector:
            Vector.draw(self.vector, Vector.add(self.pos,self.chassis.mp.t), 1)
        pygame.draw.line(screen, 0xffff, Vector.add(self.pos,self.chassis.mp.t), Vector.add(self.pos,self.chassis.mp.t, Vector.multiply(self.vector,-10*self.power**.5)), 3)

class Weight:
    def __init__(self, pos):
        self.vector = 0,1
        self.pos = pos
    def update(self):
        self.nextpos = Vector.add(self.pos, self.vector)

class AttachPoint:
    def __init__(self, chassis, wheel, elasticity):
        self.elas = 1 - elasticity
        self.chassis = chassis
        self.wheel = wheel
        self.pos = wheel.pos
        self.vector = self.wheel.weight.v
        self.nextpos = self.pos
    def update(self, keys):
        self.wheel.update(keys[pygame.K_LEFT],keys[pygame.K_RIGHT])
        v = Vector.subtract(self.wheel.pos, self.pos)
        h = log(Vector.getNorm(v))
        s = log(h)*self.elas if h>1 else 0
        if s < 10:
            self.wheel.vector = Vector.add(self.wheel.vector, Vector.multiply(v, -s))
            self.vector = Vector.multiply(v, s)
        else:
            self.wheel.vector = 0,0
            self.vector = 0,0
            self.wheel.pos = self.pos
        self.nextpos = Vector.add(self.pos,self.vector)
    def draw(self):
        pygame.draw.circle(screen, 0xffff00, Vector.add(self.pos, self.chassis.mp.t), 1)
        pygame.draw.line(screen, 0xffaa00, Vector.add(self.pos, self.chassis.mp.t), Vector.add(self.wheel.pos, self.chassis.mp.t))

class Chassis:
    def __init__(self, mp:Carte, pos, path, r, w_pos, w_r=5):
        # assert len(propellers_positions) == 2, 'there can only be 2 propellers'
        self.p = pos
        self.path = path
        self.orientation = pi/2
        self.vector = 0,0
        self.mp = mp
        self.r = r
        self.w_r = w_r
        self.propellers = Propeller(self, Vector.add(pos, (-r,0))),Propeller(self, Vector.add(pos, (r,0)))
        self.weight = Weight(pos)
        self.rotateIndex = 0
        self.w_pos = w_pos
        self.wheels = tuple(map(lambda p:Wheel(self, Vector.add(p,self.p), w_r, 0), w_pos))
        self.aPs = tuple(map(lambda w: AttachPoint(self,w,.01),self.wheels))
        mp.insert_chassis(self)
    def update(self, keys):
        self.propellers[0].power = ((1 if keys[pygame.K_RIGHT] else .75) if keys[pygame.K_UP] else 0)*(2 if keys[pygame.K_LSHIFT] else 1)
        self.propellers[1].power = ((1 if keys[pygame.K_LEFT] else .75) if keys[pygame.K_UP] else 0)*(2 if keys[pygame.K_LSHIFT] else 1)
        for p in self.propellers:
            p.update()
        self.weight.update()
        self.vector = Vector.add(self.vector, self.propellers[0].vector, self.propellers[1].vector, self.weight.vector, *map(lambda a:a.vector, self.aPs))
        self.p = Vector.add(
            Vector.multiply(self.vector, .1),
            Vector.multiply(Vector.add(self.propellers[0].nextpos,self.propellers[1].nextpos,self.weight.nextpos), 1/3)
        )
        oA = asin(-self.propellers[0].power/self.r) + asin(self.propellers[1].power/self.r)
        out1 = tuple(map(lambda p: (Vector.subtract(p.pos, self.p),Vector.subtract(p.nextpos, self.p)), self.aPs))
        out2 = tuple(map(lambda v: (Vector.getNorm(v[0]),Vector.getNorm(v[1])), out1))
        oA += sumTuple(
            tuple(map(
            lambda p,a,b: (
                Triangle.angleFromSides(
                    b[0],
                    b[1],
                    Vector.getNorm(p.vector),
                ) * (-1 if Vector.isOpposite(p.vector, (a[0][1],-a[0][0])) else 1)
            ) if b[0] * b[1] * Vector.getNorm(p.vector) != 0 else 0,
            self.aPs,
            out1,
            out2
            ))
        )/(len(self.w_pos))
        self.rotateIndex += oA
        self.orientation += self.rotateIndex*.1 + oA
        self.propellers[0].pos = Vector.add(self.p, Vector.multiply((sin(self.orientation),cos(self.orientation)),-self.r))
        self.propellers[1].pos = Vector.add(self.p, Vector.multiply((sin(self.orientation),cos(self.orientation)),self.r))
        self.weight.pos = self.p
        ro = sin(self.orientation),cos(self.orientation)
        for aP,p in zip(self.aPs,self.w_pos):
            aP.pos = Vector.add(self.p,Vector.rotate(p,ro))
            aP.update(keys)
        self.vector = Vector.multiply(self.vector, .99)
        self.rotateIndex *= .95
        render_text('{},{}'.format(*map(round,self.p)))
    def draw(self):
        ro = sin(self.orientation),cos(self.orientation)
        for p in self.aPs:
            p.draw()
        for p in self.wheels:
            p.display(self.mp.t, self.mp.l)
        for p in self.propellers:
            p.draw()
        pygame.draw.polygon(screen, 0xff, tuple(map(lambda p: Vector.add(self.p,Vector.rotate(p,ro),self.mp.t),self.path)))
        Vector.draw(self.vector, Vector.add(self.p,self.mp.t), 1, 0x00ff00)



carte = Carte(
    tuple(
        map(
            lambda x : tuple(map(lambda i: int(i), x.split(','))),
            '35,3,30,-2,28,2,26,1,25,-4,20,1,15,0,5,3,0,0,-10,-1,-10,8,35,8 40,0,38,0,38,2,40,2'.split(' ')
        )
    ),
    (5,10),
    mi/50,
    {}
)

print(carte.points)
print(carte.blocks, "blocks")

chassis = Chassis(
    carte,
    (0,-100),
    ((-20,0),(0,-20),(20,0)),
    20,
    ((-5,5),(5,5),(-15,5),(15,5),(0,-20))
)

RUN = True

while RUN:
    screen.fill(0xffffff)
    for b in carte.radBlocks[chassis.w_r]:
        for w in b.walls:
            w.draw(Vector.subtract(carte.center,carte.relative), 1)
    carte.update()
    carte.relative = chassis.p
    carte.draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN = False
    pygame.display.flip()
    clock.tick(60)
pygame.quit()