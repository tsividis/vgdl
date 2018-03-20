level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                   M   ww     w
w                   M   w      w
w                              w
w               w              w
w               A              w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

game="""
BasicGame
    SpriteSet
        missile > Missile color=RED orientation=RIGHT cooldown=1
        avatar > MovingAvatar color=DARKBLUE
        
    LevelMapping
        A > avatar
        M > missile

    InteractionSet
        avatar wall > stepBack
        missile wall > stepBack

    TerminationSet
        Termination


"""
level_game_pairs = [[game, level]]


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    # parse, run and play.
    VGDLParser.playGame(game, level)
