
level0 = """
wwwwwwwwwwwwwwwwww
w  1    a        w
w                w
wA  b        w  ww
w    w       w  ww
ww         b     w
w   a          1 w
w        2   b   w
w                g
wwwwwwwwwwwwwwwwww
"""

level1 = """
wwwwwwwwwwwwwwwwww
w  1    a        w
w    wwwww       w
w            w  ww
w    w     3 w1 ww
w1   w     b     w
w   a w          w
w     w  2   b   w
w   A w         gw
wwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwww
w  1    a       gw
w                w
w   b        w  ww
w    w     3 w1 ww
ww         b     w
w   a 1          w
w        2   b   w
w               Aw
wwwwwwwwwwwwwwwwww
"""

level3 = """
wwwwwwwwwwwwwwwwww
w       b        w
w   1            w
w 3              w
w        g    1  w
w          2     w
w           2    w
w    1          bw
w aA             w
wwwwwwwwwwwwwwwwww
"""

level4 = """
wwwwwwwwwwwwwwwwww
w       2        w
w                w
w   ww3wwwwwww   w
w           w    w
wwwwww w   2 w   w
wg        www    w
wwwwwwwwww1     bw
w aA             w
wwwwwwwwwwwwwwwwww
"""



# level3 = """
# wwwwwwwwwwwwwwwwww
# w   2w        b gw
# w b     a 1      w
# w 3   wwwwwwwwwwww
# w            a   w
# wwwwwwwwwwwwwww  w
# w       a        w
# w  wwwwwwwwwwwwwww
# w               Aw
# wwwwwwwwwwwwwwwwww
# """

# level4 = """
# wwwwwwwwwwwwwwwwww
# w       b       gw
# w   1            w
# w 3              w
# w             1  w
# w          2     w
# w           2    w
# w    1          bw
# w aA             w
# wwwwwwwwwwwwwwwwww
# """



game = """
BasicGame frame_rate=30
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE
        box > Passive
            box1 > color=RED
            box2 > color=LIGHTGREEN
        mover > VGDLSprite
            rand > RandomNPC cooldown=10
                rand1 > color=LIGHTORANGE
                rand2 > color=BLUE
        chaser > AStarChaser color=BROWN stype=avatar
        wall > ResourcePack color=BLACK
        missile > Missile
            missile1 > color=YELLOW orientation=RIGHT speed=.2
            missile2 > color=PINK orientation=RIGHT speed=.4
            missile3 > color=LIGHTBLUE orientation=UP speed=.2
        goal > Passive color=GREEN
    LevelMapping
        w > wall
        a > box1
        b > box2
        x > chaser
        y > rand1
        z > rand2
        1 > missile1
        2 > missile2
        3 > missile3
        g > goal
    InteractionSet
        avatar wall > stepBack
        mover wall > stepBack
        box avatar > killSprite
        avatar box2 > killSprite
        avatar rand > killSprite
        missile box > turn
        avatar missile > killSprite
        rand wall > stepBack
        chaser wall > stepBack
        avatar chaser > killSprite
        missile EOS > wrapAround offset=0
        missile wall > turn
        missile missile > reverseDirection
        mover mover > stepBack
        mover missile > stepBack
        mover box > stepBack
        goal avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False
        SpriteCounter stype=goal limit=0 win=True
"""

"""
show agent killing a moving item.
same prediction should be highest for other moving items of same speed, then for non-moving items.
also vice-versa.
"""

level_game_pairs = [[game, level1], [game, level2], [game, level3],
                    [game, level4]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random, sys, time
    import numpy as np
    import csv

    if len(sys.argv)==2:
        index = int(sys.argv[1])
    else:
        index = random.choice(range(len(level_game_pairs)))
    VGDLParser.playGame(*level_game_pairs[index])

    data = np.load("temp_data.npy")

    levels_won = index if not data[2] else index+int(data[2])
    # Save in format [subect, condition, gamename, levels won, steps taken, score, time elapsed]
    row = ['human', 'no_score', 'expt_relational', levels_won, data[1], data[3], data[0]]

    filename = "expt_relational_human_data.csv"
    f = open(filename, 'a+') ##append, but also read.
    writer = csv.writer(f)
    if len(f.readlines())==0:
        writer.writerow(('subject', 'condition', 'gameName', 'levels_won', 'steps', 'score', 'time'))
    writer.writerow(row)
    f.close()
