

level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w  C     C              1     Cw
w             C         1      w
w1111111111    C        1111111w
w         1   C2C  C        2  w
w         1  C C         C     w
w    C         A               w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww

"""

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                              w
# w                              w
# w             1         A      w
# w                              w
# w                              w
# w             1 1              w

# """

game="""
BasicGame
    SpriteSet
        cloner > Immovable color=GREEN
        box    > Immovable color=WHITE  #orientation=LEFT cooldown=2
        flicker > Flicker timeout=5 color=GREEN
        random > RandomNPC color=PURPLE
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
        avatar box > stepBack
        random wall > stepBack
        random box > stepBack

        random cloner > cloneSprite
        cloner random > killSprite

        random avatar > killSprite

    TerminationSet
        SpriteCounter stype=box limit=0 win=False
        # Termination

"""
level_game_pairs = [[game, level]]


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    # parse, run and play.
    VGDLParser.playGame(game, level)
