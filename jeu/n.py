import pygame

resolution = 1200,800
mid_res = tuple(map(lambda x:x*.5, resolution))
screen = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()

class Sprite:
    def __init__(self, r, pos:tuple=(0,0)):
        self.x, self.y = pos
        self.r = r
        self.rel_interval = ((-r,r),)*2
        self.speed = 10
        self.relative = (0,0)
        self.recenter = False
    def checkScreenCollision(self, str):
        """ str = 'top' or 'bottom' or 'right' or 'left' """
        if str == 'top':
            return self.y + self.rel_interval[1][0] - self.relative[1] <= 0
        if str == 'bottom':
            return self.y + self.rel_interval[1][1] - self.relative[1] >= resolution[1]
        if str == 'left':
            return self.x + self.rel_interval[0][0] - self.relative[0] <= 0
        if str == 'right':
            return self.x + self.rel_interval[0][1] - self.relative[0] >= resolution[0]
    def checkScreenCollisions(self):
        return (
            self.y + self.rel_interval[1][0] - self.relative[1] <= 0,
            self.y + self.rel_interval[1][1] - self.relative[1] >= resolution[1],
            self.x + self.rel_interval[0][0] - self.relative[0] <= 0,
            self.x + self.rel_interval[0][1] - self.relative[0] >= resolution[0]
        )
    def update(self, keys):
        if self.recenter:
            interactions = self.checkScreenCollisions()
            if interactions[0]:   self.y+=4
            elif interactions[1]: self.y-=4
            else:
                if interactions[2]:   self.x+=4
                elif interactions[3]: self.x-=4
                else: self.recenter = False
            return True
        else:
            if keys[pygame.K_LEFT]: self.x-=self.speed
            if keys[pygame.K_RIGHT]:self.x+=self.speed
            if keys[pygame.K_UP]:   self.y-=self.speed
            if keys[pygame.K_DOWN]: self.y+=self.speed
        return False
    def draw(self):
        print(self.relative)
        pygame.draw.circle(screen, 0, (self.x-self.relative[0],self.y-self.relative[1]), self.r)

class Interval:
    def __init__(self,value1:float,value2:float, type:tuple=(True,True)):
        assert value1<value2, "impossible de créer un tel interval"
        self.data = [type[0],value1,value2, type[1]]
    def toText(self):
        return ('[' if self.data[0] else ']')+(';'.join(map(str, self.data[1:3])))+(']' if self.data[3] else '[')
    def isWithin(self, value):
        return (value >= self.data[1] if self.data[0] else value > self.data[1]) and (value <= self.data[2] if self.data[3] else value < self.data[2])

class Tile:
    def __init__(self, name:str, pos, *portals):
        self.image = Images.load_image(name)
        self.portals = portals
        for i in (0,1,2,3):
            for p in self.portals[i]:
                for j in (1,2):
                    p[0].data[j]*= resolution[0 if i<2 else 1]
        self.pos = pos[0]*resolution[0],pos[1]*resolution[1]

class Images:
    @classmethod
    def load_image(cl, str):
        return pygame.transform.scale(pygame.image.load(str), resolution)
    def __init__(self):
        self.tile_n = 0;
        self.tiles = (
            Tile('yellow_tile.png', (0,0), ((Interval(0,.33),1),(Interval(.67,1),2)),(),(),()),
            Tile('blue_tile.png'   , (-.5,-1), (),((Interval(.5,.83), 0),),(),((Interval(.25,.75), 2),)),
            Tile('red_tile.png'  , (.5,-1), (),((Interval(.167,.5), 0),),((Interval(.25,.75), 1),),()),
        )
    def draw(self):
        screen.blit(self.tiles[self.tile_n].image, (0,0)+resolution)
    def withinTilePortal(self, sprite:Sprite):
        interactions = sprite.checkScreenCollisions()
        for i in (0,1,2,3):
            if interactions[i]:
                for p in self.tiles[self.tile_n].portals[i]:
                    if p[0].isWithin(sprite.x-sprite.relative[0] if i<2 else sprite.y-sprite.relative[1]):
                        self.tile_n = p[1]
                        sprite.relative = self.tiles[p[1]].pos
                        sprite.recenter = True
                        return

sprite = Sprite(30,mid_res)
images = Images()

RUN = True

while RUN:
    no_portals = sprite.update(pygame.key.get_pressed())
    if not no_portals: images.withinTilePortal(sprite)
    images.draw()
    sprite.draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN = False
    pygame.display.flip()
    # time.sleep(.1)
    clock.tick(60)
pygame.quit()