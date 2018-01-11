
level = """

wwwwwwwwwwwwwwwwwwwwwwwwwwww
w    d     Gw              w
w0000000000000000      000 w
w00000000000000000000  000 w
w00000000000000000000 00000w
www000ww000www    www  wwwww
w000000000000000000000 0000w
w00 000000000000000000  000w
w00 000x000000000000000  00w
w       A                  w
wwwwwwwwwwwwwwwwwwwwwwwwwwww

"""


game = """
BasicGame
    SpriteSet
        water > Immovable color=BLUE
        goal   > Immovable color=GREEN
        wall > Immovable color=BLACK           
        ferry > Chaser color=PINK stype=dock
        dock > Immovable color=LIGHTGREEN
    InteractionSet
        goal avatar  > killSprite
        avatar wall  > stepBack
        ferry wall > stepBack
        avatar water > killSprite
        avatar ferry > pullWithIt
    TerminationSet
        SpriteCounter stype=goal   limit=0 win=True
        SpriteCounter stype=avatar limit=0 win=False
    
    LevelMapping
        G > goal
        0 > water
        w > wall
        x > ferry water

"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    