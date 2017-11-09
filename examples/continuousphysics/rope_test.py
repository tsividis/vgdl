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
w                 w
w                 w
w                 w
w                Gw
w   A          llww
w  www         l  w
w              l  w
w              l  w
w              l  w
w              l  w
w              l  w
w              l  w
w              l  w
w              l  w
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

    TerminationSet
        SpriteCounter stype=goal      win=True
        SpriteCounter  stype=avatar win=False

    InteractionSet
        avatar goomba > killSprite
        avatar EOS  > killSprite
        goal avatar > killSprite
        avatar wall > killIfTooFast speed=19
        avatar wall > wallStop
        # wall avatar > killSprite
        avatar rope > onRope
        avatar ladder > onLadder

    LevelMapping
        w > wall
        G > goal
        A > avatar
        r > rope
        l > ladder
        x > avatar ladder
        

"""
level_game_pairs = [[game, level]]
if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
