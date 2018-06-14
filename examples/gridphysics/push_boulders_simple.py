
level = """
wwwwww
wA ggw
wswwww
"""

level1 = """
wwwwwwwww
wA swwwww
w   sgg w
w       w
wwwwwwwww
"""

level2 = """
wwwwwwwwww
wA  sgg ww
w   sss  w
w        w
wwwwwwwwww
"""

game = """
BasicGame
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE
        goal > ResourcePack color=PINK
        box > ResourcePack color=GREEN
        wall > Immovable color=DARKGRAY
        spike > Immovable color=ORANGE
    LevelMapping
        w > wall
        g > goal
        s > spike
    InteractionSet
        avatar spike > killSprite
        avatar wall > stepBack
        goal avatar > killSprite
        goal wall > stepBack
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False
"""

level_game_pairs = [[game, level], [game, level1], [game, level2]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random, sys, time, csv
    import numpy as np
    levels = [l for l in locals().keys() if 'level' in l]

    if len(sys.argv)==1:
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
                win = data[1]
                if win:
                    wins+=1
                levels_won = index*1 + wins
                # Save in format [subect, condition, gamename, levels won, steps taken, score, time elapsed]
                row = ['human', 'no_score', 'push_boulders_simple', levels_won, data[1], data[3], data[0]]

                filename = "human_data.csv"
                f = open(filename, 'a+') ##append, but also read.
                g = open(filename, 'r')
                writer = csv.writer(f)
                if len(g.readlines())==0:
                    writer.writerow(('subject', 'condition', 'gameName', 'levels_won', 'steps', 'score', 'time'))
                writer.writerow(row)
                f.close()
                g.close()
