'''
VGDL example: a simple cat-and-mouse/predator-prey chase game.

Careful: goats get angry when you see a dead goat...

@author: Tom Schaul
'''


game = """
BasicGame
    SpriteSet
        carcass > Immovable color=BROWN
        goat > stype=avatar cooldown=3
            angry  > Chaser  speed=1 color=ORANGE
            scared > Fleeing speed=1 color=BLUE

    InteractionSet
        goat   wall    > stepBack
        avatar wall    > stepBack
        avatar  angry  > killSprite
        carcass scared > killSprite
        carcass avatar > nothing
        scared avatar  > transformTo stype=carcass
        scared carcass > transformTo stype=angry

    LevelMapping
        0 > scared
        1 > angry
    TerminationSet
        SpriteCounter stype=scared win=True
        SpriteCounter stype=avatar win=False

"""

level = """
wwwwwwwwwwwwwwwwwwwwwwww
wwww    w0  ww      0www
w     w w       ww    ww
w   0   0 ww  A www    w
w wwww wwwww    ww   www
w        w  1      0  ww
ww   w0     ww   www   w
ww    ww   wwww    w   w
www              w     w
wwwwww   0  wwwwww    ww
wwwwwwwwwwwwwwwwwwwwwwww
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
