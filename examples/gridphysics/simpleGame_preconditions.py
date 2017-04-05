'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

# level = """
# wwwwwwwwwwwww
# w pmAmp  w  w
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
w     cpppppw
w A     p  gw
wwwwwwwwwwwww
"""


        
game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4              
        goal > Passive color=GOLD
        cloud > Passive 
            blue > color=BLUE
        medicine > Resource limit=10 color=WHITE
        poison > Resource limit=3 color=BROWN
        wall > Immovable color=BLACK      
    LevelMapping
        0 > hole
        c > blue 
        m > medicine
        p > poison
        w > wall   
        g > goal 
    InteractionSet
        avatar wall > stepBack  
        avatar medicine > changeResource resource=medicine value=2
        medicine avatar > killSprite
        avatar poison > changeResource resource=medicine value=-1
        avatar poison > killIfHasLess resource=medicine limit=-1
        poison avatar > killSprite
        cloud avatar  > bounceForward
        goal avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False   
        SpriteCounter stype=goal limit=0 win=True       
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    