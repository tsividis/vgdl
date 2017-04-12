
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
        avatar > MovingAvatar color=DARKBLUE       
        forest > SpawnPoint stype=log prob=0.4 cooldown=10 color=RED
        structure > Immovable
            poison > color=BLUE
            goal  > color=GREEN
        # defining 'wall' last, makes the walls show on top of all other sprites
        wall > Immovable

    InteractionSet
        goal avatar  > killSprite
        avatar wall  > stepBack
        avatar poison > killSprite
        avatar poison > changeResource
        avatar truck > killSprite

    
    TerminationSet
        SpriteCounter stype=goal   limit=0 win=True
        SpriteCounter stype=avatar limit=0 win=False
    
    LevelMapping
        G > goal
        0 > poison

"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random
    levels = [l for l in locals().keys() if 'level' in l]
    index = random.choice(range(len(levels)))
    VGDLParser.playGame(game, locals()[levels[index]])   