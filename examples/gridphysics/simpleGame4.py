'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

# box_level = """
# wwww
# wp w
# wAgw
# wwww
# """

box_level = """
wwwwwwwww
w  1    w
w    2  w
wAp  wgww
w    w ww
wwwwwwwww
"""

# box_level = """
# wwwwwwwww
# w       w
# w       w
# wAp  wgww
# w    w ww
# wwwwwwwww
# """

# box_level = """
# wwwwwwwww
# w     m w
# w       w
# wAp  wgww
# w    w ww
# wwwwwwwww
# """

push_game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > ResourcePack color=GOLD
        poison > ResourcePack limit=3 color=BROWN
        box  > ResourcePack 
            box1 > color=ORANGE
            box2 > color=RED
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
        poison avatar > stepBack
        avatar poison > stepBack
        goal avatar > killSprite
        box avatar  > killSprite
        goal box > bounceForward
        goal wall > undoAll
        goal poison > undoAll
        box wall    > undoAll    
        box treasure > undoAll
        box poison > undoAll
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(push_game, box_level)    