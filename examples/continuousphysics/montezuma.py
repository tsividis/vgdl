level = """
wwwwwwwwwwwwwwwwww
w                w
w                w
w                w
wG       A      Gw
wwww  wwwwww  wwww
w                w
w                w
w                w
wG        1      w
wwwwwwwwwwwwwwwwww
"""

game = """
BasicGame
    SpriteSet 
        avatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE
        goomba > Missile orientation=LEFT color=BROWN speed=0.2
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
        avatar wall > wallStop
        goomba wall > wallBounce
        
    LevelMapping
        w > wall
        G > goal
        1 > goomba
"""

level_game_pairs = [[game, level]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)