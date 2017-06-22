levels = {}
i = 7

game = """
BasicGame
    SpriteSet
        inertial >
            avatar > InertialAvatar color=WHITE 
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
            
    TerminationSet
        SpriteCounter stype=goal   win=True     
        SpriteCounter stype=avatar    win=False     
           
    InteractionSet
        goal avatar > killSprite
        avatar wall > wallStop friction=0
        
        
    LevelMapping
        w > wall
        G > goal
"""


levels[1] = """
wwwwwwwwwww
w         w
w         w
w  wwwww  w
w  wwwww  w
w  wwwww  w
w    w    w
w   GwA   w
wwwwwwwwwww
"""#failed

levels[2] = """
wwwwwwwwww
wG      Gw
w        w
w  wwww  w
w  wwww  w
w  wwww  w
w  wwww  w
w        w
wA      Gw
wwwwwwwwww
"""#works

levels[3] = """
wwwww
w  Gw
w   w
wAw w
wwwww
"""#doesnt terminate

levels[4] = """
wwwwwwwwwww
wG   A   Gw
wwwwwwwwwww
"""#only works with LIMIT >= 4

levels[5] = """
wwwwwwwwwwww
w      ww Gw
w      ww  w
w  ww  ww  w
w  ww  ww  w
w  ww  ww  w
w  ww  ww  w
w  ww  ww  w
w  ww  ww  w
w  ww      w
wA ww      w
wwwwwwwwwwww
"""#works

levels[6] = """
wwwwwww
w     w
w  w  w
w  w  w
w  w  w
wA w Gw
wwwwwww
"""

levels[7] = """
wwwwwwwwww
w     w Gw
w     w  w
w  w  w  w
w  w     w
wA w     w
wwwwwwwwww
"""


level = levels[i]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)