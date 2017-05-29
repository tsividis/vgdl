

level0 = """
wwwwwwwwwwwwwwwwww
w b p   w    m   w
w   p   w A  wwwww
wpppp      p     w
w     p p       ww
ww   www         w
wpppp          p w
w   pp           w
w g p    p    p  w
wwwwwwwwwwwwwwwwww
"""

level1 = """
wwwwwwwwwwwwwwwwww
w   p   w    p  bw
w m     w A  wwwww
wpppp      p     w
w     p p       ww
ww            pppw
wpppp       pppppw
wmmmpp      pp  gw
wmmmp    p  pp   w
wwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwww
w b p   w    m   w
w e p   w A  wwwww
wpppp      p     w
w     p p       ww
ww   www         w
wpppp        ffffw
w   pp       f g w
wmm p    p   f   w
wwwwwwwwwwwwwwwwww
"""

level3 = """
wwwwwwwwwwwwwwwwww
w   p   w        w
w       w A  wwwww
wpppp      p  pmmw
w     p p     p ww
wwpp         ppppw
wpppp      ppppppw
wm mpp     ppppppw
wmbmppm  p ppp g w
wwwwwwwwwwwwwwwwww
"""


# level = """
# wwwwwwwwwwwww
# w pmAmp  w  w
# w  pmp      w
# w  pppp  pp w
# w       p  gw
# wwwwwwwwwwwww
# """

# level2 = """
# wwwwwwwwwwwww
# w           w
# w  pmp      w
# w  pppppppp w
# w A     p  gw
# wwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwww
# wm           w
# w            w
# w       pppppw
# w     A p   gw
# wwwwwwwwwwwwww
# """
# level = """
# wwwww
# wmA g
# wwwww
# """

# level = """
# wwwwwwwwwwwwwwwwww
# w b c   w    m   w
# w   c   w    wwwww
# wcccc      p     w
# w     c p       ww
# ww   www A       w
# wpppp          c w
# w   pc           w
# w g p    c    c  w
# wwwwwwwwwwwwwwwwww
# """


# level = """
# wwwwwwwww
# w bp    w
# w  p  m w
# wppp A  w
# w gp    w
# wwwwwwwww
# """



game = """
BasicGame frame_rate=30
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE #cooldown=4
        goal > Passive color=GOLD
        box > Passive color=ORANGE
        medicine > Resource limit=4 color=WHITE
        water > Resource limit=4 color=LIGHTBLUE
        poison > Resource limit=3 color=RED
        fire > Resource limit=3 color=PURPLE
        suit > Resource limit=1 color=GREEN
        wall > Immovable color=BLACK
    LevelMapping
        0 > hole
        b > box
        m > medicine
        p > poison
        e > water
        f > fire
        s > suit
        w > wall
        g > goal
    InteractionSet
        avatar wall > stepBack
        medicine avatar > killSprite
        avatar fire > killIfHasLess resource=water limit=0
        avatar fire > changeResource resource=water value=-1
        avatar poison > killIfHasLess resource=medicine limit=0
        avatar poison > changeResource resource=medicine value=-1
        avatar medicine > changeResource resource=medicine value=1
        avatar water > changeResource resource=water value=1
        box avatar > killSprite
        poison avatar > killSprite
        fire avatar > killSprite
        water avatar > killSprite
        box wall    > undoAll
        box poison > undoAll
        box medicine > undoAll
        goal avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False
        SpriteCounter stype=goal limit=0 win=True
"""

level_game_pairs = [[game, level0], [game, level1], [game, level2],
                    [game, level3]]

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
                row = ['human', 'no_score', 'expt_preconditions', levels_won, data[1], data[3], data[0]]

                filename = "expt_preconditions_human_data.csv"
                f = open(filename, 'a+') ##append, but also read.
                g = open(filename, 'r')
                writer = csv.writer(f)
                if len(g.readlines())==0:
                    writer.writerow(('subject', 'condition', 'gameName', 'levels_won', 'steps', 'score', 'time'))
                writer.writerow(row)
                f.close()
                g.close()
