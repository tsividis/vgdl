

## Planner can solve this. Current' agent can't, becuase if it just explores its own interactions with single objects,
## it never learns that pushing the box into the poison kills the poison.
# level = """
# wwwwwwwwwwwwwwwwww
# wA   w  p        w
# w  1 w    p      w
# w    q  g 2  w  ww
# wwwwww1      w  ww
# ww         q     w
# w   p    q     1 w
# w    2           w
# w        2       w
# wwwwwwwwwwwwwwwwww
# """


level = """
wwwwwwwwwwwwwwwwwwwwww
w  1                 w
w    2               w
wA        2  w      ww
w    w1      w  w    w
ww                   w
w              1     w
w    2       g       w
w        2           w
wwwwwwwwwwwwwwwwwwwwww
"""


level1 = """
wwwwwwwwwwwwwwwwwwwwww
w  1    p            w
w    2    p          w
wA        2  w      ww
w    w1      w  w    w
ww                   w
w   p          1     w
w    2       g       w
w        2           w
wwwwwwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwwwwwww
w  1    p         h  w
w    2    p          w
wA  p     2  w      ww
w    w1      w  w    w
ww         q         w
w   p    q     1     w
w    2               w
w        2           w
wwwwwwwwwwwwwwwwwwwwww
"""

level3 = """
wwwwwwwwwwwwwwwwwwwwww
w  1    p         h  w
w    2    p          w
wA  p     2  w      ww
w    w1      w  w    w
ww         q         w
w   p    q     1     w
w    2               w
w        2           w
wwwwwwwwwwwwwwwwwwwwww
"""

# level4  = """
# wwwwwwwwwwwwwwwwwwwwww
# wp      w    A      2w
# w    2  w            w
# w         2    ww   ww
# w     1             hw
# ww     w   q  w      w
# w   q  w      w    p w
# w    2 w      w      w
# w g      2    1      w
# wwwwwwwwwwwwwwwwwwwwww
# """

# level5 = """
# wwwwwwwwwwwwwwwwwwwwww
# wp         Aw       2w
# w        1 11        w
# w  2        1   www ww
# w  2  2      1      ww
# ww   www       q w   w
# w     h          w g w
# w           2    w   w
# w    1   2        1  w
# wwwwwwwwwwwwwwwwwwwwww
# """

# level6 = """
# wwwwwwwwwwwwwwwwwwwwww
# w  1    p         h  w
# w    2    p     m    w
# w   q     2  w      ww
# w    w1      w  w    w
# ww         q    m    w
# w   p    q     1     w
# w    2               w
# wA       2           w
# wwwwwwwwwwwwwwwwwwwwww
# """

# level7 = """
# wwwwwwwwwwwwwwwwwwwwww
# w  1    p         h  w
# w    2    p     m    w
# w   q     2  w      ww
# w    w1      w  w    w
# ww         q    m    w
# w   p    q     1     w
# w    2               w
# wA       2           w
# wwwwwwwwwwwwwwwwwwwwww
# """


# level8 = """
# wwwwwwwwwwwwwwwwwwwwww
# wp          w       2w
# w           1    11  w
# w   g          1    ww
# w  1  12     1      ww
# ww             q     w
# w                  A w
# w  ww     q          w
# w  h 1   2        1  w
# wwwwwwwwwwwwwwwwwwwwww
# """

# level9 = """
# wwwwwwwwwwwwwwwwwwwwww
# w    1        w  w h w
# w  1 w        w   wwww
# wA   w        2     ww
# wwwwwwwwwwwwwwwwwww ww
# ww        wq         w
# w   p    qw     w    w
# w    2           w   w
# w g      2w          w
# wwwwwwwwwwwwwwwwwwwwww
# """

# level10 = """
# wwwwwwwwwwwwwwwwwwwww
# wA1p  w   p       h w
# ww  1 w     p       w
# w     p     2  w   ww
# wwwwwww1       w   ww
# ww           q      w
# w   p    q        1 w
# w    2        g     w
# w        2          w
# wwwwwwwwwwwwwwwwwwwww
# """

# level11 = """
# wwwwwwwwwwwwwwwwwwwww
# wA1p  w   p       h w
# ww  1 w     p       w
# w     p     2  w   ww
# wwwwwww1       w   ww
# ww           q      w
# w   p    q        1 w
# w    2        g     w
# w        2          w
# wwwwwwwwwwwwwwwwwwwww
# """

# level12 = """
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

# level13 = """
# wwwwwwwwwwwwwwwwwwwwww
# wp     w   Aw       2w
# w      w 1 11        w
# wwwwwwww    1   www ww
# w  2  2      1      ww
# ww   www       q w   w
# w     h          w   w
# w           2    w   w
# w    1   2        1  w
# wwwwwwwwwwwwwwwwwwwwww
# """

# level14  = """
# wwwwwwwwwwwwwwwwwwwwww
# w    1        w  w h w
# w  1 w        w   1 ww
# wA   w        2    1ww
# wwwwwwwwwwwwwwwwwww ww
# ww        wq         w
# wwwww    qw     w    w
# w   w2           w   w
# w g      2w          w
# wwwwwwwwwwwwwwwwwwwwww
# """

# level3 = """
# wwwwwwwwwwwwwwwwwwwwww
# w       b           gw
# w   1                w
# w 3                  w
# w                 1  w
# w          2         w
# w           2        w
# w    1              bw
# w aA                 w
# wwwwwwwwwwwwwwwwwwwwww
# """

# level = """    OMIT
# wwwwwwwwwwwwwwwwwwwwww
# wp     Aw        g  2w
# w    2  w            w
# w          1        ww
# w  1  1  1          ww
# ww   www   q         w
# w                  p w
# w                    w
# w    1   2    1      w
# wwwwwwwwwwwwwwwwwwwwww
# """

# level2  = """ OMIT
# wwwwwwwwwwwwwwwwwwwwww
# w  1    w           2w
# w    2  w     p      w
# w         2         ww
# w h   1             ww
# ww              A    w
# w        q        p  w
# w     wwwww   q      w
# w  g              q  w
# wwwwwwwwwwwwwwwwwwwwww
# """



game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > ResourcePack
            goal1 > color=GOLD
            goal2 > color=RED
        poison1 > ResourcePack color=ORANGE
        poison2 > ResourcePack color=PURPLE
        box1 > ResourcePack color=GREEN
        box2 > ResourcePack color=LIGHTBLUE
        wall > Immovable   
        missile > Missile color=BROWN speed=.4      
    LevelMapping
        p > poison1
        q > poison2
        1 > box1
        2 > box2
        w > wall   
        g > goal1
        h > goal2 
        m > missile
    InteractionSet
        avatar wall > stepBack  
        missile wall > reverseDirection
        avatar poison1 > killSprite
        avatar poison2 > killSprite
        avatar missile > killSprite
        goal avatar > killSprite
        box1 avatar > bounceForward
        box2 avatar  > killSprite
        goal box1 > undoAll
        goal box2 > undoAll
        goal wall > undoAll
        goal poison1 > undoAll
        goal poison2 > undoAll
        box1 wall    > undoAll    
        box2 wall    > undoAll    
        box1 box1 > undoAll
        poison1 box1 > killSprite
        poison2 box1 > killSprite
        poison1 box2 > undoAll
        poison2 box2 >undoAll
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random
    levels = [l for l in locals().keys() if 'level' in l]
    index = random.choice(range(len(levels)))
    VGDLParser.playGame(game, locals()[levels[index]]) 