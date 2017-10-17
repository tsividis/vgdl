game = """
BasicGame
    SpriteSet
        background > Immovable color=LIGHTGRAY
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
        ladder > Immovable color=YELLOW
        avatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE
        

    TerminationSet
        SpriteCounter stype=goal      win=True
        SpriteCounter stype=avatar     win=False

    InteractionSet

        avatar EOS  > killSprite
        goal avatar > killSprite
        avatar wall > wallStop

    LevelMapping
        . > background
        w > background wall
        G > background goal
        l > background ladder
"""

#ladderavatar > VerticalAvatar speed=0.3 color=WHITE
#

level = """
wwwwwwww
w......w
w.....Gw
wwwlwwww
w..l...w
w..l...w
w......w
w..A...w
wwwwwwww
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)