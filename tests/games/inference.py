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
    Termination
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

expected_theory1 = """
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
test1 = TestCase(game1, level1, [[K_UP]*4+[K_LEFT]], expected_theory1)


#########################################################
#########################################################

game2 = catDescriptions(base_game, """
InteractionSet
    avatar sam > bounceForward
    sam wall > reverseDirection
""")

# Getting this after sam spawns
# Warning. In initializeVrle. Got more than one avatar. Returning None as Vrle.

# We're passing a list of VRLEs that contains None, 
# and it's being executed at vgdl\agent.py, line 2109, env.step(action)
# env is 'NoneType'

#combine with avatar sam bounceFoward. works.
#0,0,0,0,0,0
level2 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                            1 w
w              A             1 w
w                              w
w                              w
w         c    c          3 3  w
w                              w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

expected_theory2 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE 
        box3 > Immovable color=YELLOW
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE 
        sam > Missile orientation=UP color=BLUE singleton=False cooldown=1
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
        avatar  > MovingAvatar color=DARKBLUE
    InteractionSet
        avatar sam > bounceForward

    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""
test2 = TestCase(game2, level2, [[0]*6], expected_theory2)


#########################################################
#########################################################

# This also detects multiple sprites

# TODO: You need to be able to re-run testAndExpand() when no hypotheses pass your filter
## the problem here is that you need to build on expandSprite proposals with expandLine within one errorMap and
## you don't ordinarily do that.
#0,0,0,0,0,0

game3 = catDescriptions(base_game, """
InteractionSet
    avatar sam > bounceForward
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

expected_theory3 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE 
        box3 > Immovable color=YELLOW
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE 
        sam > Missile orientation=UP color=BLUE singleton=False cooldown=1
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
        avatar  > MovingAvatar color=DARKBLUE
    InteractionSet
        avatar sam > bounceForward

    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""

test3 = TestCase(game3, level3, [[0]*6], expected_theory3)


#########################################################
#########################################################

