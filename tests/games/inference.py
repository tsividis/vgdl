from tests.locals import *

game="""
BasicGame
    SpriteSet
        cloner > Immovable color=GREEN
        box    > Immovable color=WHITE # orientation=RIGHT cooldown=1
        box2 > Immovable color=GREEN
        box3 > Immovable color=YELLOW
        flicker > Flicker timeout=1 color=ORANGE
        random > RandomNPC color=PURPLE speed=1 cooldown=1
        chaser > Chaser color=BLACK speed=1 cooldown=1 stype=box
        avatar  > MovingAvatar color=DARKBLUE 
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
        missile > Missile
            sam  > orientation=UP color=BLUE singleton=False cooldown=1
        wall > Immovable color=DARKGRAY
    LevelMapping
        C > cloner
        F > flicker
        0 > base
        1 > box
        2 > box2
        3 > box3
        4 > random
        w > wall
        c > cannon
        s > sam
        A > avatar
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

    TerminationSet
        SpriteCounter stype=box3 limit=0 win=True
        # SpriteCounter stype=box3 limit=0 win=False
        Termination


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
test1 = TestCase(game, level1, [[K_UP]*4+[K_LEFT]], test1_theory)



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
        box3 > Immovable color=YELLOW
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
        sam > Missile orientation=UP color=BLUE singleton=False cooldown=1 speed=1
    InteractionSet

        avatar sam > bounceForward



        # Need to include all step backs
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""
test2 = TestCase(game, level2, [[0]], test2_theory)

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

test3_theory = """
BasicGame
    SpriteSet
        box > Immovable color=WHITE 
        box3 > Immovable color=YELLOW
        wall > Immovable color=DARKGRAY
        avatar  > MovingAvatar color=DARKBLUE
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
        sam > Missile orientation=UP color=BLUE singleton=False cooldown=1 speed=1

    InteractionSet

        avatar sam > bounceForward



        # Need to include all step backs
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""

test3 = TestCase(game, level3, [[0]*6])

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
test4 = TestCase(game, level4, [[0]*3+[K_LEFT]*2+[0]*2])