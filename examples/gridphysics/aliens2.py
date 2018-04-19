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
1.............................
000...........................
000...........................
..............................
..............................
..............................
..............................
....000......000000.....000...
...00000....00000000...00000..
...0...0....00....00...00000..
................A.............
"""


game = """
    BasicGame
        SpriteSet
            background > Immovable img=oryx/space1 hidden=True
            base    > Immovable    color=WHITE img=oryx/planet
            avatar  > FlakAvatar   stype=sam img=oryx/spaceship1
            missile > Missile
                sam  > orientation=UP    color=BLUE singleton=True img=oryx/bullet1
                bomb > orientation=DOWN  color=RED  speed=0.5 img=oryx/bullet2
            alien   > Bomber       stype=bomb   prob=0.01  cooldown=3 speed=0.8
                alienGreen > img=oryx/alien3
                alienBlue > img=oryx/alien1
            portal  > invisible=True hidden=True
                portalSlow  > SpawnPoint   stype=alienBlue  cooldown=16   total=20 img=portal
                portalFast  > SpawnPoint   stype=alienGreen  cooldown=12   total=20 img=portal

        LevelMapping
            . > background
            0 > background base
            1 > background portalSlow
            2 > background portalFast
            A > background avatar

        TerminationSet
            SpriteCounter      stype=avatar               limit=0 win=False
            MultiSpriteCounter stype1=portal stype2=alien limit=0 win=True

        InteractionSet
            avatar  EOS  > stepBack
            alien   EOS  > turnAround
            missile EOS  > killSprite

            base bomb > killSprite
            bomb base > killSprite
            
            base sam > killSprite
            sam base > killSprite
            
            # base sam > killBoth scoreChange=1

            base   alien > killSprite
            avatar alien > killSprite scoreChange=-1
            avatar bomb  > killSprite scoreChange=-1
            alien  sam   > killSprite scoreChange=2
"""

level_game_pairs = [[game, level]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    