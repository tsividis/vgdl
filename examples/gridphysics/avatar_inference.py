

level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                              w
w                              w
w             A                w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

game="""
BasicGame
    SpriteSet
        box    > Missile    color=WHITE orientation=RIGHT cooldown=2
        avatar  > RotatingAvatar color=DARKBLUE stype=sam
        cannon > SpawnPoint color=RED stype=box spawnCooldown=5
        missile > Missile
            sam  > orientation=UP color=BLUE singleton=True
        # sam > Flicker limit=5
        wall > Immovable color=DARKGRAY
    LevelMapping
        0 > base
        1 > box
        w > wall
        c > cannon
        s > sam
        A > avatar
    InteractionSet
        avatar  EOS  > stepBack
        sam EOS  > killSprite
        sam box > killSprite
        box sam > killSprite
        box wall > killSprite
    TerminationSet
        SpriteCounter      stype=avatar               limit=0 win=False
        # Termination

"""
level_game_pairs = [[game, level]]


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    # parse, run and play.
    VGDLParser.playGame(game, level)
