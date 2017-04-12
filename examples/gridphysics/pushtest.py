'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''


level = """
wwwwwww
wA 12 g
wwwwwww
"""

game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > Passive color=GOLD
        wall > Immovable color=BLACK
        box1  > ResourcePack color=GREEN
        box2 > ResourcePack color=BLUE 
    LevelMapping
        w > wall   
        g > goal 
        1 > box1
        2 > box2
    InteractionSet
        avatar wall > stepBack  
        goal avatar > killSprite
        goal wall > undoAll
        box1 avatar  > bounceForward
        box2 box1 > bounceForward
        goal box2 > killSprite
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    