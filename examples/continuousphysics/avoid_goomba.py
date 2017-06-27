level = """
wwwwwwwwwwwww
w           w
w           w
w           w
w           w
w           w
w           w
wA        1Gw
wwwwwwwwwwwww
"""

game = """
BasicGame
    SpriteSet 
        avatar > MarioAvatar strength=20 physicstype=GravityPhysics color=WHITE
        goomba > Missile orientation=LEFT color=PURPLE speed=0.3
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
            
    TerminationSet
        SpriteCounter stype=goal      win=True     
        SpriteCounter stype=avatar    win=False     
           
    InteractionSet
        
        avatar goomba > killSprite
        avatar EOS  > killSprite
        goomba EOS > killSprite
        goal avatar > killSprite
        avatar wall > wallStop friction=0.1
        goomba wall > killSprite
        
    LevelMapping
        w > wall
        G > goal
        1 > goomba
"""



if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)