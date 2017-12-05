# level = """
# wwwwwwwwwwwwwww
# w     r       w
# w     r       w
# w     r       w
# w A          Gw
# wwww       llww
# w          l  w
# w          l  w
# wwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwww
# w     r           w
# w     r           w
# w     r           w
# w A              Gw
# wwww           llww
# w              l  w
# w              l  w
# wwwwwwwwwwwwwwwwwww
# """

level = """
wwwwwwwwwwwwwwwwwww
w     r           w
w     r           w
w     r           w
w A              Gw
wwww           llww
w              l  w
w          k   l  w
wwwwwwwwwwwwwwwwwww
"""

level = """
wwwwwwwwwwwwwwwwwww
w                 w
w                 w
w                 w
w                 w
w                 w
w                 w
w          A k k Gw
wwwwwwwwwwwwwwwwwww
"""


# level = """
# wwwwwwwwwwwwwwwwwww
# w                 w
# w                 w
# w                 w
# w                Gw
# w   A          llww
# w  www         l  w
# w              l  w
# w              l  w
# w              l  w
# w              l  w
# w              l  w
# w              l  w
# w              l  w
# w              l  w
# wwwwwwwwwwwwwwwwwww
# """

level = """
wwwwwwwwwwwwwwwwwww
w                 w
w                 w
w                 w
w                Gw
w     A        llww
w    www       l  w
w                 w
w                 w
w                 w
wwwwwwwwwwwwwwwwwww
"""

game = """
BasicGame
    SpriteSet
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
        rope > Immovable color=RED
        ladder > Immovable color=BLUE
        avatar > MarioAvatar strength=15 physicstype=GravityPhysics color=WHITE
        key > Resource limit=2 color=GOLD

    TerminationSet
        SpriteCounter stype=goal      win=True
        SpriteCounter  stype=avatar win=False

    InteractionSet
        # avatar goomba > killSprite
        # avatar EOS  > killSprite
        goal avatar > killSprite
        avatar wall > killIfTooFast speed=21
        avatar wall > wallStop
        # wall avatar > killSprite
        # avatar rope > onRope
        # avatar ladder > onLadder
        # goal avatar > killIfOtherHasMore resource=key limit=2
        key avatar > killSprite
        avatar key > changeResource resource=key value=1
    LevelMapping
        w > wall
        G > goal
        A > avatar
        r > rope
        l > ladder
        x > avatar ladder
        k > key
        

"""
level_game_pairs = [[game, level]]
if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
