'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''


level = """
wwwww
wA  w
w   w
w  gw
wwwww
"""

game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > Passive color=GOLD
        wall > Immovable color=BLACK      
    LevelMapping
        w > wall   
        g > goal 
    InteractionSet
        avatar wall > stepBack  
        goal avatar > killSprite
        goal wall > undoAll
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    