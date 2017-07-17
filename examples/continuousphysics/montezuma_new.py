# level = """
# wwwwwwwwwwwwwwwwwwww
# w                  w
# wG       A        Gw
# wwww   wwlww    wwww
# w        l         w
# w                  w
# wwwl  wwwwwww   lwww
# w  l            l  w
# wG        1        w
# wwwwwwwwwwwwwwwwwwww
# """

level = """
wwwwwwwwwwwwwwwwwwww
w..................w
w..................w
wG.........A.......w
wwww...wwlww....wwww
wk.......l.........w
w..................w
w..................w
wwwl..wwwwwww...lwww
w..l............l..w
w..l............l..w
w.........1........w
wwwwwwwwwwwwwwwwwwww
"""

# game = """
# BasicGame
#     SpriteSet
#         avatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE
#         ladderavatar > VerticalAvatar speed=0.3 color=WHITE
#         goomba > Missile orientation=LEFT color=BROWN speed=0.2
#         goal > Immovable color=GREEN
#         wall > Immovable color=BLACK
#         ladder > Immovable color=YELLOW
#
#     TerminationSet
#         SpriteCounter stype=goal      win=True
#         MultiSpriteCounter stype1=avatar stype2=ladderavatar   win=False
#
#     InteractionSet
#
#         avatar goomba > killSprite
#         avatar EOS  > killSprite
#         goomba EOS > killSprite
#         goal avatar > killSprite
#         avatar wall > wallStop
#         goomba wall > wallBounce
#
#         avatar ladder > transformTo stype=ladderavatar
#         ladderavatar wall > transformTo stype=avatar
#
#     LevelMapping
#         w > wall
#         G > goal
#         1 > goomba
#         l > ladder
# """

game = """
BasicGame
    SpriteSet
        background > Immovable color=LIGHTGRAY
        goomba > Missile orientation=LEFT color=BROWN speed=0.2
        goal > Immovable color=GREEN
        key > Resource color=GOLD
        wall > Immovable color=BLACK
        ladder > Immovable color=YELLOW

        avatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE
        ladderavatar > VerticalAvatar speed=0.3 color=WHITE
        keyavatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE
        keyladderavatar > VerticalAvatar speed=0.3 color=WHITE

    TerminationSet
        SpriteCounter stype=goal      win=True
        MultiSpriteCounter stype1=avatar stype2=ladderavatar stype3=keyavatar stype4=keyladderavatar win=False

    InteractionSet

        avatar goomba > killSprite
        avatar EOS  > killSprite
        goomba EOS > killSprite
        avatar goal > stepBack
        goal keyavatar > killSprite
        key avatar > killSprite
        avatar key > transformTo stype=keyavatar
        avatar wall > wallStop
        goomba wall > wallBounce

        keyavatar goomba > killSprite
        keyavatar EOS  > killSprite
        keyavatar wall > wallStop

        ladderavatar background > transformTo stype=avatar
        avatar ladder > transformTo stype=ladderavatar

        keyladderavatar background > transformTo stype=keyavatar
        keyavatar ladder > transformTo stype=keyladderavatar

    LevelMapping
        . > background
        w > background wall
        G > background goal
        1 > background goomba
        l > background ladder
        k > background key
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
