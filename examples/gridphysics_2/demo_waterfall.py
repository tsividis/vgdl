'''
VGDL example: Frogger Transpose

'''
## If you put the goal at the bottom, something fails. Same bug as in frogs??
# level = """
# wwwwwww00000000wwwwwww
# w      00000000  G   w
# w      ====0000      w
# w      00~~~000      w
# w      00000000      w
# w      000===00      w
# w      00000000      w
# w      0000~~~0      w
# w      00000000      w
# w      00000000      w
# w      00000000      w
# w      00000===      w
# w   A  00000000      w
# wwwwwww00000000wwwwwww
# """

level = """
www      000       www
w        000     G   w
w      ====0000      w
w      00===000      w
w      00000000      w
w      000===00      w
w      00000000      w
w      ========      w
w      00000000      w
w      00000000      w
w      00000000      w
w      00000===      w
w   A    0000        w
www      0000      www
"""



game = """

BasicGame
    SpriteSet

        structure > Immovable
            water > color=BLUE
            goal  > color=ORANGE

        stationary > Immovable
            rock > color=PINK
        float    > Missile
            leaf > orientation=UP color=GREEN
                leaf1 > speed=0.1
                leaf2 > speed=0.15
            log > orientation=UP color=BROWN
                log1 > speed=0.5
                log2 > speed=0.15

        safety > Resource  limit=2 color=WHITE
        # defining 'wall' last, makes the walls show on top of all other sprites
        wall > Immovable color=GRAY
        avatar > MovingAvatar color=DARKBLUE
    InteractionSet
        goal avatar  > killSprite
        avatar float   > changeResource resource=safety value=2
        avatar float   > pullWithIt   # note how one collision can have multiple effects
        avatar wall  > stepBack
        avatar water > killIfHasLess  resource=safety limit=0
        avatar water > changeResource resource=safety value=-1
        float    EOS   > wrapAround
        avatar EOS > stepBack

    TerminationSet
        SpriteCounter stype=goal   limit=0 win=True
        SpriteCounter stype=avatar limit=0 win=False

    LevelMapping
        G > goal
        0 > water
        p > rock
        + > water rock
        = > water log1
        - > water leaf1
        ~ > water log2
        _ > water leaf2
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
