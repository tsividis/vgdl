level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                              w
w                              w
w          F    S              w
w               A              w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

game="""
BasicGame
    SpriteSet
        missile > Missile color=RED orientation=RIGHT cooldown=1
        avatar > MovingAvatar color=DARKBLUE
        out > Immovable color=BLUE
        teleporter > Immovable color=WHITE stype=out
        
    LevelMapping
        A > avatar
        M > missile
        F > out
        S > teleporter
    InteractionSet
        avatar teleporter > teleportToExit

    TerminationSet
        Termination


"""
level_game_pairs = [[game, level]]


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    # parse, run and play.
    VGDLParser.playGame(game, level)
