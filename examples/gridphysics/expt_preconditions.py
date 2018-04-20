
level0 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwww                wwwwwwww
wwwwwwww     A          wwwwwwww
wwwwwwww                wwwwwwww
wwwwwwww                wwwwwwww
wwwwwwww                wwwwwwww
wwwwwwww  b             wwwwwwww
wwwwwwww                wwwwwwww
wwwwwwww             g  wwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""
level1 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwww b p   w    m   wwwwwwww
wwwwwwww   p   w A  wwwwwwwwwwww
wwwwwwww g p         p  wwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwww   p   w    p  bwwwwwwww
wwwwwwww m     w A  wwwwwwwwwwww
wwwwwwwwpppp      p     wwwwwwww
wwwwwwww     p p       wwwwwwwww
wwwwwwwww            pppwwwwwwww
wwwwwwwwpppp       pppppwwwwwwww
wwwwwwwwmpp        pp  gwwwwwwww
wwwwwwwwmp      p  pp   wwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level3 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwww   p   w        wwwwwwww
wwwwwwww       w A  wwwwwwwwwwww
wwwwwwwwpppp      p  pmmwwwwwwww
wwwwwwww     p p     p wwwwwwwww
wwwwwwwwwpp         ppppwwwwwwww
wwwwwwwwpppp      ppppppwwwwwwww
wwwwwwww m pp     ppppppwwwwwwww
wwwwwwwwbmmppm  p ppp g wwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

game = """
BasicGame frame_rate=30
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE #cooldown=4
        goal > Passive color=GOLD
        box > Passive color=ORANGE
        medicine > Resource limit=4 color=WHITE
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
        avatar medicine > changeResource resource=medicine value=1
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

level_game_pairs = [[game, level0], [game, level1], [game, level2], [game, level3]]

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
