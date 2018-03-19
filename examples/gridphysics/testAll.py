
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                  g    x      w
# w  x     x              x     gw
# w             x         x   e  w
# wxxxxxxxxxx    p        xxxxxxxw
# w      mm x   pgp  x           w
# w      mm x  x p         x     w
# w    x         A a c         t w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

simplifiedLevel = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                  g    x      w
w  x     x              x     gw
w             x         x   e  w
wxxxxxxxxxx    p   x    xxxxxxxw
w      mm x t pgp              w
w      mm x  x p         x     w
w    x    mm a A               w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

spriteLimitReachedLevel = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                  g    x      w
w  x     x              x     gw
w             x         x   e  w
wxxxxxxxxxx    p   x    xxxxxxxw
w      mm x   pgp              w
w      mm x  x p         x     w
w    x         A a c         t w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level = simplifiedLevel

game="""
BasicGame
    SpriteSet
        box    > Passive color=BROWN # orientation=RIGHT cooldown=1
        flicker > Flicker timeout=1 color=YELLOW

        chaser > Chaser color=BLACK speed=1 cooldown=1 stype=box
        avatar  > MovingAvatar color=DARKBLUE #stype=sam
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=4 #16
        missile > Missile
            sam  > orientation=UP color=BLUE cooldown=1 #4
        wall > Immovable color=DARKGRAY
        medicine > Resource limit=4 color=WHITE
        invisiblemedicine > Resource limit=4 color=PURPLE
        poison > Resource limit=3 color=PINK
        goal > Passive color=GOLD
        armor > Resource limit=1 color=GRAY
        portal > Portal color=LIGHTGREEN stype=exit1
        exit1 > Immovable color=GREEN

    LevelMapping
        f > flicker
        0 > base
        x > box
        r > random
        w > wall
        c > cannon
        s > sam
        A > avatar
        h > chaser
        m > medicine
        p > poison
        g > goal
        a > armor
        t > portal
        e > exit1
{}
    TerminationSet
        # SpriteCounter stype=box2 limit=0 win=True
        # SpriteCounter stype=box3 limit=0 win=False
        SpriteCounter stype=goal limit=0 win=True
        # Termination
"""

interactionSetAll = """
    InteractionSet
        cannon wall > stepBack
        sam wall > killSprite
        box avatar > killSprite
        cannon avatar > bounceForward
        box sam > killSprite
        avatar sam > bounceForward
        avatar wall > stepBack
        avatar armor > changeResource resource=armor value=1
        medicine avatar > collectResource
        avatar poison > changeResource resource=medicine value=-1
        poison avatar > killIfOtherHasMore resource=medicine limit=0
        sam sam > killSprite
        sam goal > flipDirection
        goal avatar > killSprite
        avatar goal > changeScore value=1
        avatar portal > teleportToExit

        sam medicine > transformTo stype=poison
        sam poison > transformTo stype=medicine
        sam exit1 > undoAll

        # avatar sam > killIfHasLess resource=armor limit=1

"""

game = game.format(interactionSetAll)

level_game_pairs = [[game, level]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    # parse, run and play.
    VGDLParser.playGame(game, level)

''' all working gridphysics interactions
['killSprite', 'transformTo',\
'killIfHasLess', 'killIfHasMore', 'killIfOtherHasLess', 'killIfOtherHasMore',\
'undoAll', 'nothing',\
'turn', 'turnAround', 'reverseDirection', 'flipDirection', 'bounceForward',\
'changeResource', 'collectResource', 'changeScore', 'teleportToExit', ],
'''
