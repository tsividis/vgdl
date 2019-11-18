game = """
BasicGame
    SpriteSet
        goal > Immovable color=RED
        avatar > BreakoutAvatar speed=0.35#HorizontalAvatar speed=0.35
        ball > Missile orientation=DOWN speed=15 color=ORANGE physicstype=NoFrictionPhysics
        lost > Immovable color=BLACK
            
    TerminationSet
        SpriteCounter stype=goal limit=0 win=True   
        SpriteCounter stype=ball limit=0 win=False
           
    InteractionSet
        goal ball   > killSprite
        ball goal > wallBounce
        ball avatar > bounceDirection
        ball wall   > wallBounce
        avatar wall > stepBack
        lost ball > killSprite
        ball EOS > killSprite
        
    LevelMapping
        g > goal
        l > lost
        o > ball
        r > avatar
"""

level = """
wwwwwwwwwwwwwwwwwwww
wggggggggggggggggggw
wggggggggggggggggggw
wggggggggggggggggggw
w                  w
w        o         w
w                  w
w                  w
w                  w
w        r         w
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)