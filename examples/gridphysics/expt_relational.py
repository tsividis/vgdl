
# level0 = """
# wwwwwwwwwwwwwwwwwwwwww
# wA                   w
# w                    w
# w          x   f     w
# w                    w
# w      f             w
# w                 x  w
# w                    w
# w                    p
# wwwwwwwwwwwwwwwwwwwwww
# """

level0 = """
wwwwwwwwwwwwwwwwwwwwww
wA                   w
w    a             x w
w              f     w
w                    w
w      f             w
w                 x  w
w          a         w
w                    p
wwwwwwwwwwwwwwwwwwwwww
"""

level1 = """
wwwwwwwwwwwwwwwwwwwwww
wA                   w
w    a    x          w
w                    w
w                    w
w              z     w
w   x    z           w
w          a         w
w                    p
wwwwwwwwwwwwwwwwwwwwww
"""

# level1 = """
# wwwwwwwwwwwwwwwwwwwwww
# w                    w
# w              A  x  w
# w                    w
# w                    w
# w              z     w
# w   x    z           w
# w                    w
# w                    p
# wwwwwwwwwwwwwwwwwwwwww
# """

level2 = """
wwwwwwwwwwwwwwwwwwwwww
w                    w
w    a    x          w
w                    w
w                    w
w              y     w
w   x    y           w
w          a         w
w          A         p
wwwwwwwwwwwwwwwwwwwwww
"""

level3 = """
wwwwwwwwwwwwwwwwwwwwww
w                    w
w         x          w
w            y       w
w                    w
w          y   z     w
w   x    z           w
w                    w
w          A         p
wwwwwwwwwwwwwwwwwwwwww
"""


game0 = """
BasicGame frame_rate=30
    SpriteSet
        probe > Immovable color=BLUE
        converter > Immovable
            converter1 > color=RED
            converter2 > color=PURPLE
        box > Immovable
            box1 > color=ORANGE
        fire > Immovable color=YELLOW
        avatar > MovingAvatar color=WHITE
        poison > Immovable color=BLACK
        wall > Immovable color=BLACK
    LevelMapping
        w > wall
        a > box1
        b > box2
        f > fire
        x > probe
        z > converter1
        y > converter2
        p > poison
    InteractionSet
        avatar wall > stepBack
        avatar fire > stepBack
        box avatar > bounceForward
        box probe > stepBack
        probe box > stepBack
        box box > stepBack
        box wall > stepBack
        probe wall > stepBack
        # avatar converter > stepBack
        converter wall > stepBack
        probe converter > stepBack
        converter probe > stepBack
        converter1 box > bounceForward
        box converter2 > transformTo stype=fire
        converter2 fire > killSprite
        box fire > stepBack
        probe probe > stepBack
        probe avatar > bounceForward
        converter1 avatar > transformTo stype=fire
        probe fire > killSprite
        fire probe > killSprite
        avatar poison > killSprite
    TerminationSet  
        SpriteCounter stype=avatar  limit=0 win=False
        SpriteCounter stype=probe limit=0 win=True
"""

game3 = """
BasicGame frame_rate=30
    SpriteSet
        probe > Immovable color=BLUE
        converter > Immovable
            converter1 > color=RED
            converter2 > color=PURPLE
            converter3 > color=PINK
        box > Immovable
            box1 > color=ORANGE
            box2 > color=GREEN
        fire > Immovable color=YELLOW
        avatar > MovingAvatar color=WHITE
        poison > Immovable color=BLACK
        wall > Immovable color=BLACK
    LevelMapping
        w > wall
        a > box1
        b > box2
        f > fire
        x > probe
        z > converter1
        y > converter2
        z > converter3
        p > poison
    InteractionSet
        avatar wall > stepBack
        avatar fire > stepBack
        box avatar > bounceForward
        box probe > stepBack
        probe box > stepBack
        box box > stepBack
        box wall > stepBack
        probe wall > stepBack
        converter wall > stepBack
        probe converter > stepBack
        converter1 box1 > bounceForward
        box1 converter2 > transformTo stype=fire
        converter3 avatar > transformTo stype=box1
        converter2 fire > killSprite
        box fire > stepBack
        probe probe > stepBack
        probe avatar > bounceForward
        converter1 avatar > transformTo stype=fire
        probe fire > killSprite
        fire probe > killSprite
        # avatar converter > stepBack ## this was uncommented in the original experiment, but stepBack and transformTo are currently incompatible. fix bug.
        avatar poison > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False
        SpriteCounter stype=probe limit=0 win=True
"""


level_game_pairs = [[game0, level0], [game0, level1], [game0, level2],[game3, level3]]

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
                row = ['human', 'no_score', 'expt_relational', levels_won, data[1], data[3], data[0]]

                filename = "human_data.csv"
                f = open(filename, 'a+') ##append, but also read.
                g = open(filename, 'r')
                writer = csv.writer(f)
                if len(g.readlines())==0:
                    writer.writerow(('subject', 'condition', 'gameName', 'levels_won', 'steps', 'score', 'time'))
                writer.writerow(row)
                f.close()
                g.close()
