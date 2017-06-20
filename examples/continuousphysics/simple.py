levels = {}
i = 6

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
wA  w
wwwww
"""#doesnt terminate

levels[4] = """
wwwwwwwwwww
wG   A   Gw
wwwwwwwwwww
"""#only works with LIMIT >= 4

levels[5] = """
wwwwwwwwww
w     w Gw
w     w  w
w  w  w  w
w  w     w
wA w     w
wwwwwwwwww
"""#works

levels[6] = """
wwwwwww
w     w
w     w
w     w
w     w
wA w Gw
wwwwwww
"""


level = levels[i]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)