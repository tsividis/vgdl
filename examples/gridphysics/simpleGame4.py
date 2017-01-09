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
w       w
w       w
wAp  wgww
w    w ww
wwwwwwwww
"""

# box_level = """
# wwwwwwwww
# w     A w
# w       w
# w    wgww
# w    w ww
# wwwwwwwww
# """

push_game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > Passive color=GOLD
        poison > Resource limit=3 color=BROWN
        box  > ResourcePack color=ORANGE
        wall > Immovable color=BLACK      
        score > Resource color=PINK limit=10         
    LevelMapping
        p > poison
        1 > box
        w > wall   
        g > goal 
        h > hole
    InteractionSet
        avatar wall > stepBack  
        poison avatar > killSprite
        avatar poison > killSprite
        goal avatar > killSprite
        box avatar  > bounceForward
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