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
w0000====0000000000====00012
w00===000===000====0000===02
www   ww   www    www  wwwww
w-     xxx       xxx   xx  w
w -   ---     -   --   --  w
w       A                  w
wwwwwwwwwwwwwwwwwwwwwwwwwwww
"""


game = """
BasicGame
    SpriteSet
        forest > SpawnPoint stype=log prob=0.4  cooldown=10 color=BLACK
        structure > Immovable
            water > color=BLUE
            goal  > color=GREEN
        log    > Missile   orientation=LEFT  speed=0.5 color=BROWN
        safety > Resource  limit=4 color=BROWN
        truck  > Missile   orientation=RIGHT 
            slowtruck  > speed=.5 color=RED
            fasttruck  > speed=.5  color=ORANGE
        # defining 'wall' last, makes the walls show on top of all other sprites
        wall > Immovable color=BLACK   
        avatar > MovingAvatar color=DARKBLUE        
    InteractionSet
        goal avatar  > killSprite
        avatar log   > changeResource resource=safety value=1
        avatar log   > pullWithIt   # note how one collision can have multiple effects
        avatar wall  > stepBack
        forest water > nothing
        forest wall > nothing
        log wall > nothing
        fasttruck wall > nothing
        slowtruck wall > nothing
        fasttruck fasttruck > nothing
        slowtruck slowtruck > nothing
        water log > nothing
        log forest > nothing
        truck truck > nothing
        log log > nothing
        truck wall > nothing
        forest avatar > nothing
        avatar water > killIfHasLess  resource=safety limit=-1
        avatar water > changeResource resource=safety value=-1
        avatar truck > killSprite
        log    EOS   > killSprite
        truck  EOS   > wrapAround
    
    TerminationSet
        SpriteCounter stype=goal   limit=0 win=True
        SpriteCounter stype=avatar limit=0 win=False
    
    LevelMapping
        G > goal
        0 > water
        1 > forest water       # note how a single character can spawn multiple sprites
        2 > forest wall log
        - > slowtruck
        x > fasttruck
        = > log water
"""

level_game_pairs = [[game, level]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    