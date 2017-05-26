
level0 = """
wwwwwwwwwwwwwwwwwwwww
w  1    p           w
w    2    p         w
wA  q     2  w     ww
w    w1      w w    w
ww         q        w
w   p    q     1    w
w    2       g      w
w        2          w
wwwwwwwwwwwwwwwwwwwww
"""

level1 = """
wwwwwwwwwwwwwwwwwwwww
wp      w   A      2w
w  g 2  w           w
w         2   ww   ww
w     1             w
ww     w   q  w     w
w   q  w      w   p w
w    2 w      w     w
w        2    1     w
wwwwwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwwwwww
wp        Aw       2w
w       1 11        w
w  2       1   www ww
w  2  2     1      ww
ww   www      q w   w
w               w g w
w           2   w   w
w    1   2       1  w
wwwwwwwwwwwwwwwwwwwww
"""

level3 = """
wwwwwwwwwwwwwwwwwwwww
wp         w       2w
w          1    11  w
w   g         1    ww
w  1  12    1      ww
ww            q     w
w                 A w
w  ww     q         w
w  h 1   2       1  w
wwwwwwwwwwwwwwwwwwwww
"""

level4 = """
wwwwwwwwwwwwwwwwwwwww
w    1       w  w   w
w  1 w       w   wwww
wA   w       2     ww
wwwwwwwwwwwwwwwwww ww
ww        wq        w
w   p    qw    w    w
w    2          w   w
w g      2w         w
wwwwwwwwwwwwwwwwwwwww
"""

level5 = """
wwwwwwwwwwwwwwwwwwwww
wA1   w   p       g w
ww  1 w     p       w
w     p     2  w   ww
wwwwwww1       w   ww
ww           q      w
w   p    q        1 w
w    2              w
w        2          w
wwwwwwwwwwwwwwwwwwwww
"""

level6 = """
wwwwwwwwwwwwwwwwwwwww
wA1p  w   p         w
ww  1 w     p       w
w     p     2  w   ww
wwwwwww1       w   ww
ww           q      w
w   p    q        1 w
w    2        g     w
w        2          w
wwwwwwwwwwwwwwwwwwwww
"""


level7 = """
wwwwwwwwwwwwwwwwwwwwww
w    1        w  w   w
w  1 w        w   1  w
wA   w        2   11 w
wwwwwwwwwwwwwwwwwww ww
ww        w ww   w  ww
wwwww   w   1   ww   w
w   w2   ww  w   ww ww
w  g     2www       ww
wwwwwwwwwwwwwwwwwwwwww
"""


level8 = """
wwwwwwwwwwwwwwwwwwwwww
w    1        w  w w w
w  1 w        w1  1 ww
w g  w        1   11 w
wwwwwwwwwwwwwwwwwww ww
w   w     w w    w Aww
wwww q    w 1 w  w   w
w    1ww q    w  ww ww
w  w  w w w   w     ww
wwwwwwwwwwwwwwwwwwwwww
"""

# level11 = """
# wwwwwwwwwwwwwwwwwwwwww
# wp      w    Aw     2w
# w       w 1  11      w
# wwwwwwwww     1  ww ww
# w  2   2       1    ww
# ww    www      q w   w
# w      g         w   w
# w            2   w   w
# w     1  2        1  w
# wwwwwwwwwwwwwwwwwwwwww
# """
# level10 = """
# wwwwwwwwwwwwwwwwwwwwww
# wp      w    A      2w
# w  g 2  w            w
# w         2    ww wwww
# w     1           w  w
# ww     w   q  w   w  w
# w   q  w      w   wwww
# w    2 w      w      w
# w        2    1      w
# wwwwwwwwwwwwwwwwwwwwww
# """





game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > ResourcePack
            goal1 > color=GOLD
            goal2 > color=RED
        poison > ResourcePack
            poison1 > color=ORANGE
            poison2 >  color=PINK
        box1 > ResourcePack color=GREEN
        box2 > ResourcePack color=LIGHTBLUE
        wall > Immovable color=DARKGRAY
        score > Resource color=PINK limit=10  
    LevelMapping
        p > poison1
        q > poison2
        1 > box1
        2 > box2
        w > wall   
        g > goal1
        h > goal2 
    InteractionSet
        avatar wall > stepBack  
        avatar poison > killSprite
        goal avatar > killSprite
        box1 avatar > bounceForward
        box2 avatar  > killSprite
        poison wall > stepBack
        goal box1 > stepBack
        goal box2 > stepBack
        goal wall > stepBack
        goal poison1 > stepBack
        goal poison2 > stepBack
        box1 wall    > stepBack   
        box2 wall    > stepBack   
        box1 box1 > stepBack
        poison1 box1 > killSprite
        poison2 box1 > bounceForward
        poison1 box2 > stepBack
        poison2 box2 >stepBack
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random, sys
    levels = [l for l in locals().keys() if 'level' in l]
    
    if len(sys.argv)==2:
        index = int(sys.argv[1])
    else:
        index = random.choice(range(len(levels)))
    # VGDLParser.playGame(*level_game)
    # index = random.choice(range(len(levels)))
    VGDLParser.playGame(game, locals()[levels[index]])
