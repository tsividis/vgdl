
# level0 = """
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w               f    o d w
# w   a      A    d        w
# w      a         o  d    w
# w            b           w
# w     e       d  b  c    w
# w   o    c     ec        w
# w         f f  o      e  w
# w   b e   b    f d c     w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# """


level0 = """
wwwwwwwwwwwww
w  Ao    c  w
w a  d    f w
w   b e   b w
wwwwwwwwwwwww
"""


# level0 = """
# wwwwwwwww
# w Ab b bw
# wwwwwwwww
# """

game0 = """
BasicGame frame_rate=30
    SpriteSet
        apple > Missile color=GREEN speed=.5
        # apple > Immovable color=GREEN
        orange > Immovable color=ORANGE
        blueberry > Immovable color=BLUE
        dough > Immovable color=YELLOW
        cranberry > Immovable color=LIGHTBLUE
        eel > Immovable color=PINK
        fruit > Immovable color=RED
        avatar > MovingAvatar color=DARKBLUE
        wall > Immovable color=BLACK
        health > Resource color=PURPLE
    LevelMapping
        w > wall
        a > apple
        b > blueberry
        o > orange
        c > cranberry
        d > dough
        e > eel
        f > fruit
    InteractionSet
        avatar wall > stepBack
        blueberry avatar > killSprite
        avatar cranberry > stepBack
        dough avatar > killSprite
        eel avatar > killSprite
        fruit avatar > killSprite
        apple avatar > killSprite
        orange avatar > bounceForward
        # orange avatar > killSprite
        # avatar orange > changeResource resource=health value=1
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False
        SpriteCounter stype=blueberry limit=0 win=True

"""

level_game_pairs = [[game0, level0]]


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
            while wins<1:
                VGDLParser.playGame(*level)
                time.sleep(1)
                data = np.load("temp_data.npy")
                win = data[2]
                if win:
                    wins+=1
                levels_won = index*2 + wins
                # Save in format [subect, condition, gamename, levels won, steps taken, score, time elapsed]
                row = ['human', 'no_score', 'expt_exploration_exploitation', levels_won, data[1], data[3], data[0]]

                filename = "human_data.csv"
                f = open(filename, 'a+') ##append, but also read.
                g = open(filename, 'r')
                writer = csv.writer(f)
                if len(g.readlines())==0:
                    writer.writerow(('subject', 'condition', 'gameName', 'levels_won', 'steps', 'score', 'time'))
                writer.writerow(row)
                f.close()
                g.close()
