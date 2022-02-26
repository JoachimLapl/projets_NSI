import pygame, time
from variables import screen, clock, mi, mid_screen
import map_utils as mp
from math_utils import Vector


# matrix = (0,0,0,0,0,0,0,0,0,0),(1,0,0,0,0,0,0,0,0,0),(1,2,0,0,0,0,1,2,2,2),(1,1,0,1,1,1,1,2,2,2),(1,1,1,1,1,1,1,1,1,2)
images = {}
with open('images.txt') as f:
    for i in f.readlines()[0].split(' '):
        s = i.split(',')
        images[float(s[1])]=s[0]
print(images)
with open('data.txt') as f:
    carte = mp.Carte(
        tuple(
            map(
                lambda x : tuple(map(lambda i: int(i), x.split(','))),
                f.readlines()[0].split(' ')
            )
        ),
        (5,10),
        mi/10,
        images
    )
print(carte.points)
print(carte.blocks, "blocks")
block = mp.Block(((0,0),(1,-1),(0,-2),(-2,-1),(-1,2),(1,3)))
# print(block.vectors, block.v_ns, block.offset_vectors, sep='\n')

# wheel = mp.Wheel((0,-10),1)
# carte.insert_wheel(wheel)
chassis = mp.Chassis(
    carte,
    (0,-50),
    ((-20,-10),(0,-20),(20,-10)),
    20,
    ((-5,-5),(5,-5),(-15,-5),(15,-5))
)

# chassis = mp.Chassis((0,-10),((-3,0),(3,0),(0,-2)), ((-3,1),(0,1),(3,1)),1) # position, path, wheels_pos, wheels_rad, spring_elas=.5
# carte.insert_chassis(chassis)

RUN = True

while RUN:
    screen.fill(0xffffff)
    # for w in block.elab_walls(1).walls:
    #     w.draw(mid_screen, 50)
    # block.draw(mid_screen, 50)
    # Vector.draw((100,100),(198.29424612264538, 218.90053972500195),3, 0x00ff00)
    carte.update()
    # chassis.update()
    carte.relative = chassis.p
    # chassis.draw()
    # for b in carte.radBlocks[chassis.w_r]:
    #     for w in b.walls:
    #         w.draw(Vector.subtract(carte.center,carte.relative), 1)
    carte.draw()
    # for v in mp.vectors:
    #     Vector.draw(v[0], Vector.add(Vector.subtract(carte.center, carte.relative),Vector.multiply(v[1],carte.l)),1, 0xff0000)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN = False
    pygame.display.flip()
    # time.sleep(.1)
    clock.tick(60)
pygame.quit()