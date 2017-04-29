
level = """

wwwwwwwwwwwwwwwwwwwwwwwwwwww
w           wG             w
w0000000000000000      000 w
w00000000000000000000  000 w
w00000000000000000000 00000w
www   ww   www    www  wwwww
w000000000000000000000 0000w
w00 000000000000000000  000w
w00 0000000000000000000  00w
w       A                  w
wwwwwwwwwwwwwwwwwwwwwwwwwwww

"""


game = """
BasicGame
    SpriteSet
        poison > Immovable color=BLUE
        goal   > Immovable color=GREEN
        wall > Immovable color=BLACK           
        
    InteractionSet
        goal avatar  > killSprite
        avatar wall  > stepBack
        avatar poison > killSprite

    TerminationSet
        SpriteCounter stype=goal   limit=0 win=True
        SpriteCounter stype=avatar limit=0 win=False
    
    LevelMapping
        G > goal
        0 > poison
        w > wall

"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    