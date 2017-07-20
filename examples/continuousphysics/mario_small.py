'''
VGDL example: Mario, jump around! 

@author: Tom Schaul
'''
level1 = """
wwwwwwwwwwwwwwwwwww
w                 w
w             G   w
w             w   w
w            1w   w
w        wwwwww   w
w       Gw        w
w    wwwww        w
w    w            w
w A  w            w
wwwwww G         1w
wwwwwwwwwwwwwwwwwww
""" 

level2 = """
wwwwwwww
w      w
w      w
w    www
w      w
www    w
w     Gw
w    www
wG     w
www    w
w     Gw
w    www
wA     w
wwwwwwww
"""

level3 = """
wwwwwwwwwwwwww
w            w
w            w
w            w
w        1  Gw
w     wwwwwwww
wA           w
wwwwwwwwwwwwww
"""

level4 = """
wwwwwwwwww
w        w
w       Gw
w      www
w        w
w   ww   w
wA       w
www      w
w        w
w        w
w  G     w
wwwwwwwwww
"""

level5 = """
wwwwwww
w     w
w     w
w    Gw
wA  www
ww    w
w     w
w  G  w
wwwwwww
"""

level6 = """
wwwwwwwwwwwwww
w            w
w            w
w            w
w           Gw
wA    wwwwwwww
wwwwwwwwwwwwww
"""

level7 = """
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

level = level5

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
# 

# goomba > Walker orientation=LEFT color=BROWN physicstype=GravityPhysics

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



if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)