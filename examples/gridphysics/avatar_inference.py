

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


## TEST1
#[K_UP, K_UP, K_UP, K_UP, K_LEFT]
## combine with transform box1 to box2
# and box2 nothing
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

## TEST2
# [K_UP, K_UP, K_UP]
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

## TEST3
#[K_LEFT, K_UP, K_UP]
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w              1             1 w
# w                            1 w
# w              2               w
# w                    2         w
# w              1A         3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

## TEST4
# [[K_LEFT], [K_UP, K_UP, K_UP]]
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w              1             1 w
# w                            1 w
# w               2              w
# w                    2         w
# w              1A         3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

## TEST5
#combine with avatar sam bounceFoward. works.
#[0]*6
# # works 4/12
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w              A             1 w
# w                              w
# w                              w
# w         c    c          3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

## TEST6
#[0]*10
# combine with sam wall reverseDirection
# works 4/12
level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                            1 w
w                            1 w
w                              w
w         wwwwww               w
w                         3 3  w
w         s    s A             w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

## TEST7
#up, up, up, right
## tests whether we can learn randomNPCs and know that the box we push isn't a randomNPC
## i.e., a good test of randomNPC likelihood and theory prior().
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                           3  w
# w                 2            w
# w          4                3  w
# w                      2       w
# w     4                        w
# w                      A       w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

## TEST8
# Not getting this one because we stepBack with the missile
## but our best theories are almost right.
#left, left, left, left, left, left, left, 0
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w            c    A            w
# w  c                           w
# w                         3 3  w
# w         c                    w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# #up, up
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w              m               w
# w              m               w
# w              A          3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# works for changeResource, killIfOtherHasMore/Less.
#up, up, up, up
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w              p             1 w
# w              m             1 w
# w              m               w
# w              p               w
# w              A          3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

## diagnoses ability to learn preconditions across multiple episodes. works.
# works with avatar poison > killIfHasLess/More
#[up],[left,left,left,left]
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w                              w
# w              p               w
# w          pmm A          3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# [0]*11: test for wrapAround (add sam EOS wrapAround to rules)
# level = """
# wwwwwwwwwwwwwwwww
# w         3 3   w
# w               w
# w  s   s   A    w
# w               w
# wwwwwwwwwwwwwwwww
# """


# testing when poisons make you step back
# works
# #left, up, up, up, up
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w              p             1 w
# w              m             1 w
# w              m               w
# w                              w
# w             pA          3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# tests shootavatar, flakavatar. combine with sam wall killSprite
#[K_RIGHT, K_UP, K_SPACE, 0, 0,0,0,0]
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w                              w
# w                              w
# w              A          3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

## Add a game where we do stepback and killSprite


# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w        c                     w
# w                              w
# w           c                  w
# w                              w
# w      11 22 A            3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwww
# wA     w
# w      w
# w    3 w
# wwwwwwww
# """

## combine with box2 avatar killsprite.
## if you use box2 avatar bounceForward this could be
## a good test of whether re-doing testAndExpand helps.
# works 4/11
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
# w              A               w
# w         c    c          3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# works if you don't allow the eventHandler to apply effects to newly-created sprites
# Note: this is much slower when you have more intParis, i.e., when you move things down a row.
# It's actually too slow even when things are up a row.
# [0,0,0,K_LEFT, K_LEFT,0,0]
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                            1 w
# w                              w
# w                              w
# w         c    c A        3 3  w
# w                              w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

#[0]*10
## distinguishing between random and missiles
# Works 4/12
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w                            1 w
# w                     4      1 w
# w                              w
# w   4                          w
# w                         3 3  w
# w         s    s A             w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

#[0]*10
# This doesn't test for anything new; it just has all the objects thrown in
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w        4                   1 w
# w              k             1 w
# w      4           A           w
# w                              w
# w          k              3 3  w
# w                       s  s   w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """


#[0]*10
#randomnpc inference, just more sprites
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                              w
# w    4                       1 w
# w         4           4      1 w
# w                              w
# w   4         4                w
# w                         3 3  w
# w                A             w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w m w                          w
# wwwww                          w
# w                              w
# w                              w
# w                          wwwww
# w        2  2   1 1    m   w 3 w
# w     A                    w 3 w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwww
# w         3 3   w
# w   p           w
# w               w
# w A p           w
# wwwwwwwwwwwwwwwww
# """

# level1 = """
# wwwwwwwwwwwwwwwww
# w         3 3   w
# w   p           w
# w               w
# w A p           w
# wwwwwwwwwwwwwwwww
# """

game="""
BasicGame
    SpriteSet
        avatar  > MovingAvatar color=DARKBLUE #stype=sam
        cloner > Immovable color=GREEN
        box    > Immovable color=WHITE # orientation=RIGHT cooldown=1
        box2 > Immovable color=GREEN
        box3 > Immovable color=YELLOW
        box5 > Immovable color=LIGHTBLUE
        flicker > Flicker timeout=1 color=ORANGE
        random > RandomNPC color=PURPLE speed=1 cooldown=1
        chaser > Chaser color=BLACK speed=1 cooldown=4 stype=avatar fleeing=True
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=2
        missile > Missile
            sam  > orientation=UP color=BLUE singleton=False cooldown=1
        wall > Immovable color=DARKGRAY
        medicine > Resource limit=2 color=LIGHTGREEN
        poison > Resource limit=3 color=PINK
        invisiblemedicine > Resource limit=4 color=PURPLE
    LevelMapping
        C > cloner
        F > flicker
        0 > base
        1 > box
        2 > box2
        3 > box3
        4 > random
        5 > box5
        w > wall
        c > cannon
        s > sam
        k > chaser
        A > avatar
        m > medicine
        p > poison
    InteractionSet
        ## TEST1
        # box avatar > transformTo stype=box2
        # box2 avatar > nothing

        ## TEST2
        # box2 avatar > bounceForward
        # box box2 > killSprite

        ## TEST3
        # box2 avatar > bounceForward
        # box avatar > killSprite
        # avatar box > stepBack

        ## TEST4
        # box2 avatar > bounceForward
        # avatar box > killSprite

        ## TEST5
        avatar sam > bounceForward

        ## TEST6
        sam wall > reverseDirection

        ## TEST7
        # box2 avatar > bounceForward

        # box avatar > nothing
        # box avatar >killSprite
        
        box3 avatar > killSprite
        avatar box5 > killSprite
        cannon avatar > bounceForward
        
        # avatar sam > stepBack
        # avatar sam > killSprite
        # cannon sam > stepBack
        
        sam cannon > stepBack
        # sam wall > killSprite
        # sam EOS > wrapAround
        medicine avatar > killSprite
        # avatar medicine > changeResource resource=invisiblemedicine value=1
        # avatar poison > changeResource resource=invisiblemedicine value=-1
        # poison avatar > killIfOtherHasMore resource=invisiblemedicine limit=0
        avatar wall > stepBack

        avatar medicine > changeResource resource=medicine value=1
        avatar poison > changeResource resource=medicine value=-1
        # poison avatar >killIfHasLess resource=medicine limit=-1
        avatar poison > killIfHasLess resource=medicine limit=-1
        poison avatar > killSprite

    TerminationSet
        SpriteCounter stype=box3 limit=0 win=True
        SpriteCounter stype=avatar limit=0 win=False


"""
level_game_pairs = [[game, level]]#, [game, level1]]


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    # parse, run and play.
    VGDLParser.playGame(game, level)
