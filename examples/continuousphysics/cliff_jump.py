level = """
wwwwwwwwwwwwwwwwwwww
w                  w
w                  w
w        A         w
w      wwwww    wwww
w                  w
w                  w
w                  w
w                  w
w                  w
w                  w
w        G         w
wwwwwwwwwwwwwwwwwwww
"""

game = """
BasicGame
    SpriteSet

        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
        avatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE

    TerminationSet
        SpriteCounter stype=goal      win=True
        SpriteCounter stype=avatar    win=False

    InteractionSet
        avatar EOS  > killSprite
        goal avatar > killSprite
        avatar wall > killIfTooFast
        avatar wall > wallStop


    LevelMapping
        w > wall
        G > goal

"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)