'''
VGDL example: a simplified variant of the classic frogger game.

Logs spawn randomly, but trucks wrap around the screen and come back. 

@author: Tom Schaul
'''

frog_level = """

wwwwwwwwwwwwwwwwwwwwwwwwwwww
w           wGw            w
w00==000000===0000=====000=2
w0000====0000000000====00012
w00===000===000====0000===02
www   ww   www    www  wwwww
w   ----   ---   -  ----   w
w-     xxx       xxx    xx w
w -   ---     -   ---- --  w
w       A                  w
wwwwwwwwwwwwwwwwwwwwwwwwwwww

"""

"""
'RED'       > Missile   orientation=RIGHT speed=0.2
'ORANGE'    > Missile   orientation=RIGHT speed=0.2
'BROWN'     > Missile   orientation=LEFT  speed=0.1
"""

frog_game = """
BasicGame
    SpriteSet


    InteractionSet


    TerminationSet

    
    LevelMapping
        G > 'GREEN'
        0 > 'BLUE'
        1 > 'BLUE'
        2 > 'BROWN'
        - > 'RED'
        x > 'ORANGE'
        = > ''BLUE
        A > 'WHITE'

"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(frog_game, frog_level)    