'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''


level1 = """
wwwwwwwwwwwww
w m         w
w           w
w          pw
w A        gw
wwwwwwwwwwwww
"""


        
game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4              
        goal > Passive color=GOLD
        cloud > Passive color=BLUE
        medicine > Resource limit=1 color=WHITE
        poison > Resource limit=3 color=BROWN
        wall > Immovable color=BLACK      
    LevelMapping
        0 > hole
        c > cloud 
        m > medicine
        p > poison
        w > wall   
        g > goal 
    InteractionSet
        avatar wall > stepBack  
        hole avatar > killSprite
        treasure avatar > changeResource resource=score value=5
        treasure avatar > killSprite
        trap avatar > changeResource resource=score value=-5
        trap avatar > killSprite
        box trap > killSprite
        cloud avatar > killSprite
        avatar medicine > changeResource resource=medicine value=1
        medicine avatar > killSprite
        avatar poison > changeResource resource=medicine value=-1
        poison avatar > killSprite
        avatar poison > killIfHasLess resource=medicine limit=-1
        box avatar  > bounceForward
        box wall    > undoAll        
        box hole    > killSprite
        box treasure > undoAll
        box poison > undoAll
        box medicine > undoAll
        goal avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False   
        SpriteCounter stype=goal limit=0 win=True       
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    