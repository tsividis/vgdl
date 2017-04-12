'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

# level1 = """
# wwwwwwwwwwwww
# w  mAmp  w  w
# w  pmp      w
# w  pppp  pp w
# w       p  gw
# wwwwwwwwwwwww
# """

# level2 = """
# wwwwwwwwwwwww
# w           w
# w  pmp      w
# w  pppppppp w
# w A     p  gw
# wwwwwwwwwwwww
# """

level = """
wwwwwwwwwwwww
w m         w
w           w
w      pppppw
w A     p  gw
wwwwwwwwwwwww
"""


        
game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4              
        goal > Passive color=GOLD
        cloud > Passive color=BLUE
        medicine > Resource limit=2 color=WHITE
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
        avatar medicine > changeResource resource=medicine value=2
        medicine avatar > killSprite
        avatar poison > changeResource resource=medicine value=-1
        poison avatar > killSprite
        avatar poison > killIfHasLess resource=medicine limit=-1
        box avatar  > bounceForward
        box wall    > undoAll        
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