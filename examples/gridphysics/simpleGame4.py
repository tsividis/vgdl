'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''


# level = """
# wwwwwwwww
# w  1    w
# w    2  w
# wAp  wgww
# w    w ww
# wwwwwwwww
# """

# level2 = """
# wwwwwwwww
# wA 1    w
# w    2  w
# w p  w ww
# w   gw ww
# wwwwwwwww
# """

level = """
wwwwwwwww
w  1   pw
w       w
wg2  wAww
w    w ww
wwwwwwwww
"""

# level = """
# wwwwwwwww
# w       w
# w   A   w
# w      ww
# w g  w ww
# wwwwwwwww
# """



game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > Passive color=GOLD
        poison > Resource limit=3 color=BROWN
        box1  > ResourcePack color=ORANGE
        box2 > ResourcePack color=BLUE
        wall > Immovable color=BLACK      
        score > Resource color=PINK limit=10         
    LevelMapping
        p > poison
        1 > box1
        2 > box2
        w > wall   
        g > goal 
        h > hole
    InteractionSet
        avatar wall > stepBack  
        poison avatar > killSprite
        avatar poison > killSprite
        goal avatar > killSprite
        box1 avatar  > bounceForward
        box2 avatar > killSprite
        goal box1 > bounceForward
        goal wall > undoAll
        goal poison > undoAll
        box1 wall    > undoAll    
        box1 poison > undoAll
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    