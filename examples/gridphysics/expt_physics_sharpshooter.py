level1 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
a                     2        a
a                              a
a                              a
a                              a
a                 A            a
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
a          2                   a
a                        3     a
a                              a
a                              a
a                              a
a                 A            a
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""


level3 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
a1                             a
a          2                   a
a                        3     a
a                              a
a        5                     a
a                              a
a                              a
a                 A            a
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level4 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
a1                             a
a          2                   a
a                        3     a
a                              a
a        5                     a
a                 4            a
a                              a
a                              a
a                 A            a
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

game= """
BasicGame frame_rate=42
    SpriteSet
        fakewall   > Immovable    color=DARKGRAY
        avatar  > FlakAvatar stype=sam color=DARKBLUE
        missile > Missile color=BLACK
            sam  > orientation=UP    color=BLUE speed=0.3 singleton=True
            bomb > orientation=DOWN  color=RED  speed=0.5
        alien   >  Missile orientation=RIGHT
            alien1   > speed=.3 orientation=RIGHT color=ORANGE
            alien2   >  speed=.5 orientation=RIGHT color=LIGHTBLUE
            alien3   >  speed=.4 orientation=RIGHT color=PINK
            alien4   >  speed=.2 orientation=RIGHT color=GREEN
            alien5   >  speed=.1 orientation=RIGHT color=YELLOW
        portal  > SpawnPoint   stype=alien  cooldown=10   total=3 color=BLACK
        wall > Immovable color=DARKGRAY
    LevelMapping
        0 > portal
        1 > alien1
        2 > alien2
        3 > alien3
        4 > alien4
        5 > alien5
        a > wall

    InteractionSet
        alien wall > reverseDirection
        avatar wall > stepBack
        avatar  EOS  > stepBack
        alien1   EOS > reverseDirection
        alien2   EOS > reverseDirection
        alien3   EOS > reverseDirection
        alien4   EOS > reverseDirection
        alien5   EOS > reverseDirection
        missile EOS  > killSprite
        avatar bomb  > killSprite
        alien1  sam   > killSprite
        alien2  sam   > killSprite
        alien3  sam   > killSprite
        alien4  sam   > killSprite
        alien5  sam   > killSprite
        sam wall > killSprite

    TerminationSet
        SpriteCounter      stype=avatar               limit=0 win=False
        MultiSpriteCounter stype1=portal stype2=alien limit=0 win=True
"""

level_game_pairs = [[game, level1], [game, level2], [game, level3],
                    [game, level4]]

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
                row = ['human', 'no_score', 'expt_physics_sharpshooter', levels_won, data[1], data[3], data[0]]

                filename = "expt_physics_sharpshooter_human_data.csv"
                f = open(filename, 'a+') ##append, but also read.
                g = open(filename, 'r')
                writer = csv.writer(f)
                if len(g.readlines())==0:
                    writer.writerow(('subject', 'condition', 'gameName', 'levels_won', 'steps', 'score', 'time'))
                writer.writerow(row)
                f.close()
                g.close()
