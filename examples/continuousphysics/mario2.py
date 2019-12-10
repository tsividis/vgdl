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
        box > Passive color=PINK
        wall > Immovable color=BLACK
            
    TerminationSet
        SpriteCounter stype=goal      win=True     
        SpriteCounter stype=avatar    win=False     
           
    InteractionSet
        # avatar box > bounceForward
        box avatar > bounceForwardContinuous
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
        b > box
        = > elevator
"""

level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwww
w                          w
w                         Gw
w             ===       wwww
w                          w
w                w    ww   w
w                wwwwwww   w
w                          w
w                          w
w                          w
w        www      wwwwww   w
w            ===           w
w  A   b                   w
wwwwwwwwwwwwwwwwwwww       w
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