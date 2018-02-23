
level0 = """
wwwwwwwwwwwwwwwwww
w                w
w     A          w
w                w
w                w
w                w
w  b             w
w                w
w             g  w
wwwwwwwwwwwwwwwwww
"""
level1 = """
wwwwwwwwwwwwwwwwww
w g p   w pA m   w
w   p   w    wwwww
w g p         m  w
wwwwwwwwwwwwwwwwww
"""

# level1 = """
# wwwwwwwwwwwwwwwwww
# w b p   w    m   w
# w   p   w A  wwwww
# wpppp      p     w
# w     p p       ww
# ww   www         w
# wpppp          p w
# w   pp           w
# w g p    p    p  w
# wwwwwwwwwwwwwwwwww
# """

level2 = """
wwwwwwwwwwwwwwwwww
w   w   w    p  bw
w m     w A  wwwww
wwwww            w
w               ww
ww            wwww
wwwww       wwwwww
wmww        ww  gw
wmp         pp   w
wwwwwwwwwwwwwwwwww
"""

# level2 = """
# wwwwwwwwwwwwwwwwww
# w b p   w    m   w
# w e p   w A  wwwww
# wpppp      p     w
# w     p p       ww
# ww   www         w
# wpppp        ffffw
# w   pp       f g w
# wmm p    p   f   w
# wwwwwwwwwwwwwwwwww
# """

level3 = """
wwwwwwwwwwwwwwwwww
w   w   w        w
w       w A  wwwww
wwwww         pmmw
w             w ww
wwww         wwpww
wwwww      wwwwpww
w m pp     wwwwpww
wbmmwwm    www g w
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
        invisiblemedicine > Resource limit=4 color=PURPLE
        poison > Resource limit=3 color=PINK
        suit > Resource limit=1 color=GREEN
        wall > Immovable color=BLACK
    LevelMapping
        0 > hole
        b > box
        m > medicine
        p > poison
        s > suit
        w > wall
        g > goal
    InteractionSet
        avatar wall > stepBack
        medicine avatar > killSprite
        avatar poison > killIfHasLess resource=medicine limit=-1
        avatar poison > changeResource resource=medicine value=-1
        # avatar medicine > changeResource resource=invisiblemedicine value=1
        avatar medicine > changeResource resource=medicine value=1
        # avatar medicine > changeScore value=5
        # medicine avatar > collectResource
        box avatar > killSprite
        poison avatar > killSprite
        box wall    > undoAll
        box poison > undoAll
        box medicine > undoAll
        goal avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False
        SpriteCounter stype=goal limit=0 win=True
"""

level_game_pairs = [[game, level1], [game, level2], [game, level3]] #[game, level0], 

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
                row = ['human', 'no_score', 'expt_preconditions', levels_won, data[1], data[3], data[0]]

                filename = "human_data.csv"
                f = open(filename, 'a+') ##append, but also read.
                g = open(filename, 'r')
                writer = csv.writer(f)
                if len(g.readlines())==0:
                    writer.writerow(('subject', 'condition', 'gameName', 'levels_won', 'steps', 'score', 'time'))
                writer.writerow(row)
                f.close()
                g.close()
