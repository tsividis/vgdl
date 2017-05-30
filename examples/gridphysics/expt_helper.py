
level0 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w              a               w
w  x                           w
w                         a    w
w                              w
w  A                           w
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

# level2 = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w        a         a           w
# w              a               w
# w  x                           w
# w          b              a    w
# w                   a          w
# w  A     a     b               w
# www                 x          w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

level2 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                b   b         w
w        a       b a b         w
w              a bbbbb         w
w  x                           w
w                         a    w
w      bbbbb        a          w
w  A   b a b   b               w
www    b   b        x          w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level3 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w        a     c   a         c w
w                              w
w  z                           w
w          b                   w
w  a                a          w
w  A           b               w
www                     z      w
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
            box1 > color=WHITE
            box2 > color=GREEN
            box3 > color=YELLOW
        mover > VGDLSprite
            rand > RandomNPC cooldown=0 color=PURPLE #12 for humans, 2 for Planner
            chaser > Chaser
                chaser1 > stype=box1 color=ORANGE  cooldown=0 #12 #for humans
                chaser2 > stype=box3 color=LIGHTBLUE cooldown=0 #for humans
        wall > Immovable color=BLACK
        missile > Missile
            missile1 > color=YELLOW orientation=RIGHT
            missile2 > color=PINK orientation=RIGHT
    LevelMapping
        w > wall
        a > box1
        b > box2
        c > box3
        x > chaser1
        z > chaser2
        r > rand
        z > chaser2
        1 > missile1
        2 > missile2
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
        box1 box3 > nothing
        avatar box3 > nothing
        box3 chaser > nothing
        avatar rand > nothing
        chaser wall > stepBack
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
    import random, sys, time
    import numpy as np
    import csv
    from IPython import embed


    # level_game_pairs = [[game, level]]

    levels = [l for l in locals().keys() if 'level' in l and len(l)<8]
    if len(sys.argv)==2:
        index = int(sys.argv[1])
        VGDLParser.playGame(*level_game_pairs[index])
    else:
        # index = random.choice(range(len(level_game_pairs)))
        for index, level in enumerate(level_game_pairs):
            win = False
            while not win:
                VGDLParser.playGame(*level)
                time.sleep(1)
                data = np.load("temp_data.npy")
                win = data[2]
                levels_won = index if not data[2] else index+int(data[2])
                # Save in format [subect, condition, gamename, levels won, steps taken, score, time elapsed]
                row = ['human', 'no_score', 'expt_helper', levels_won, data[1], data[3], data[0]]

                filename = "expt_helper_human_data.csv"
                f = open(filename, 'a+') ##append, but also read.
                g = open(filename, 'r')
                writer = csv.writer(f)
                if len(g.readlines())==0:
                    writer.writerow(('subject', 'condition', 'gameName', 'levels_won', 'steps', 'score', 'time'))
                writer.writerow(row)
                f.close()
                g.close()
