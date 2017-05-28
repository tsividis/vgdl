# level = """
# wwwwwwwwwwwww
# wA     x    w
# w b         w
# w           w
# w          aw
# wwwwwwwwwwwww
# """

level0 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                              w
w                              w
w                              w
w                              w
wm A b                        aw
www                            w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level1 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                              w
w  b                           w
w                              w
w                              w
wm A                          aw
www                            w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                              w
w  b                           w
w                              w
w                              w
wr A                          aw
www                            w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""


level3 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w     a       b    a      a    w
w                              w
w  b            a     a        w
w              A m             w
w     a     a                  w
w     b                       aw
www                  a         w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level4 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w  a                           w
w     a       b    a      a    w
w       a              fffff   w
w  b        m   a     af   f   w
w              A       f   f   w
w     a     a          fffff   w
w     a   a       b      a    aw
www                  a         w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

game = """
BasicGame frame_rate=30
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE cooldown=6
        box > Passive
            box1 > color=RED
            box2 > color=ORANGE
        chaser > VGDLSprite cooldown=16
            randomChaser > RandomNPC color=LIGHTBLUE
            mediumChaser > Chaser color=BLUE stype=box2
            goodChaser > AStarChaser color=PINK stype=box2
        forcefield > Passive color=PURPLE
        wall > Immovable color=DARKGRAY
    LevelMapping
        w > wall
        a > box1
        b > box2
        m > mediumChaser
        r > randomChaser
        s > goodChaser
        f > forcefield
    InteractionSet
        avatar wall > stepBack
        mover wall > stepBack
        avatar mover > stepBack
        box wall > stepBack
        box2 avatar > bounceForward
        box2 forcefield > nothing
        chaser forcefield > stepBack
        avatar forcefield > nothing
        box2 box1 > stepBack
        avatar chaser > nothing
        box1 avatar > killSprite
        box2 chaser > killSprite
        chaser wall > stepBack
        chaser box1 > nothing
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False
        SpriteCounter stype=box2  limit=0 win=False
        SpriteCounter stype=box1 limit=0 win=True
"""

level_game_pairs = [[game, level0], [game, level1], [game, level2],
                    [game, level3], [game, level4]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random, sys
    levels = [l for l in locals().keys() if 'level' in l]
    if len(sys.argv)==2:
        index = int(sys.argv[1])
    else:
        index = random.choice(range(len(levels)))
    VGDLParser.playGame(game, locals()[levels[index]])
