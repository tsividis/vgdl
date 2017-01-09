'''
VGDL example: a simple cat-and-mouse/predator-prey chase game.

Careful: goats get angry when you see a dead goat...

@author: Tom Schaul
'''


chase_game = """
BasicGame
    SpriteSet
        carcass > Immovable color=BROWN
        goat > stype=avatar cooldown=3
            angry  > Chaser speed=0.5 color=ORANGE
        hay > Passive color=YELLOW


    InteractionSet
        goat    wall   > stepBack
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
ww          ww        ww
w                     ww
w         h    A       w
w                    www
w                      w
w                a c   w
w                      w
wwwwwwwwwwwwwwwwwwwwwwww
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(chase_game, chase_level)