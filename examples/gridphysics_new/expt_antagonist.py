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
w             A                w
wm                             w
w             b                w
www                           aw
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level1 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wm                             w
w                              w
w                              w
w                              w
w                              w
w    b                         w
w  A                          aw
www                            w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w     m   Aba       a        a w
w                              w
w                            a w
w                              w
w                              w
w                              w
w                            a w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

# level2 = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                              w
# w                              w
# w  b                           w
# w                              w
# w                              w
# wr A                          aw
# www                            w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """


# level3 = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w     a       b    a      a    w
# w                              w
# w  b            a     a        w
# w              A m             w
# w     a     a                  w
# w     b                       aw
# www                  a         w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

level3 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w  a                           w
w     a            a      a    w
w       a                      w
w               a              w
w         m    A   b           w
w     a     a            ffffffw
w     a   a              f     w
www                  a   f     w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""


# level4 = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w  a                           w
# w     a       b    a      a    w
# w       a              fffff   w
# w  b        m   a     af   f   w
# w              A       f   f   w
# w     a     a          fffff   w
# w     a   a       b      a    aw
# www                  a         w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

game = """
BasicGame frame_rate=30
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE
        chaser > VGDLSprite
            randomChaser > RandomNPC color=WHITE
            mediumChaser > Chaser color=LIGHTGREEN cooldown=1 stype=box2
            goodChaser > AStarChaser color=RED stype=box2
        forcefield > Passive color=LIGHTBLUE
        wall > Immovable color=DARKGRAY
        box > Passive
            box1 > color=PINK
            box2 > color=YELLOW
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
        box1 box2 > killSprite
        avatar chaser > nothing
        box1 avatar > killSprite
        box2 chaser > killSprite
        chaser box1 > stepBack
        chaser wall > stepBack
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False
        SpriteCounter stype=box2  limit=0 win=False
        SpriteCounter stype=box1 limit=0 win=True
"""

level_game_pairs = [[game, level0], [game, level1], [game, level2],
                    [game, level3]]

# level_game_pairs = [[game, level0], [game, level2]]

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
            wins = 0
            while wins<2:
                VGDLParser.playGame(*level)
                time.sleep(1)
                data = np.load("temp_data.npy")
                win = data[2]
                if win:
                    wins+=1
                levels_won = index*2 + wins
                # Save in format [subect, condition, gamename, levels won, steps taken, score, time elapsed]
                row = ['human', 'no_score', 'expt_antagonist', levels_won, data[1], data[3], data[0]]

                filename = "human_data.csv"
                f = open(filename, 'a+') ##append, but also read.
                g = open(filename, 'r')
                writer = csv.writer(f)
                if len(g.readlines())==0:
                    writer.writerow(('subject', 'condition', 'gameName', 'levels_won', 'steps', 'score', 'time'))
                writer.writerow(row)
                f.close()
                g.close()
