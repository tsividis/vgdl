

level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                              w
w                              w
w                              w
w             A1               w

"""

game="""
BasicGame
    SpriteSet
        box    > Resource    color=WHITE 
        avatar  > MovingAvatar color=DARKBLUE # stype=sam
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
        box avatar > cloneSprite
        avatar box > stepBack
    TerminationSet
        # SpriteCounter stype=box limit=10 win=False
        # Termination

"""
level_game_pairs = [[game, level]]


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    # parse, run and play.
    VGDLParser.playGame(game, level)
