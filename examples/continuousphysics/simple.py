levels = {}
i = 1

game = """
BasicGame
    SpriteSet
        avatar > InertialAvatar color=WHITE 
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
        poison > Immovable color=RED
            
    TerminationSet
        SpriteCounter stype=goal   win=True     
        SpriteCounter stype=avatar    win=False     
           
    InteractionSet
        goal avatar > killSprite
        avatar wall > wallStop friction=0
        avatar poison > killSprite
        
        
    LevelMapping
        w > wall
        G > goal
        p > poison
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
w          w
w w  G     w
w  w   w  Gw
w   w   w  w
w    G   w w
w     w    w
w     wG   w
w     w    w
w          w
wA         w
wwwwwwwwwwww
"""#works

levels[6] = """
wwwwwww
w G p w
w     w
w     w
w     w
wA    w
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