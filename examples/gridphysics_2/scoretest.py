'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''



level = """
wwwwwwwwwwwwwwwwww
wp     Aw       2w
w    2  w        w
w               ww
w  1  1         ww
ww   www   q     w
w  1 1         p w
w  1   1    g    w
w    1   2    1  w
wwwwwwwwwwwwwwwwww
"""


game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > ResourcePack color=GREEN
        poison1 > ResourcePack color=BROWN
        poison2 > ResourcePack color=PINK
        box1 > ResourcePack color=GOLD
        box2 > ResourcePack color=LIGHTBLUE
        wall > Immovable color=BLACK      
        score > Resource color=PINK limit=10  
    LevelMapping
        p > poison1
        q > poison2
        1 > box1
        2 > box2
        w > wall   
        g > goal 
    InteractionSet
        avatar wall > stepBack  
        poison1 avatar > killSprite
        poison2 avatar > killSprite
        avatar poison1 > killSprite
        avatar poison2 > killSprite
        goal avatar > killSprite
        avatar box1 > changeScore value=1
        box1 avatar > killSprite
        box2 avatar  > killSprite
        goal box1 > bounceForward
        goal box2 > bounceForward
        goal wall > undoAll
        goal poison1 > undoAll
        goal poison2 > undoAll
        box1 box1 > undoAll
        box1 wall    > undoAll    
        box2 wall    > undoAll    
        poison1 box1 > killSprite
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