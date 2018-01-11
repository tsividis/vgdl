'''
VGDL example: a simple cat-and-mouse/predator-prey chase game.

Careful: goats get angry when you see a dead goat...

@author: Tom Schaul
'''


game = """
BasicGame
    SpriteSet
        carcass > Immovable color=BROWN
        angry  > Missile color=ORANGE speed=0.5
        hay > Passive color=YELLOW
        goal > ResourcePack color=RED
        wall > Immovable color=DARKGRAY
        avatar > MovingAvatar

    InteractionSet
        avatar  wall   > stepBack
        angry   wall   > stepBack
        avatar  angry  > killSprite
        carcass avatar > killSprite
        hay     avatar  > killSprite
        goal avatar > killSprite

    LevelMapping
        a > angry
        c > carcass
        h > hay
        g > goal

    TerminationSet
        SpriteCounter stype=hay win=True
        SpriteCounter stype=avatar win=False
        SpriteCounter stype=goal win=True

"""

level = """
wwwwwwwwwwwwwwwwwwwwwwww
wwww        ww        ww
w                     ww
w         h    A       w
w wwww               www
w                     ww
ww           g         w
ww                     w
www                    w
www              a c   w
w                      w
wwwwwwwwwwwwwwwwwwwwwwww
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)