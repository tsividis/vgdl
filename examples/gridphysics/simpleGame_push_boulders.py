'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

level = """
wwwwwwwwwwwwwwwwww
w    w  p        w
w  1 w    p      w
wA  q     2  w  ww
wwwwww1  g   w  ww
ww         q     w
w   p    q     1 w
w    2           w
w        2       w
wwwwwwwwwwwwwwwwww
"""


game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > ResourcePack color=GOLD
        poison >
            poison1 > ResourcePack color=BROWN
            poison2 > ResourcePack color=PINK
        box >
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
        poison avatar > killSprite
        avatar poison > killSprite
        
        goal avatar > killSprite

        
        box box > bounceForward
        box wall > stepBack

        box avatar > bounceForward
        

        goal box > stepBack
        goal box > bounceForward

        goal poison > stepBack
        goal wall > stepBack

        poison box1 > killSprite
        box2 poison > killSprite
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    