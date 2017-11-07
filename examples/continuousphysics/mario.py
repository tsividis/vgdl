'''
VGDL example: Mario, jump around! 

@author: Tom Schaul
'''

game = """
BasicGame
    SpriteSet 
        elevator > Missile orientation=UP speed=0.1 color=BLUE 
        avatar > MarioAvatar strength=15 physicstype=GravityPhysics color=WHITE
        goomba     > Walker     color=BROWN physicstype=GravityPhysics orientation=LEFT
        paratroopa > WalkJumper color=RED prob=.9 physicstype=GravityPhysics orientation=LEFT
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
            
    TerminationSet
        SpriteCounter stype=goal      win=True     
        SpriteCounter stype=avatar    win=False     
           
    InteractionSet
        avatar goomba > killSprite
        avatar paratroopa > killSprite
        avatar EOS  > killSprite
        goomba EOS  > killSprite
        paratroopa EOS  > killSprite
        goal avatar > killSprite
        avatar wall > wallStop friction=0.1
        goomba wall > wallStop friction=0.1
        paratroopa wall > wallStop friction=0.1
        avatar elevator > pullWithIt
        goomba elevator > pullWithIt
        paratroopa elevator > pullWithIt        
        elevator EOS    > wrapAround
        
    LevelMapping
        w > wall
        G > goal
        1 > goomba
        2 > paratroopa
        = > elevator
"""

level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwww
w                          w
w                        1Gw
w             ===       wwww
w                     1    w
w                w  2 ww   w
w                wwwwwww   w
w                          w
w                          w
w          2        2      w
w        www      wwwwww   w
w A      1   ===           w
wwww   wwww        2       w
wwwwwwwwww      wwww       w
"""


# test_level = """
# wwwwwwwwwwwwww
# w        G   w
# w            w
# w            w
# w            w
# w   A        w
# w            w
# w            w
# w            w
# wwwwwwwwwwwwww
# """

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)