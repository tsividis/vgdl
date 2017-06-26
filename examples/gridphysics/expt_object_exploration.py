
level0 = """
wwwwwwwwwwwwwwwwwwwwwww
w   www   www   www   w
w                     w
w   www   www   www   w
ww wwwww wwwww wwwww ww
ww wwwww wwwww wwwww ww
ww wwwww wwwww wwwww ww
w   www   www   www   w
w a     A             w
w   www   www   www   w
ww wwwww wwwww wwwww ww
ww wwwww wwwww wwwww ww
ww wwwww wwwww wwwww ww
w   www   www   www   w
w       b             p
w   www   www   www   w
wwwwwwwwwwwwwwwwwwwwwww
"""

level1 = """
wwwwwwwwwwwwwwwwwwwwwww
w   www   www   www   w
w                     w
w   www   www   www   w
ww wwwww wwwww wwwww ww
ww wwwwwwwwwww wwwww ww
ww wwwww wwwww wwwww ww
w   www   www   www   w
w a  b  A             w
w   www   www   www   w
ww wwwww wwwww wwwww ww
ww wwwww wwwww wwwww ww
ww wwwww wwwww wwwww ww
w   www   www   www   w
w                     p
w   www   www   www   w
wwwwwwwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwwwwwwww
w   www   www   www   w
w          w  d     d w
w   www   www   www   w
ww wwwww wwwww wwwww ww
ww wwwww wwwww wwwwwwww
ww wwwww wwwww wwwww ww
w   www   www   www   w
w       A     c     c w
w   www   www   www   w
ww wwwww wwwww wwwww ww
ww wwwww wwwww wwwwwwww
ww wwwww wwwww wwwww ww
w   www   www   www   w
w          w  n       p
w   www   www   www   w
wwwwwwwwwwwwwwwwwwwwwww
"""

level3 = """
wwwwwwwwwwwwwwwwwwwwwww
w   www   www   www   w
w          w  f     f w
w   www   www   www   w
ww wwwww wwwww wwwww ww
ww wwwww wwwww wwwwwwww
ww wwwww wwwww wwwww ww
w   www   www   www   w
w       A     e     e w
w   www   www   www   w
ww wwwww wwwww wwwww ww
ww wwwww wwwww wwwwwwww
ww wwwww wwwww wwwww ww
w   www   www   www   w
w          w  m       p
w   www   www   www   w
wwwwwwwwwwwwwwwwwwwwwww
"""

game0 = """
BasicGame frame_rate=30
    SpriteSet
        apple > Immovable color=ORANGE
        trap > Immovable color=YELLOW
        goodkey1 > Immovable color=BLUE
        goodkey2 > Immovable color=BROWN
        badkey1 > Immovable color=GREEN
        goodkey3 > Immovable color=PINK
        nothing1 > Immovable color=LIGHTBLUE
        nothing2 > Immovable color=LIGHTGREEN
        avatar > MovingAvatar color=WHITE
        poison > Immovable color=BLACK
        wall > Immovable color=BLACK
    LevelMapping
        w > wall
        a > apple
        b > trap
        c > goodkey1
        d > goodkey2
        e > badkey1
        f > goodkey3
        n > nothing1
        m > nothing2
        p > poison
    InteractionSet
        avatar wall > stepBack
        apple avatar > killSprite
        avatar trap > killSprite
        avatar poison > killSprite

        goodkey1 avatar > bounceForward
        goodkey2 avatar > bounceForward
        goodkey3 avatar > bounceForward
        badkey1 avatar > bounceForward

        goodkey1 goodkey1 > killSprite
        goodkey2 goodkey2 > killSprite
        goodkey2 goodkey1 > stepBack
        goodkey1 goodkey2 > stepBack
        
        badkey1 badkey1 > stepBack
        goodkey3 goodkey3 > killSprite
        badkey1 goodkey3 > stepBack
        goodkey3 badkey1 > stepBack

        avatar nothing1 > stepBack
        avatar nothing2 > stepBack

    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False
        SpriteCounter stype=apple limit=0 win=True
"""

game1 = """
BasicGame frame_rate=30
    SpriteSet
        apple > Immovable color=ORANGE
        trap > Immovable color=YELLOW
        goodkey1 > Immovable color=BLUE
        goodkey2 > Immovable color=BROWN
        badkey1 > Immovable color=GREEN
        goodkey3 > Immovable color=PINK
        nothing1 > Immovable color=LIGHTBLUE
        nothing2 > Immovable color=LIGHTGREEN
        avatar > MovingAvatar color=WHITE
        poison > Immovable color=BLACK
        wall > Immovable color=BLACK
    LevelMapping
        w > wall
        a > apple
        b > trap
        c > goodkey1
        d > goodkey2
        e > badkey1
        f > goodkey3
        n > nothing1
        m > nothing2
        p > poison
    InteractionSet
        avatar wall > stepBack
        apple avatar > killSprite
        avatar trap > killSprite
        avatar poison > killSprite

        goodkey1 avatar > bounceForward
        goodkey2 avatar > bounceForward
        goodkey3 avatar > bounceForward
        badkey1 avatar > bounceForward

        goodkey1 goodkey1 > killSprite
        goodkey2 goodkey2 > killSprite
        goodkey2 goodkey1 > stepBack
        goodkey1 goodkey2 > stepBack
        
        badkey1 badkey1 > stepBack
        goodkey3 goodkey3 > killSprite
        badkey1 goodkey3 > stepBack
        goodkey3 badkey1 > stepBack

        avatar nothing1 > stepBack
        goodkey1 nothing1 > stepBack
        goodkey2 nothing1 > stepBack

    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False
        SpriteCounter stype=goodkey2 limit=0 win=True
"""

game2 = """
BasicGame frame_rate=30
    SpriteSet
        apple > Immovable color=ORANGE
        trap > Immovable color=YELLOW
        goodkey1 > Immovable color=BLUE
        goodkey2 > Immovable color=BROWN
        badkey1 > Immovable color=GREEN
        goodkey3 > Immovable color=PINK
        nothing1 > Immovable color=LIGHTBLUE
        nothing2 > Immovable color=LIGHTGREEN
        avatar > MovingAvatar color=WHITE
        poison > Immovable color=BLACK
        wall > Immovable color=BLACK
    LevelMapping
        w > wall
        a > apple
        b > trap
        c > goodkey1
        d > goodkey2
        e > badkey1
        f > goodkey3
        n > nothing1
        m > nothing2
        p > poison
    InteractionSet
        avatar wall > stepBack
        apple avatar > killSprite
        avatar trap > killSprite
        avatar poison > killSprite

        goodkey1 avatar > bounceForward
        goodkey2 avatar > bounceForward
        goodkey3 avatar > bounceForward
        badkey1 avatar > bounceForward

        goodkey1 goodkey1 > killSprite
        goodkey2 goodkey2 > killSprite
        goodkey2 goodkey1 > stepBack
        goodkey1 goodkey2 > stepBack
        
        badkey1 badkey1 > stepBack
        goodkey3 goodkey3 > killSprite
        badkey1 goodkey3 > stepBack
        goodkey3 badkey1 > stepBack

        avatar nothing2 > stepBack
        goodkey3 nothing2 > stepBack
        badkey1 nothing2 > stepBack


    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False
        SpriteCounter stype=goodkey3 limit=0 win=True
"""

level_game_pairs = [[game0,level0],[game0,level1],[game1,level2],[game2, level3]]#
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
