from tests.locals import *

tSetBase = """
TerminationSet
    SpriteCounter stype=avatar limit=0 win=False
"""

levelMapping = """
LevelMapping
	1 > box
	2 > box2
	3 > box3
	w > wall
	c > cannon
	A > avatar
"""


sSetBoxes = """
SpriteSet
    avatar > MovingAvatar color=DARKBLUE
    box	 > Immovable color=WHITE 
    box2 > Immovable color=GREEN
    box3 > Immovable color=YELLOW
    wall > Immovable color=DARKGRAY
"""

sSetCannons = joinDescs(sSetBoxes, """
SpriteSet
    cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
    sam > Missile orientation=UP color=BLUE singleton=False cooldown=1
""")

iSetBoxes = """
InteractionSet
    avatar wall > stepBack
    box avatar > transformTo stype=box2
    # Need to include all step backs
"""

iSetCannons = joinDescs(iSetBoxes, """
InteractionSet
    cannon avatar > bounceForward
    avatar sam > bounceForward
    # cannon sam > stepBack
    # sam cannon > stepBack
    # need to include additional stepbacks
""")

# print iSetCannons.__repr__()

iSetWeird = joinDescs(iSetCannons, """
InteractionSet
	cannon sam > stepBack
	sam cannon > stepBack
""")
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


gameBoxes = catDescriptions(sSetBoxes, iSetBoxes, tSetBase, levelMapping)

gameCannons = catDescriptions(sSetCannons, iSetCannons, tSetBase, levelMapping)
gameWeird = catDescriptions(sSetCannons, iSetWeird, tSetBase, levelMapping)
# print 
# print game

game = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE 
        box2 > Immovable color=GREEN
        box3 > Immovable color=YELLOW
        wall > Immovable color=DARKGRAY
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
        sam > Missile orientation=UP color=BLUE single=False cooldown=1
        avatar  > MovingAvatar color=DARKBLUE 
    LevelMapping
        1 > box
        2 > box2
        3 > box3
        w > wall
        c > cannon
        A > avatar
    InteractionSet
        avatar wall > stepBack
        box avatar > transformTo stype=box2
        box2 avatar > killSprite
        box3 avatar > killSprite
        # Need to include all step backs
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""

level0 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                            1 w
w                            1 w
w              c   A           w
w  c                           w
w                         3 3  w
w         c                    w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""
test0 = TestCase(game, level0, [[K_LEFT]])


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

        # box avatar > stepBack
        # avatar box > stepBack
        # box2 avatar > stepBack
        # avatar box2 > stepBack

        avatar wall > stepBack
        wall avatar > stepBack

        # box box2 > stepBack
        # box2 box > stepBack
        box wall > stepBack
        wall box > stepBack
        box2 wall > stepBack
        wall box2 > stepBack


        box box > stepBack
        avatar avatar > stepBack
        wall wall > stepBack
        box2 box2 > stepBack

        box EOS > stepBack
        box2 EOS > stepBack
        wall EOS > stepBack
        avatar EOS > stepBack


        # Need to include all step backs
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
        SpriteCounter stype=box limit=0 win=True
"""
test1 = TestCase(gameBoxes, level1, [[K_UP]*4+[K_LEFT]], test1_theory)



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
test2_theory = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE 
        box2 > Immovable color=GREEN
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
        sam > Missile orientation=UP color=BLUE singleton=False cooldown=1
    LevelMapping
        1 > box
        2 > box2
        A > avatar
    InteractionSet
        
        box avatar > transformTo stype=box2

        # box avatar > stepBack
        # avatar box > stepBack
        # box2 avatar > stepBack
        # avatar box2 > stepBack

        avatar wall > stepBack
        wall avatar > stepBack

        box box2 > stepBack
        box2 box > stepBack
        box wall > stepBack
        wall box > stepBack
        box2 wall > stepBack
        wall box2 > stepBack


        box box > stepBack
        avatar avatar > stepBack
        wall wall > stepBack
        box2 box2 > stepBack

        box EOS > stepBack
        box2 EOS > stepBack
        wall EOS > stepBack
        avatar EOS > stepBack


        # Need to include all step backs
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
        SpriteCounter stype=box limit=0 win=True
"""
test2 = TestCase(gameBoxes, level1, [[0]*6], test2_theory)

# TODO: You need to be able to re-run testAndExpand() when no hypotheses pass your filter
## the problem here is that you need to build on expandSprite proposals with expandLine within one errorMap and
## you don't ordinarily do that.
#0,0,0,0,0,0
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

test3 = TestCase(gameBoxes, level3, [[0]*6])

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
test4 = TestCase(gameBoxes, level4, [[0]*3+[K_LEFT]*2+[0]*2])

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
test5 = TestCase(gameBoxes, level5, [[K_UP, K_UP, K_DOWN]])

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
test6 = TestCase(gameBoxes, level6, [[0]*7])

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                       1      w
# w                       1      w
# w1111111111    C        1111111w
# w         1   C2C           2  w
# w         1    C               w
# w              A               w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                              w
# w                              w
# w                              w
# w            1 C               w
# w                              w
# w                      A       w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """