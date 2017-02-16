'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

level = """
wwwwwwwwwwwwwwwwww
w  1    p        w
w    2    p      w
wA  q     2  w  ww
w    w1      w  ww
ww         q     w
w   p    q     1 w
w    2       g   w
w        2       w
wwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwww
w  1    w       2w
w    2  w        w
w         2     ww
w     1         ww
ww         q A   w
w        q     p w
w     wwwww      w
w  g          q  w
wwwwwwwwwwwwwwwwww
"""

level3 = """
wwwwwwwwwwwwwwwwww
wp      w    A  2w
w  g 2  w        w
w         2     ww
w     1         ww
ww     w   q     w
w   q  w       p w
w    2 w         w
w        2    1  w
wwwwwwwwwwwwwwwwww
"""

level4 = """
wwwwwwwwwwwwwwwwww
wp     Aw    g  2w
w    2  w        w
w          1    ww
w  1  1  1      ww
ww   www   q     w
w              p w
w                w
w    1   2    1  w
wwwwwwwwwwwwwwwwww
"""

level5 = """
wwwwwwwwwwwwwwwwww
wp     Aw       2w
w    1 11        w
w  2    1   www ww
w  2  2  1      ww
ww   www   q w   w
w            w g w
w            w   w
w    1   2    1  w
wwwwwwwwwwwwwwwwww
"""

level6 = """
wwwwwwwwwwwwwwwwww
wp      w       2w
w       1    11  w
w   g      1    ww
w  1  12 1      ww
ww         q     w
w              A w
w  ww     q      w
w    1   2    1  w
wwwwwwwwwwwwwwwwww
"""


game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > ResourcePack color=GOLD
        poison1 > ResourcePack color=BROWN
        poison2 > ResourcePack color=PINK
        box1 > ResourcePack color=GREEN
        box2 > ResourcePack color=LIGHTBLUE
        wall > Immovable color=BLACK      
        score > Resource color=PINK limit=10  
        missile > Missile color=RED speed=.2      
    LevelMapping
        p > poison1
        q > poison2
        1 > box1
        2 > box2
        w > wall   
        g > goal 
        m > missile
    InteractionSet
        avatar wall > stepBack  
        missile wall > reverseDirection
        poison1 avatar > killSprite
        poison2 avatar > killSprite
        avatar poison1 > killSprite
        avatar poison2 > killSprite
        goal avatar > killSprite
        box1 avatar > bounceForward
        box2 avatar  > killSprite
        goal box1 > bounceForward
        goal box2 > bounceForward
        goal wall > undoAll
        goal poison1 > undoAll
        goal poison2 > undoAll
        box1 wall    > undoAll    
        box2 wall    > undoAll    
        box1 poison1 > undoAll
        box2 poison1 > undoAll
        box1 poison2 > undoAll
        box2 poison2 > undoAll
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    