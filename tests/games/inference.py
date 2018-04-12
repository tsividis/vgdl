from tests.locals import *

# print iSetWeird.__repr__()

'''
The original interaction set

InteractionSet
    avatar wall > stepBack
    # box avatar > nothing
    box avatar > transformTo stype=box2
    # cannon sam > stepBack
    # sam cannon > stepBack
    box2 avatar > killSprite
    # box2 avatar > bounceForward
    box3 avatar > killSprite
    cannon avatar > bounceForward
    avatar sam > bounceForward
    cannon sam > stepBack
    sam cannon > stepBack
'''

base_game = """
SpriteSet
    avatar  > MovingAvatar color=DARKBLUE
    cloner > Immovable color=GREEN
    box    > Immovable color=WHITE # orientation=RIGHT cooldown=1
    box2 > Immovable color=GREEN
    box3 > Immovable color=YELLOW
    box5 > Immovable color=LIGHTBLUE
    flicker > Flicker timeout=1 color=ORANGE
    random > RandomNPC color=PURPLE speed=1 cooldown=2
    chaser > Chaser color=BLACK speed=1 cooldown=4 stype=avatar fleeing=True
    cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
    missile > Missile
        sam  > orientation=UP color=BLUE singleton=False cooldown=1
    wall > Immovable color=DARKGRAY
    medicine > Resource limit=4 color=GREEN
    poison > Resource limit=3 color=PINK
    invisiblemedicine > Resource limit=4 color=PURPLE
LevelMapping
    C > cloner
    F > flicker
    0 > base
    1 > box
    2 > box2
    3 > box3
    4 > random
    5 > box5
    w > wall
    c > cannon
    s > sam
    k > chaser
    A > avatar
    m > medicine
    p > poison
TerminationSet
    SpriteCounter stype=avatar limit=0 win=False
"""

# level0 = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w              c   A           w
# w  c                           w
# w                         3 3  w
# w         c                    w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# test0 = TestCase(base_game, level0, [[K_LEFT]])

#########################################################
#########################################################
game1 = catDescriptions(base_game, """
InteractionSet
    box avatar > transformTo stype=box2
    box2 avatar > nothing
""")

# up, up, up, up, left
level1 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w              1             1 w
w                            1 w
w              2               w
w                    2         w
w              A               w
w                              w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

test1_theory = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE 
        box2 > Immovable color=GREEN
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE 
    LevelMapping
        1 > box
        2 > box2
        A > avatar
    InteractionSet
        
        box avatar > transformTo stype=box2
        box2 avatar > nothing
        
        # step backs for non interacting sprites are automatically added
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
        SpriteCounter stype=box limit=0 win=True
"""
test1 = TestCase(game1, level1, [[K_UP]*4+[K_LEFT]], test1_theory)


#########################################################
#########################################################

game2 = catDescriptions(base_game, """
InteractionSet
    avatar sam > bounceForward
    sam wall > reverseDirection
""")

#combine with avatar sam bounceFoward. works.
#0,0,0,0,0,0
level2 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                            1 w
w                            1 w
w                              w
w              A               w
w                         3 3  w
w         c    c               w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

test_theory2 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE 
        box3 > Immovable color=GREEN
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE 
        sam > Missile orientation=UP color=BLUE singleton=FALSE cooldown=1
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
    InteractionSet
        avatar sam > bounceForward

    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""
test2 = TestCase(game2, level2, [[0]*6], test_theory2)


#########################################################
#########################################################

# TODO: You need to be able to re-run testAndExpand() when no hypotheses pass your filter
## the problem here is that you need to build on expandSprite proposals with expandLine within one errorMap and
## you don't ordinarily do that.
#0,0,0,0,0,0

game3 = catDescriptions(base_game, """
InteractionSet
    box avatar > bounceForward
""")
level3 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                            1 w
w                            1 w
w                              w
w                              w
w              A          3 3  w
w         c    c               w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

test_theory3 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE 
        box3 > Immovable color=GREEN
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE 
        sam > Missile orientation=UP color=BLUE singleton=FALSE cooldown=1
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
    InteractionSet
        avatar sam > bounceForward

    TerminationSet
        SpriteCounter stype=avatar limet=0 win=False
"""

