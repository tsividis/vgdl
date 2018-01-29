game = """
BasicGame
    SpriteSet
        goal1 > Immovable color=BLUE
        goal2 > Immovable color=GREEN
        goal3 > Immovable color=RED
        avatar > HorizontalAvatar speed=0.5 color=WHITE
        ball > Missile orientation=DOWN speed=15 color=ORANGE physicstype=NoFrictionPhysics
        lost > Immovable color=BLACK
        obstacle > Immovable color=BLACK

    TerminationSet # from the perspective of player 1 (on the left)
        MultiSpriteCounter stype1=goal1 stype2=goal2 stype3=goal3 limit=0 win=True
        SpriteCounter stype=ball limit=0 win=False

    InteractionSet
        goal1 ball   > killSprite
        ball goal1 > wallBounce
        goal1 ball   > changeScore value=1000
        goal2 ball   > killSprite
        ball goal2 > wallBounce
        goal2 ball   > changeScore value=2000
        goal3 ball   > killSprite
        ball goal3 > wallBounce
        goal3 ball   > changeScore value=3000
        ball avatar > bounceDirection

        ball wall   > wallBounce
        avatar wall > stepBack
        lost ball > killSprite
        ball EOS > killSprite

        ball obstacle   > wallBounce

    LevelMapping
        1 > goal1
        2 > goal2
        3 > goal3
        l > lost
        o > ball
        r > avatar
        v > obstacle
"""

# level = """
# wwwwwwwwwwwwwwwwwwww
# wggggggggggggggggggw
# wggggggggggggggggggw
# wggggggggggggggggggw
# w                  w
# w        o         w
# w                  w
# w                  w
# w                  w
# w        r         w
# """

level1 = """
wwwwwwwwwwwwwwwwwwwwwwwww
w11111111111111111111111w
w22222222222222222222222w
w33333333333333333333333w
w                       w
w           o           w
w                       w
w                       w
w                       w
w                       w
w                       w
w                       w
w           r           w
"""

# Middle wall breakout
level2 = """
wwwwwwwwwwwwwwwwwwwwwwwww
w11111111111111111111111w
w22222222222222222222222w
w33333333333333333333333w
w       vvvvvvvvv       w
w           o           w
w                       w
w                       w
w                       w
w                       w
w                       w
w                       w
w           r           w
"""


# Offset paddle breakout
level3 = """
wwwwwwwwwwwwwwwwwwwwwwwww
w11111111111111111111111w
w22222222222222222222222w
w33333333333333333333333w
w                       w
w           o           w
w                       w
w                       w
w                       w
w                       w
w           r           w
w                       w
w                       w
"""
level_game_pairs = [[game, level1], [game, level2], [game, level3]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
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
                    wins +=1
                levels_won = index*2 + wins
                # Save in format [subect, condition, gamename, levels won, steps taken, score, time elapsed]
                row = ['human', 'no_score', 'breakout', levels_won, data[1], data[3], data[0]]

                filename = "human_data.csv"
                f = open(filename, 'a+') ##append, but also read.
                g = open(filename, 'r')
                writer = csv.writer(f)
                if len(g.readlines())==0:
                    writer.writerow(('subject', 'condition', 'gameName', 'levels_won', 'steps', 'score', 'time'))
                writer.writerow(row)
                f.close()
                g.close()
