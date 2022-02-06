import pygame, time
from math_utils import hypot, mp, sumTuple, Vector, Point, Droite, Circle, Segment, Force, Interval
from math import floor, pi, asin, sin, cos
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
        pygame.draw.polygon(screen, 0xff0000, mp(self.points, lambda p,i: Vector.add(Point.homothetia(p,k),t)))

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
            # print('dist',dist)
            npos = Vector.add(q, Vector.multiply(self.u, dist*(1+bounciness)))
            return (npos, Vector.setToNorm(Vector.subtract(npos,intersect), Vector.getNorm(segment.v)*bounciness), self.up)
        def draw(self, t:tuple = (0,0), k:float = 1):
            pygame.draw.line(screen, 0, Vector.add(Vector.multiply(self.p,k),t), Vector.add(Vector.multiply(self.q,k),t), width=1)
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
            drt = Droite(*v, -v[0]*intersect[0]-v[1]*intersect[1])
            q = segment.getQ()
            print('error here?')
            dist = drt.distance(q)
            npos = Vector.add(q, Vector.multiply(v, dist*(1+bounciness)))
            return (npos, Vector.setToNorm(Vector.subtract(npos,intersect), Vector.getNorm(segment.v)*bounciness), (v[1],-v[0]))
        def draw(self, t:tuple = (0,0), k:float = 1):
            pygame.draw.circle(screen, 0, Vector.add(Vector.multiply(self.p,k),t), self.r*k)
        def closeToInterval(self,point, err=.01):
            return self.interval[0][0]-err>point[0]>self.interval[0][1]+err and self.interval[1][0]-err>point[1]>self.interval[1][1]+err


class Wheel:
    def __init__(self, pos, r:float):
        self.pos = pos
        self.weight = Force(pos, (0,.01))
        self.forces = [self.weight]
        self.vector = 0,0
        self.nextPos = pos
        self.r = r
        self.bounciness = .5
    def update(self, carte, leftArrow, rightArrow):
        seg = self.getSegment()
        self.vector = Vector.add(self.vector, *mp(self.forces, lambda f,i: f.v))
        self.pos = Vector.add(self.pos, self.vector)
        walls = carte.getWithinWalls(self)
        walls1 = tuple((w.collides(seg), w) for w in walls)
        walls2 = tuple(w for w in walls1 if w[0] and w[1].closeToInterval(w[0]))
        if len(walls2)>0:
            for w in sorted(walls2, key= lambda w: w[0]):
                data = w[1].bounce(seg,w[0], self.bounciness)
                self.pos = data[0] # ou w[0], ça rend plus joli mais ça ne marche pas (pas encore)
                self.vector = Vector.add(data[1],Vector.multiply(data[2], (leftArrow-rightArrow)*.05))
        self.vector = Vector.multiply(self.vector,.99)
    def addForce(self, force):
        self.forces.append(force)
    def display(self, t:tuple=(0,0), k:float=1):
        pygame.draw.circle(screen, 0, Vector.add(Vector.multiply(self.pos,k),t), self.r*k, 0xff0000)
        # Vector.draw(self.vector, mid_screen, 0, 1)
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

class Chassis:
    def __init__(self, position, path, wheels_pos, wheels_rad, spring_elas=.5):
        self.pos = position
        self.path = path
        self.w_p = wheels_pos
        self.w_dist = mp(wheels_pos, lambda p,i: sumTuple(p,lambda x:x*x)**.5)
        self.wheels = mp(wheels_pos, lambda p,i: Wheel(p,wheels_rad))
        self.springs = tuple(map(lambda p,q: Ressort(p,q,spring_elas,0)))
        self.weight = Force((0,1),self.pos)
        self.vector = 0,0
        self.orientation = 0
        self.rotationIndex = 0
    def update(self, carte, leftArrow, rightArrow):
        for w in self.wheels:
            w.update()
        w_pos = mp(self.w_p, lambda p,i: Vector.add(Point.rotate(p, self.orientation),self.pos))
        forces = ((self.pos, self.weight),) + tuple(map(lambda s,p: (p,s.v1), self.springs, w_pos))
        self.pos = Vector.add(
            Vector.multiply(self.vector,.1),
            Vector.multiply(Vector.add(self.weight.nextPos,*map(lambda w: w.nextPos, self.wheels),1/(len(self.wheels)+1)))
        )
        self.weight.p = self.pos
        r_offset = mp(self.wheels, lambda w,i: Vector.getAngle(Vector.subtract(w.nextPos, self.pos)) - Vector.getAngle(Vector.subtract(w.pos, self.pos)))
        self.rotateIndex += r_offset
        self.orientation += self.rotateIndex * .1 + r_offset
        self.vector = Vector.multiply(self.vector, .99)
        self.rotationIndex *= .95
    def display(self):
        pts = mp(self.path, lambda p,i: Point.rotate(p,self.orientation))
        pygame.draw.polygon(screen, 0, pts)
        for w in self.wheels:
            w.display()


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
                (d[i*2],d[i*2+1]) for i in range(l)
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
    def insert_chassis(self, chassis:Chassis):
        if chassis.w_r not in self.radBlocks.keys():
            self.radBlocks[chassis.w_r] = mp(self.blocks, lambda b,i: b.elab_walls(chassis.w_r))
        self.chassis += (chassis,)
    def update(self):
        keys = pygame.key.get_pressed()
        for a in (self.chassis+self.wheels):
            a.update(self, keys[pygame.K_LEFT], keys[pygame.K_RIGHT])
    def draw(self):
        t = Vector.subtract(self.center,self.relative)
        for b in self.blocks:
            b.draw(t, self.l)
        for w in self.wheels:
            w.display(t, self.l)
            w.drawVec(t, self.l)
        for c in self.chassis:
            c.display(t, self.l)


