'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''



level = """
wwwwwwwww
w   1   w
w Ap    w
w 2  wgww
w    w ww
wwwwwwwww
"""

level2 = """
wwwwwwwww
w  1    w
w    2  w
wAp  wgww
w    w ww
wwwwwwwww
"""
level3 = """
wwwwwwwww
w  2   1w
w       w
wA   wgww
w  p w ww
wwwwwwwww
"""


game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE
        goal > ResourcePack color=GOLD
        poison > ResourcePack limit=3 color=BROWN
        box  > ResourcePack 
            box1 > color=GREEN
            box2 > color=LIGHTBLUE
        wall > Immovable color=BLACK      
        score > Resource color=PINK limit=10  
    LevelMapping
        p > poison
        1 > box1
        2 > box2
        w > wall   
        g > goal 
    InteractionSet
        avatar wall > stepBack  
        missile wall > reverseDirection
        poison avatar > killSprite
        avatar poison > killSprite
        goal avatar > killSprite
        box1 avatar > bounceForward
        box2 avatar  > killSprite
        goal box > bounceForward
        goal wall > undoAll
        goal poison > undoAll
        box wall    > undoAll    
        box poison > undoAll
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level1)    