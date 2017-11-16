level = """
wwwwwwwwwwwww
w     r     w
w     r     w
w     r     w
wA         Gw
wwww     wwww
w           w
w           w
wwwwwwwwwwwww
"""

game = """
BasicGame
    SpriteSet
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
        rope > Immovable color=RED
        avatar > MarioAvatar strength=15 physicstype=GravityPhysics color=WHITE

    TerminationSet
        SpriteCounter stype=goal      win=True
        SpriteCounter  stype=avatar win=False

    InteractionSet

        avatar goomba > killSprite
        avatar EOS  > killSprite
        goal avatar > killSprite
        # avatar wall > killIfTooFast speed=40
        avatar wall > wallStop
        avatar rope > onRope


    LevelMapping
        w > wall
        G > goal
        A > avatar
        r > rope
        

"""
level_game_pairs = [[game, level]]
if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
