

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w  C     C              1     Cw
# w             C         1      w
# w1111111111    C        1111111w
# w         1   C2C  C        2  w
# w         1  C C         C     w
# w    C         A               w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww

# """

level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w             A                w
w                              w
w             1 C              w
w                              w
w                              w
w             1 1              w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                       1      w
# w                       1      w
# w1111111111    C        1111111w
# w         1   C2C           2  w
# w         1    C               w
# w              A               w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                              w
# w                              w
# w                              w
# w            1 C               w
# w                              w
# w                      A       w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """



game="""
BasicGame
    SpriteSet
        cloner > Immovable color=GREEN
        box    > Missile color=WHITE orientation=RIGHT cooldown=2
        flicker > Flicker timeout=5 color=ORANGE
        random > RandomNPC color=PURPLE speed=1
        avatar  > MovingAvatar color=DARKBLUE stype=sam
        cannon > SpawnPoint color=RED stype=box spawnCooldown=5
        missile > Missile
            sam  > orientation=UP color=BLUE singleton=True
        # sam > Flicker limit=5
        wall > Immovable color=DARKGRAY
    LevelMapping
        C > cloner
        F > flicker
        0 > base
        1 > box
        2 > random
        w > wall
        c > cannon
        s > sam
        A > avatar
    InteractionSet
        avatar wall > stepBack
        box avatar > killSprite
        random wall > stepBack
        random box > stepBack
        box cloner > cloneSprite
        cloner box > killSprite

        random avatar > killSprite

    TerminationSet
        SpriteCounter stype=box limit=0 win=False


"""
level_game_pairs = [[game, level]]


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    # parse, run and play.
    VGDLParser.playGame(game, level)
