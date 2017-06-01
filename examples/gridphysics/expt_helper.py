
# level0 = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                              w
# w              a               w
# w  x                           w
# w                         a    w
# w                              w
# w  A                           w
# www                            w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level1 = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w        a         a           w
# w              a               w
# w  x                           w
# w   b                     a    w
# w                   a          w
# w  A  b  a                     w
# www                 x          w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level2 = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w        a         a           w
# w              a               w
# w  r                           w
# w          b              a    w
# w                   a          w
# w  A     a     b               w
# www                 r          w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level2 = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                b a b         w
# w        a       bbbbb         w
# w              a               w
# w  x                           w
# w                         a    w
# w                   a          w
# w  A   w       b             bbw
# www    w            x        baw
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

level2= """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w        a     c   a         c w
w                              w
w  z                           w
w          b                   w
w  a                a          w
w  A           b               w
www c            c      z   c  w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""



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
        rand wall > stepBack
        box1 avatar > bounceForward
        box1 box2 > stepBack
        avatar chaser > nothing
        box2 avatar > killSprite
        box1 chaser > killSprite
        box1 rand > killSprite
        box1 box3 > nothing
        avatar box3 > nothing
        box3 chaser > killSprite
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
level_game_pairs = [[game, level2]]


# level_game_pairs = [[game, level0], [game, level1], [game, level2],
#                     [game, level3]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random, sys, time
    import numpy as np
    import csv
    from IPython import embed



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
