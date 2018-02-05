

level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                              w
w                              w
w              2               w
w             111              w
w             1A1              w

"""

game="""
BasicGame
    SpriteSet
        box    > Immovable color=WHITE # orientation=LEFT cooldown=2
        flicker > Flicker timeout=5 color=GREEN
        random > Chaser color=PURPLE cooldown=1 stype=avatar
        avatar  > MovingAvatar color=DARKBLUE stype=sam
        cannon > SpawnPoint color=RED stype=box spawnCooldown=5
        missile > Missile
            sam  > orientation=UP color=BLUE singleton=True
        # sam > Flicker limit=5
        wall > Immovable color=DARKGRAY
    LevelMapping
        F > flicker
        0 > base
        1 > box
        2 > random
        w > wall
        c > cannon
        s > sam
        A > avatar
    InteractionSet
        # box avatar > cloneSprite
        # avatar box > stepBack
        box random > killSprite
        random box > cloneSprite
    TerminationSet
        # SpriteCounter stype=box limit=10 win=False
        # Termination

"""
level_game_pairs = [[game, level]]


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    # parse, run and play.
    VGDLParser.playGame(game, level)
