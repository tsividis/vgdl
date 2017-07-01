'''
VGDL example: a simplified variant of the classic frogger game.

Logs spawn randomly, but trucks wrap around the screen and come back.

@author: Tom Schaul
'''

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwww
# w         w  G  w          w
# w00==000000===0000=====000=2
# w0000====0000000000====00012
# w00===000===000====0000===02
# www   ww   www    www  wwwww
# w   ----   ---   -         w
# w-     xxx       xxx   xx  w
# w -   ---     -   --   --  w
# w       A                  w
# wwwwwwwwwwwwwwwwwwwwwwwwwwww
# """


# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwww
# w            G             w
# w0000====0000000000====00012
# www   ww   www    www  wwwww
# w-     xxx       xxx   xx  w
# w -   ---     -   --   --  w
# w       A                  w
# wwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwww
w         w  G  w          w
w0000====0000000000====000=w
w00===000===000====0000====w
www   ww   www    www  wwwww
w-     xxx       xxx   xx  w
w -   ---     -   --   --  w
w         A                w
wwwwwwwwwwwwwwwwwwwwwwwwwwww
"""


game = """
BasicGame
    SpriteSet
        water > Immovable color=BLUE
        goal  > Immovable color=GREEN
        log    > Missile   orientation=LEFT  speed=.5 color=BROWN
        safety > Resource  limit=4 color=BROWN
        slowtruck > Missile   orientation=RIGHT speed=.5 color=RED
        fasttruck > Missile   orientation=RIGHT speed=.5 color=ORANGE
        # defining 'wall' last, makes the walls show on top of all other sprites
        wall > Immovable color=BLACK
        avatar > MovingAvatar color=DARKBLUE
    InteractionSet
        goal avatar  > killSprite
        avatar log   > changeResource resource=safety value=1
        avatar log   > pullWithIt   # note how one collision can have multiple effects
        avatar wall  > stepBack
        log wall > nothing
        fasttruck wall > nothing
        slowtruck wall > nothing
        fasttruck fasttruck > nothing
        slowtruck slowtruck > nothing
        water log > nothing
        fasttruck slowtruck > nothing
        log log > nothing
        fasttruck wall > nothing
        slowtruck wall > nothing
        avatar water > killIfHasLess  resource=safety limit=-1
        avatar water > changeResource resource=safety value=-1
        avatar fasttruck > killSprite
        avatar slowtruck > killSprite
        log    EOS   > wrapAround
        slowtruck  EOS   > wrapAround
        fasttruck  EOS   > wrapAround

    TerminationSet
        SpriteCounter stype=goal   limit=0 win=True
        SpriteCounter stype=avatar limit=0 win=False

    LevelMapping
        G > goal
        0 > water
        - > slowtruck
        x > fasttruck
        = > log water
"""

level_game_pairs = [[game, level]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
