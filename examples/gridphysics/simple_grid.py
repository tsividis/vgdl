game = """
BasicGame frame_rate=30
    SpriteSet 
        avatar > MovingAvatar color=WHITE
        evil   >  
            goomba     > Immovable color=BROWN 
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
        poison > Immovable color=RED
            
    TerminationSet
        SpriteCounter stype=goal  limit=0  win=True     
        SpriteCounter stype=avatar    win=False     
           
    InteractionSet
        goal avatar > killSprite
        avatar wall > stepBack
        avatar poison > killSprite
        avatar evil > killIfAlive
        
        
    LevelMapping
        w > wall
        G > goal
        P > poison
        1 > goomba
"""



level = """
wwwwwwwwwww
wG   A   Gw
wwwwwwwwwww
"""

level = """
wwwwwwwwww
wA      Gw
wwwwwwwwww
"""

level = """
wwwwwwwwww
w        w
w wwwwww w
w w  A   w
w w wwwwww
w w w    w
w w w    w
w w wwwwww
wGw1     w
wwwwwwwwww
"""

level = """
wwwwwwwwwww
wG   A   Gw
wwwwwwwwwww
"""

level = """
wwwwwww
w    Gw
w     w
ww   ww
w     w
wA    w
wwwwwww
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)