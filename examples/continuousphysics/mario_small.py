'''
VGDL example: Mario, jump around! 

@author: Tom Schaul
'''
level = """
wwwwwwwwwwww
w          w
w          w
w          w
w        G1w
w       wwww
w          w
w   www    w
w A        w
wwww   wwwww
wwwwwwwwwwww
"""


# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                          w
# w                        G1w
# w             ===       wwww
# w                     1    w
# w                w  2 ww   w
# w                wwwwwww   w
# w                          w
# w                          w
# w          2        2      w
# w        www      wwwwww   w
# w A      1   ===           w
# wwww   wwww        2       w
# wwwwwwwwww      wwww       w
# """


game = """
BasicGame
    SpriteSet 
        avatar > MarioAvatar strength=20 physicstype=GravityPhysics color=WHITE
        goomba     > Walker orientation=LEFT color=BROWN physicstype=GravityPhysics
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
        goomba wall > wallStop friction=0.1
        
    LevelMapping
        w > wall
        G > goal
        1 > goomba
"""



if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)