test3 = TestCase(game3, level3, [[0]*6], test_theory3)


#########################################################
#########################################################

game4 = catDescriptions(base_game, """
InteractionSet
    avatar sam > bounceForward
    canon avatar > bounceForward
""")

# works if you don't allow the eventHandler to apply effects to newly-created sprites
#[0,0,0,K_LEFT, K_LEFT,0,0]
level4 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                            1 w
w                            1 w
w                              w
w                              w
w                         3 3  w
w         c    c A             w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

test_theory4 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE 
        box3 > Immovable color=GREEN
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE 
        sam > Missile orientation=UP color=BLUE singleton=FALSE cooldown=1
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
    InteractionSet
        canon avatar > bounceForward

    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""

test4 = TestCase(base_game, level4, [[0]*3+[K_LEFT]*2+[0]*2], test_theory4)


#########################################################
#########################################################

game5 = catDescriptions(base_game,
"""
InteractionSet
    box avatar > transformTo stype=box2
""")

# #up, up, down
level5 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                            1 w
w                            1 w
w              1               w
w              1               w
w              A          3 3  w
w                              w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""
test5 = TestCase(base_game, level5, [[K_UP, K_UP, K_DOWN]])


#########################################################
#########################################################

#0,0,0,0,0,0,0
level6 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                            1 w
w                            1 w
w              1               w
w              1               w
w              A          3 3  w
w   c   c                      w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""
test6 = TestCase(base_game, level6, [[0]*7])


#########################################################
#########################################################


# distinguishing between random and missiles
level7 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                            1 w
w                     4      1 w
w                              w
w   4                          w
w                         3 3  w
w         s    s A             w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

test7 = TestCase(base_game, level7, [[0]*10])


#########################################################
#########################################################

# combine with sam wall reverseDirection
# we do learn reverseDirection, but a few
# incorrect Chaser theories have low error even though they're totally wrong.
level8 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                            1 w
w                            1 w
w                              w
w         wwwwww               w
w                         3 3  w
w         s    s A             w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

test8 = TestCase(base_game, level8, [[0]*10])

#########################################################
#########################################################

# level9 = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w        4                   1 w
# w              k             1 w
# w      4           A           w
# w                              w
# w          k              3 3  w
# w                       s  s   w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# test9 = TestCase(base_game, level9, [])


#########################################################
#########################################################

# level10 = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w                              w
# w         wwwwww               w
# w                              w
# w       5      5 A 3  3        w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# test10 = TestCase(base_game, level10, [])


#########################################################
#########################################################

#randomnpc inference, just more sprites
level11 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w    4                       1 w
w         4           4      1 w
w                              w
w   4         4                w
w                         3 3  w
w                A             w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

test11 = TestCase(base_game, level11, [[0]*10])


#########################################################
#########################################################

#up, up, up, right
## tests whether we can learn randomNPCs and know that the box we push isn't a randomNPC
## i.e., a good test of randomNPC likelihood and theory prior().
level12 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                           3  w
w                 2            w
w          4                3  w
w                      2       w
w     4                        w
w                      A       w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

test12 = TestCase(base_game, level12, [[K_UP]*3+[K_RIGHT]])


#########################################################
#########################################################

# Not getting this one because we stepBack with the missile
## but our best theories are almost right.
#left, left, left, left, left, left, left, 0
level13 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                            1 w
w                            1 w
w            c    A            w
w  c                           w
w                         3 3  w
w         c                    w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

test13 = TestCase(base_game, level13, [[K_LEFT]*7+[0]])


#########################################################
#########################################################

# #up, up
level14 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                            1 w
w                            1 w
w              m               w
w              m               w
w              A          3 3  w
w                              w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

test14 = TestCase(base_game, level14, [[K_UP]*2])


#########################################################
#########################################################


level15 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w              p             1 w
w              m             1 w
w              m               w
w              p               w
w              A          3 3  w
w                              w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

test15 = TestCase(base_game, level15, [[K_UP]*4])


#########################################################
#########################################################


level16 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w              p             1 w
w              m             1 w
w              m               w
w                              w
w             pA          3 3  w
w                              w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

test16 = TestCase(base_game, level16, [[K_LEFT]+[K_UP]*4])



#########################################################
#########################################################