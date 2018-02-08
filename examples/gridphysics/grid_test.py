level = """
wwwwwwwwwwwwwwwwwww
w      k       PPPw
w          A   P Gw
wwwwwwwwwwwwwwwwwww
"""

game = """
BasicGame
    SpriteSet
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
        poison > Immovable color=RED
        avatar > MovingAvatar strength=15 color=WHITE
        key > Resource limit=1 color=GOLD

    TerminationSet
        SpriteCounter stype=goal      win=True
        SpriteCounter  stype=avatar win=False

    InteractionSet

        goal avatar > killSprite
        avatar wall > stepBack
        avatar poison > killIfHasLess resource=key limit=0
        key avatar > killSprite
        avatar key > changeResource resource=key value=1
    LevelMapping
        w > wall
        G > goal
        A > avatar
        k > key
        P > poison

"""
level_game_pairs = [[game, level]]
if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
