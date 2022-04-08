import pygame, time
from math_utils import hypot, mp, sumTuple, Vector, Point, Droite, Circle, Segment, Force, Interval, Triangle
from math import floor, pi, asin, sin, cos, log, sqrt
from variables import screen, resolution, mid_screen, mi

vectors = []

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
        pygame.draw.polygon(screen, 0xff0000, mp(self.points, lambda p,i: Vector.add(p,t)))

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
            # print(Vector.multiply(Vector.add(self.p, v),.05), Vector.multiply(Vector.add(self.q, v),.05))
            return Wall.Line(Vector.add(self.p, v), Vector.add(self.q, v))
        def collides(self, segment:Segment):
            intersect = self.line.intersection(segment.line)
            return segment.p if not intersect else intersect if Point.distance(segment.p, intersect)<=segment.getSize() else False
        def bounce(self, segment:Segment, intersect, bounciness=1):
            q = segment.getQ()
            dist = self.line.distance(q)
            # print('dist',dist)
            npos = Vector.add(q, Vector.multiply(self.u, dist*(1+bounciness)))
            k,l = Vector.multiply(((self.up[0]*segment.v[0]+self.up[1]*segment.v[1]),(self.up[1]*segment.v[0]-self.up[0]*segment.v[1])), self.up[0]**2+self.up[1]**2)
            return (
                npos,
                Vector.subtract(Vector.multiply(self.up,k*bounciness),Vector.multiply((self.up[1],-self.up[0]), l*bounciness)),
                self.up,
                self.u,
                k,l
            )
            # return (npos, Vector.setToNorm(Vector.subtract(npos,intersect), Vector.getNorm(segment.v)*bounciness), self.up, self.vp)
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
            # print('error here?')
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
    def __init__(self, carte, pos, r:float, bounciness:float=.1):
        self.bounciness = bounciness
        self.carte = carte
        self.pos = pos
        self.weight = Force(pos, (0,.1))
        self.forces = [self.weight]
        self.vector = 0,0
        self.nextPos = pos
        self.r = r
        self.bounciness = .5
        self.propellers = (
            Propeller(self, (-r,0)),
            Propeller(self, (+r,0))
        )
    def update(self, keys):
        seg = self.getSegment()
        for i in self.propellers:
            i.update(keys)
        self.vector = Vector.add(self.vector, *mp(self.forces, lambda f,i: f.v), *mp(self.propellers, lambda p,i: p.vector))
        self.pos = Vector.add(self.pos, self.vector)
        walls = self.carte.getWithinWalls(self)
        walls1 = tuple((w.collides(seg), w) for w in walls)
        walls2 = tuple(w for w in walls1 if w[0] and w[1].closeToInterval(w[0]))
        if len(walls2)>0:
            for w in sorted(walls2, key = lambda w: w[0]):
                data = w[1].bounce(seg,w[0], self.bounciness)
                if Vector.isOpposite(Vector.add(self.weight.v, data[1]), data[3]):
                    self.vector = Vector.multiply(data[2],data[4]*self.carte.l)
                    self.pos = Vector.add(Vector.subtract(w[0],Vector.multiply(data[3],-.0005)),self.vector)
                else:
                    self.pos = data[0] # ou w[0], ça rend plus joli mais ça ne marche pas (pas encore)
                    self.vector = Vector.multiply(data[1],1/self.carte.l)
                self.vector = Vector.add(self.vector, Vector.multiply(data[2], (keys[pygame.K_LEFT]-keys[pygame.K_RIGHT])))
        self.vector = Vector.multiply(self.vector,.99)
    def addForce(self, force):
        self.forces.append(force)
    def display(self, t:tuple=(0,0), k:float=1):
        pygame.draw.circle(screen, 0, Vector.add(self.pos,t), self.r, 0xff0000)
        # Vector.draw(self.vector, mid_screen, 0, 1)
    def drawVec(self, t:tuple=(0,0), k:float=1):
        Vector.draw(Vector.multiply(self.vector,k*5), Vector.add(self.pos,t),.5*k,0x00ff00)
    def getSegment(self):
        return Segment(self.pos, self.vector)


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
    def update(self):
        keys = pygame.key.get_pressed()
        for a in self.wheels:
            a.update(keys)
    def draw(self):
        self.t = Vector.subtract(self.center,self.relative)
        for b in self.blocks:
            b.draw(self.t, self.l)
        for w in self.wheels:
            w.display(self.t, self.l)
            w.drawVec(self.t, self.l)

class Propeller:
    def __init__(self, wheel, pos):
        self.power = .1
        self.wheel = wheel
        self.vector = 0,0
        self.pos = pos
    def update(self, keys):
        # print(keys[pygame.K_UP])
        self.vector = 0,(-self.power if keys[pygame.K_UP] else 0)
        if keys[pygame.K_RIGHT]: self.vector = Vector.rotate(self.vector, (sqrt(3)*.4,-.5))
        if keys[pygame.K_LEFT]: self.vector = Vector.rotate(self.vector, (sqrt(3)*.4,.5))
        # print(self.vector)
        self.nextpos = Vector.add(self.pos, self.vector)
    def draw(self, vector:bool=False):
        if vector:
            Vector.draw(self.vector, Vector.add(self.pos,self.wheel.carte.t), 1)
        pygame.draw.line(screen, 0xffff, Vector.add(self.pos,self.wheel.carte.t), Vector.add(self.pos,self.wheel.carte.t, Vector.multiply(self.vector,-10*self.power**.5)), 3)

class Weight:
    def __init__(self, pos):
        self.vector = 0,1
        self.pos = pos
    def update(self):
        self.nextpos = Vector.add(self.pos, self.vector)


class Polygon:
    def __init__(self, path):
        self.path = path
        self.p = Vector.multiply(Vector.add(*path),1/len(path))
        self.orientation = 1,0
        self.weight = Weight(self.p)
    def update(self):
        pass
    def draw(self, c=0xff):
        pygame.draw.polygon(screen, c, tuple(map(lambda pt: Vector.add(self.p, Vector.rotate(pt, self.orientation)),self.path)))