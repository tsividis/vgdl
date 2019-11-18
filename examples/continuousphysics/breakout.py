game = """
BasicGame
    SpriteSet
        goal > Immovable color=RED
        avatar > BreakoutAvatar speed=2.0
        ball > Missile orientation=DOWN speed=15 color=ORANGE physicstype=NoFrictionPhysics width=0.25 height=0.5
            
    TerminationSet
        SpriteCounter stype=goal limit=0 win=True   
        SpriteCounter stype=ball limit=0 win=False
           
    InteractionSet
        goal ball   > killSprite
        ball goal > wallBounce
        ball avatar > bounceDirection
        ball wall   > wallBounce
        avatar wall > stepBack
        avatar avatar > stepBack
        ball EOS > killSprite
        
    LevelMapping
        g > goal
        o > ball
        r > avatar
"""

#SpriteCounter stype=lost limit=3 win=False


level = """
wwwwwwwwww
wggggggggw
wggggggggw
w        w
w        w
w   o    w
w        w
w        w
w  r     w
"""


'''
level = """
wwwwwww
wgggggw
wgggggw
w     w
w     w
w  o  w
w     w
w  r  w
"""
'''



'''
level = """
wwwww
wgggw
wgggw
w o w
w   w
w   w
w   w
w r w
"""
'''


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
