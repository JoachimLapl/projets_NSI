import pygame
from math import pi

resolution = (600,400)
screen = pygame.display.set_mode(resolution)
mid_screen = tuple(i/2 for i in resolution)

p2 = pi / 2
keys = {}
onmousedown = ({ key }) => keys[key] = true;
onmouseup = ({ key }) => keys[key] = false;
onmousemove = ({ x, y }) => { mouseposition.x = x; mouseposition.y = y };

def sumTuple(t, callback = lambda x : x):
    S = 0
    for i in t:
        S += callback(i)
    return S

def hypot(*p):
    return sumTuple(p, lambda x:x**2)**.5
    


class Map:
    def __init__(self, height=100, width=100):
        self.height=height
        self.width=width

class MotionPoint:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.traits_v = ()
        self.v = [0, 0]
    def addTrait(self, vector):
        self.traits_v.push+=(vector,)
    def update(self):
        for v in self.traits_v:
            self.v[0] += v[0]
            self.v[1] += v[1]
        self.v[1] += .1
        self.pos[0] += self.v[0]
        self.pos[1] += self.v[1]
        if (self.pos[1] > mid_screen[1]) self.pos[1] = mid_screen
        self.v[0] *= .95
        self.v[1] *= .95

class Trait:
    def __init__(self, p1, p2, size, elasticity):
        self.p1 = p1
        self.p2 = p2
        self.size = size
        self.v1 = [0, 0]
        p1.addTrait(self.v1)
        self.v2 = [0, 0]
        p2.addTrait(self.v2)
        self.elas = 1 - elasticity
    def update(self):
        a = self.p1.pos[0] - self.p2.pos[0]
        b = self.p1.pos[1] - self.p2.pos[1]
        h = hypot(a, b)
        s = (h - self.size) / 2 * self.elas / h 
        a *= s
        b *= s
        self.v1[0] -= a
        self.v1[1] -= b
        self.v2[0] += a
        self.v2[1] += b
    def display(self):
        # self.el.x1.baseVal.value = self.p1.pos[0]
        # self.el.y1.baseVal.value = self.p1.pos[1]
        # self.el.x2.baseVal.value = self.p2.pos[0]
        # self.el.y2.baseVal.value = self.p2.pos[1]
        self.reset()
    def reset(self):
        self.v1[0] = 0
        self.v1[1] = 0
        self.v2[0] = 0
        self.v2[1] = 0

class Wheel(MotionPoint):
    def __init__(self, x, y):
        super(x, y)
    def display(self):
        pygame.draw.circle(srceen, )

Map()

const wheels = [
    new Wheel(-24, 0, $('#w1', svg)),
    new Wheel(-8, 0, $('#w2', svg)),
    new Wheel(8, 0, $('#w3', svg)),
    new Wheel(24, 0, $('#w4', svg))
];
const points = [
    new MotionPoint(-12, -12),
    new MotionPoint(0, -12),
    new MotionPoint(12, -12)
];
e = .9
Object.defineProperties(window, {
    r: {
        get: function () {
            return Math.random() * 10 + 10
        }
    }
})
const traits = [
    new Trait(wheels[0], wheels[1], r, e, $('#trait1', svg)),
    new Trait(wheels[1], wheels[2], r, e, $('#trait2', svg)),
    new Trait(wheels[2], wheels[3], r, e, $('#trait3', svg)),
    new Trait(wheels[0], points[0], r, e, $('#trait4', svg)),
    new Trait(wheels[1], points[0], r, e, $('#trait5', svg)),
    new Trait(wheels[1], points[1], r, e, $('#trait6', svg)),
    new Trait(wheels[2], points[1], r, e, $('#trait7', svg)),
    new Trait(wheels[2], points[2], r, e, $('#trait8', svg)),
    new Trait(wheels[3], points[2], r, e, $('#trait9', svg)),
    new Trait(points[0], points[1], r, e, $('#trait10', svg)),
    new Trait(points[1], points[2], r, e, $('#trait11', svg))
];


[...wheels, ...traits].forEach(e => e.display());
(loop = () => {
    //orient.children[1].innerText = mouseposition.x
    //	orient.children[2 ].innerText = mouseposition.y
    requestAnimationFrame(loop);
    [...traits, ...wheels, ...points].forEach(e => e.update());
    [...wheels, ...traits].forEach(e => e.display());

})();