game4 = catDescriptions(base_game, """
InteractionSet
    cannon avatar > bounceForward
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

expected_theory4 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE 
        box3 > Immovable color=YELLOW
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE 
        sam > Missile orientation=UP color=BLUE singleton=FALSE cooldown=1
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
        avatar  > MovingAvatar color=DARKBLUE
    InteractionSet
        cannon avatar > bounceForward

    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""

test4 = TestCase(game4, level4, [[0]*3+[K_LEFT]*2+[0]*2], expected_theory4)


#########################################################
#########################################################

game5 = catDescriptions(base_game,"""
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

expected_theory5 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE 
        box2 > Immovable color=GREEN
        box3 > Immovable color=YELLOW
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE
    InteractionSet
        box avatar > transformTo stype=box2
        avatar box2 > nothing
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
        SpriteCounter stype=box limit=0 win=True

"""

test5 = TestCase(game5, level5, [[K_UP, K_UP, K_DOWN]], expected_theory5)


#########################################################
#########################################################

game6 = catDescriptions(base_game, """
InteractionSet
    sam wall > reverseDirection
""")

#0,0,0,0,0,0,0,0,0,0,0
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

expected_theory6 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE 
        box3 > Immovable color=YELLOW
        wall > Immovable color=DARKGRAY
        sam > Missile orientation=UP color=BLUE singleton=FALSE cooldown=1
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
        avatar  > MovingAvatar color=DARKBLUE
    InteractionSet
        sam wall > reverseDirection
        # Should get to the step where this happens
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""
test6 = TestCase(game6, level6, [[0]*10], expected_theory6)


#########################################################
#########################################################

game7 = catDescriptions(base_game, """
InteractionSet
    # sam wall > reverseDirection
""")

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

expected_theory7 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE
        box3 > Immovable color=YELLOW
        random > RandomNPC color=PURPLE speed=1 cooldown=2
        sam > Missile orientation=UP color=BLUE singleton=False cooldown=1
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE
    InteractionSet
        # sam wall > reverseDirection
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""

test7 = TestCase(game7, level7, [[0]*10], expected_theory7)


#########################################################
#########################################################

game8 = catDescriptions(base_game, """
InteractionSet
    sam wall > reverseDirection
""")

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

expected_theory8 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE
        box3 > Immovable color=YELLOW
        sam > Missile orientation=UP color=BLUE singleton=False cooldown=1
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE
    InteractionSet
        sam wall > reverseDirection
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""

test8 = TestCase(game8, level8, [[0]*10], expected_theory8)

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

game11 = catDescriptions(base_game, """
InteractionSet
    box avatar > nothing
""")

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

expected_theory11 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE
        box3 > Immovable color=YELLOW
        random > RandomNPC color=PURPLE speed=1 cooldown=2
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""

test11 = TestCase(game11, level11, [[0]*10], expected_theory11)


#########################################################
#########################################################

game12 = catDescriptions(base_game, """
InteractionSet
    box2 avatar > bounceForward
""")

#up, up, up, right, 
## tests that the box we push isn't a randomNPC
## i.e., a good test of randomNPC likelihood and theory prior().
level12 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                           3  w
w                 2            w
w                           3  w
w                      2       w
w                              w
w                      A       w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

expected_theory12 = """
BasicGame
    SpriteSet
        box2 > Immovable color=GREEN
        box3 > Immovable color=YELLOW
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE
    InteractionSet
        box2 avatar > bounceForward
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""

test12 = TestCase(game12, level12, [[K_UP]*3+[K_RIGHT]+[0]*4], expected_theory12)


#########################################################
#########################################################

game13 = catDescriptions(base_game, """
InteractionSet
    cannon sam > stepBack
    sam cannon > stepBack
    cannon avatar > bounceForward
    avatar sam > bounceForward
""")

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

expected_theory13 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE
        box3 > Immovable color=YELLOW
        sam > Missile orientation=UP color=BLUE singleton=FALSE cooldown=1
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE
    InteractionSet
        cannon avatar > bounceForward
        sam wall > nothing
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""

test13 = TestCase(game13, level13, [[K_LEFT]*7+[0]], expected_theory13)


#########################################################
#########################################################

game14 = catDescriptions(base_game, """
InteractionSet
    medicine avatar > killSprite
    avatar medicine > changeResource resource=medicine value=1
""")

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

expected_theory14 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE
        box3 > Immovable color=YELLOW
        medicine > Resource limit=4 color=GREEN
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE
    InteractionSet
        medicine avatar > killSprite
        avatar medicine > changeResource resource=medicine value=1 limit=4
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""

test14 = TestCase(game14, level14, [[K_UP]*2], expected_theory14)


#########################################################
#########################################################

game15 = catDescriptions(base_game, """
InteractionSet
    avatar poison > killIfHasMore resource=medicine limit=0
    # poison avatar > killSprite # Do we not include this?
    medicine avatar > killSprite
    avatar medicine > changeResource resource=medicine value=1
    avatar poison > changeResource resource=medicine value=-1
""")

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

expected_theory15 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE
        box3 > Immovable color=YELLOW
        medicine > Resource limit=4 color=GREEN
        poison > Resource limit=3 color=PINK
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE
    InteractionSet
        avatar poison > killIfHasMore resource=medicine limit=0
        # poison avatar > killSprite # Do we not include this?
        medicine avatar > killSprite
        avatar medicine > changeResource resource=medicine value=1 limit=4
        avatar poison > changeResource resource=medicine value=-1 limit=4
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""

test15 = TestCase(game15, level15, [[K_UP]*4], expected_theory15)


#########################################################
#########################################################

game16 = catDescriptions(base_game, """
InteractionSet
    poison avatar > killIfOtherHasMore resource=medicine limit=0
    avatar poison > changeResource resource=medicine limit=0
""")

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

expected_theory16 = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE
        box3 > Immovable color=YELLOW
        medicine > Immovable color=GREEN
        poison > Resource limit=3 color=PINK
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE
    InteractionSet
        avatar poison > changeResource resource=medicine limit=4 value=1 
        poison avatar > killSprite # doesn't learn the 'ifHasMore'
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
        SpriteCounter stype=poison limit=0 win=True  
        # Should we add this last rule if it reduces our resources?
"""
test16 = TestCase(game16, level16, [[K_LEFT]+[K_UP]*4], expected_theory16)



#########################################################
#########################################################
