'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''


level = """
wwwwwwwwwwwwwwwwww
wA 1    p        w
w    2    p      w
w p       w  w gww
w    w 1     w  ww
wwwwwwwwwwwwwwwwww
"""

# level = """
# wwwwwwwwwwwwwwwwww
# w  1    p        w
# w    2    p      w
# w p       2  wg ww
# w    w 1   A w  ww
# wwwwwwwwwwwwwwwwww
# """


game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > ResourcePack color=GOLD
        poison > ResourcePack limit=3 color=BROWN
        box1 > ResourcePack color=GREEN
        box2 > ResourcePack color=LIGHTBLUE
        wall > Immovable color=BLACK      
        score > Resource color=PINK limit=10  
        missile > Missile color=RED speed=.2      
    LevelMapping
        p > poison
        1 > box1
        2 > box2
        w > wall   
        g > goal 
        m > missile
    InteractionSet
        avatar wall > stepBack  
        missile wall > reverseDirection
        poison avatar > killSprite
        avatar poison > killSprite
        goal avatar > killSprite
        box1 avatar > bounceForward
        box2 avatar  > killSprite
        goal box1 > bounceForward
        goal box2 > bounceForward
        goal wall > undoAll
        goal poison > undoAll
        box1 wall    > undoAll    
        box2 wall    > undoAll    
        box1 poison > undoAll
        box2 poison > undoAll
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    