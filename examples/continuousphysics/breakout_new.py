game = """
BasicGame
    SpriteSet
        goal1 > Immovable color=BLUE
        goal2 > Immovable color=GREEN
        goal3 > Immovable color=RED
        avatar > HorizontalAvatar speed=0.5
        ball > Missile orientation=DOWN speed=15 color=ORANGE physicstype=NoFrictionPhysics
        lost > Immovable color=BLACK
        obstacle > Immovable color=BLACK

    TerminationSet # from the perspective of player 1 (on the left)
        MultiSpriteCounter stype1=goal1 stype2=goal2 stype3=goal3 limit=0 win=True
        SpriteCounter stype=ball limit=0 win=False

    InteractionSet
        goal1 ball   > killSprite
        ball goal1 > wallBounce
        goal1 ball   > changeScore value=1000
        goal2 ball   > killSprite
        ball goal2 > wallBounce
        goal2 ball   > changeScore value=2000
        goal3 ball   > killSprite
        ball goal3 > wallBounce
        goal3 ball   > changeScore value=3000
        ball avatar > bounceDirection

        ball wall   > wallBounce
        avatar wall > stepBack
        lost ball > killSprite
        ball EOS > killSprite

        ball obstacle   > wallBounce

    LevelMapping
        1 > goal1
        2 > goal2
        3 > goal3
        l > lost
        o > ball
        r > avatar
        v > obstacle
"""

# level = """
# wwwwwwwwwwwwwwwwwwww
# wggggggggggggggggggw
# wggggggggggggggggggw
# wggggggggggggggggggw
# w                  w
# w        o         w
# w                  w
# w                  w
# w                  w
# w        r         w
# """

level1 = """
wwwwwwwwwwwwwwwwwwwwwwwww
w11111111111111111111111w
w22222222222222222222222w
w33333333333333333333333w
w                       w
w           o           w
w                       w
w                       w
w                       w
w                       w
w                       w
w                       w
w           r           w
"""

# Middle wall breakout
level2 = """
wwwwwwwwwwwwwwwwwwwwwwwww
w11111111111111111111111w
w22222222222222222222222w
w33333333333333333333333w
w       vvvvvvvvv       w
w           o           w
w                       w
w                       w
w                       w
w                       w
w                       w
w                       w
w           r           w
"""


# Offset paddle breakout
level3 = """
wwwwwwwwwwwwwwwwwwwwwwwww
w11111111111111111111111w
w22222222222222222222222w
w33333333333333333333333w
w                       w
w           o           w
w                       w
w                       w
w                       w
w                       w
w           r           w
w                       w
w                       w
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level2)
