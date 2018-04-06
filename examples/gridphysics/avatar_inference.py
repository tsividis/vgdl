

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

# up, up, up, up, left
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w              1             1 w
# w                            1 w
# w              2               w
# w                    2         w
# w              A          3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

#combine with avatar sam bounceFoward. works.
#0,0,0,0,0,0
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w                              w
# w              A               w
# w                         3 3  w
# w         c    c               w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# TODO: You need to be able to re-run testAndExpand() when no hypotheses pass your filter
## the problem here is that you need to build on expandSprite proposals with expandLine within one errorMap and
## you don't ordinarily do that.
#0,0,0,0,0,0
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w                              w
# w                              w
# w              A          3 3  w
# w         c    c               w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# works if you don't allow the eventHandler to apply effects to newly-created sprites
#[0,0,0,K_LEFT, K_LEFT,0,0]
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w                              w
# w                              w
# w                         3 3  w
# w         c    c A             w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# #up, up, down
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w              1               w
# w              1               w
# w              A          3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

#0,0,0,0,0,0,0
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w              1               w
# w              1               w
# w              A          3 3  w
# w   c   c                      w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

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

# super wacky level: add
# cannon sam > stepBack
# sam cannon > stepBack
#, then push a cannon into the missles from another
# spoiler: it teleports back to where it started O.o
level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                            1 w
w                            1 w
w            c    A            w
w  c                           w
w                         3 3  w
w         c                    w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""


game="""
BasicGame
    SpriteSet
        cloner > Immovable color=GREEN
        box    > Immovable color=WHITE # orientation=RIGHT cooldown=1
        box2 > Immovable color=GREEN
        box3 > Immovable color=YELLOW
        flicker > Flicker timeout=1 color=ORANGE
        random > RandomNPC color=PURPLE speed=1 cooldown=1
        chaser > Chaser color=BLACK speed=1 cooldown=1 stype=box
        avatar  > MovingAvatar color=DARKBLUE 
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
        missile > Missile
            sam  > orientation=UP color=BLUE singleton=False cooldown=1
        wall > Immovable color=DARKGRAY
    LevelMapping
        C > cloner
        F > flicker
        0 > base
        1 > box
        2 > box2
        3 > box3
        4 > random
        w > wall
        c > cannon
        s > sam
        A > avatar
    InteractionSet
        avatar wall > stepBack
        # box avatar > nothing
        box avatar > transformTo stype=box2
        # cannon sam > stepBack
        # sam cannon > stepBack
        box2 avatar > killSprite
        # box2 avatar > bounceForward
        box3 avatar > killSprite
        cannon avatar > bounceForward
        avatar sam > bounceForward
        cannon sam > stepBack
        sam cannon > stepBack

    TerminationSet
        SpriteCounter stype=box3 limit=0 win=True
        # SpriteCounter stype=box3 limit=0 win=False
        Termination


"""
level_game_pairs = [[game, level]]


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    # parse, run and play.
    VGDLParser.playGame(game, level)
