
level0 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w              a               w
w  x                           w
w          b              a    w
w                              w
w  A           b               w
www                            w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level1 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w        a         a           w
w              a               w
w  x                           w
w          b              a    w
w                   a          w
w  A     a     b               w
www                 x          w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w        a         a           w
w              a               w
w  x                           w
w          b              a    w
w                   a          w
w  A     a     b               w
www                 x          w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level3 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w        a         a           w
w              a               w
w  r                           w
w          b              a    w
w                   a          w
w  A     a     b               w
www                 r          w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level4 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                b   b         w
w        a       b a b         w
w              a bbbbb         w
w  x                           w
w          b              a    w
w                   a          w
w  A     a     b               w
www                 x          w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

# level = """
# wwwwwwww
# w b    w
# wab   xw
# w bbbA w
# wwwwwwww
# """

# level = """
# wwwwwwwwwwwwww
# w    bbb     w
# w a  b    a  w
# w    b       w
# w    bbbA   xw
# wwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwww
# w    bbb     w
# w g  bbb     w
# w    bbb     w
# w    bbb     w
# w    bbb   x w
# w    bbb   A w
# wwwwwwwwwwwwww
# """



# level = """
# wwwwwwwwwwwwwwwwwwwwwwww
# w                 b    w
# w              b  b  a w
# w   a             bbbbbw
# w       w   a      x   w
# w   A                  w
# wwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwww
# w                 b    w
# w              b  b A  w
# w   a             wwwwww
# w       w   a      x   w
# w                      w
# w                 bbbb w
# w              www  wwww
# wbbbbbbb     b         w
# w      b               w
# w  a   b        x      w
# w      b               w
# w      b   a           w
# wwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                 b    b           w
# w              b  b A  b  a   a    w
# w   a             wwwwww           w
# w           a                  x   w
# w                           b      w
# w                 bbbb      b      w
# w     x                     b      w
# w                      a    ww  wwww
# wbbbbbbb     b                     w
# w      b                       a   w
# w  a   b              a            w
# w      b                           w
# w      b   a              b        w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

game = """
BasicGame frame_rate=30
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE cooldown=0
        box > Passive
            box1 > color=RED
            box2 > color=ORANGE
        mover > VGDLSprite
            rand > RandomNPC cooldown=6 color=LIGHTBLUE
            chaser > Chaser color=BLUE stype=box1 cooldown=12 #for humans
        wall > Immovable color=BLACK
        missile > Missile
            missile1 > color=YELLOW orientation=RIGHT
            missile2 > color=PINK orientation=RIGHT
        goal > Immovable color=GREEN
    LevelMapping
        w > wall
        a > box1
        b > box2
        x > chaser
        r > rand
        1 > missile1
        2 > missile2
        g > goal
    InteractionSet
        avatar wall > stepBack
        mover wall > stepBack
        box wall > stepBack
        box1 avatar > bounceForward
        box1 box2 > stepBack
        avatar chaser > nothing
        #box2 avatar > changeScore value=-2
        box2 avatar > killSprite
        box1 chaser > killSprite
        box1 rand > killSprite
        avatar rand > nothing
        chaser wall > stepBack
        goal chaser > killSprite
        chaser box2 > stepBack
        missile EOS > wrapAround
        missile avatar > killSprite
        missile missile > reverseDirection
        mover mover > stepBack
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False
        SpriteCounter stype=box1 limit=0 win=True
"""

level_game_pairs = [[game, level0], [game, level1], [game, level2],
                    [game, level3]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random, sys
    levels = [l for l in locals().keys() if 'level' in l]
    if len(sys.argv)==2:
        index = int(sys.argv[1])
    else:
        index = random.choice(range(len(levels)))
    VGDLParser.playGame(game, locals()[levels[index]])
