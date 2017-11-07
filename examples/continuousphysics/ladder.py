game = """
BasicGame
    SpriteSet
        background > Immovable color=LIGHTGRAY
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
        ladder > Immovable color=YELLOW

        avatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE
        ladderavatar > VerticalAvatar speed=0.3 color=WHITE

    TerminationSet
        SpriteCounter stype=goal      win=True
        MultiSpriteCounter stype1=avatar stype2=ladderavatar win=False

    InteractionSet

        avatar EOS  > killSprite
        ladderavatar EOS > killSprite
        goal avatar > killSprite
        avatar wall > wallStop

        ladderavatar background > transformTo stype=avatar
        avatar ladder > transformTo stype=ladderavatar

    LevelMapping
        . > background
        w > background wall
        G > background goal
        l > background ladder
"""

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