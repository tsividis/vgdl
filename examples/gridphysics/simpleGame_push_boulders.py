

## Planner can solve this. Current' agent can't, becuase if it just explores its own interactions with single objects,
## it never learns that pushing the box into the poison kills the poison.
level = """
wwwwwwwwwwwwwwwwww
wA   w  p        w
w 1  w    p      w
w    q  g 2  w  ww
wwwwww1      w  ww
ww         q     w
w   p    q     1 w
w    2           w
w        2       w
wwwwwwwwwwwwwwwwww
"""

# level = """
# wwwwwwwwwwwwwwwwwwww
# w    1pw  p        w
# ww     w    p      w
# w   A1 p    2  w  ww
# wwwwwww1  g    w  ww
# ww           q     w
# w   p    q       1 w
# w    2             w
# w        2         w
# wwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwww
# w    1    w  w   w
# w  1 w    w   1 ww
# wA   w    2    1ww
# wwwwwwwwwwwwwww ww
# ww        wq     w
# w   p    qw      w
# w    2           w
# w g      2w      w
# wwwwwwwwwwwwwwwwww
# """

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
    VGDLParser.playGame(game, level)    