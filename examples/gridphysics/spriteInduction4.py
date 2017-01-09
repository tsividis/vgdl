'''
VGDL example: a simple cat-and-mouse/predator-prey chase game.

Careful: goats get angry when you see a dead goat...

@author: Tom Schaul
'''


chase_game = """
BasicGame
    SpriteSet
        carcass > Immovable color=BROWN
        angry  > Missile color=ORANGE
        hay > Passive color=YELLOW


    InteractionSet
        avatar  wall   > stepBack
        angry   wall   > stepBack
        avatar  angry  > killSprite
        carcass avatar > killSprite
        hay     avatar  > killSprite

    LevelMapping
        a > angry
        c > carcass
        h > hay

    TerminationSet
        SpriteCounter stype=hay win=True
        SpriteCounter stype=avatar win=False

"""

chase_level = """
wwwwwwwwwwwwwwwwwwwwwwww
wwww        ww        ww
w                     ww
w         h    A       w
w wwww               www
w                     ww
ww                     w
ww                     w
www                    w
www              a c   w
w                      w
wwwwwwwwwwwwwwwwwwwwwwww
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(chase_game, chase_level)