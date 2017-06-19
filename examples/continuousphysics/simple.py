levels = {}
i = 3

game = """
BasicGame
    SpriteSet 
        avatar > InertialAvatar color=WHITE
        evil   >  orientation=LEFT speed=0.01
                goomba     >  Walker color=BROWN 
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
        poison > Immovable color=RED
            
    TerminationSet
        SpriteCounter stype=goal  limit=0  win=True     
        SpriteCounter stype=avatar    win=False     
           
    InteractionSet
        goal avatar > killSprite
        avatar wall > wallStop friction=0.0
        evil wall > wallStop friction=0.0
        avatar poison > killSprite
        avatar evil > killIfAlive
        evil EOS > wrapAround
        
        
    LevelMapping
        w > wall
        G > goal
        P > poison
        1 > goomba
"""


levels[1] = """
wwwwwww
w     w
w     w
w     w
w    Gw
wA    w
wwwwwww
"""#works

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
wwwwwww
w    Gw
w     w
w     w
w     w
wA    w
wwwwwww
"""#doesnt terminate

levels[4] = """
wwwwwwwwwww
wG   A   Gw
wwwwwwwwwww
"""#only works with LIMIT >= 4

level = levels[i]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)