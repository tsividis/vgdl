'''
VGDL example: a simplified Sokoban variant: push the boxes into the holes.

@author: Tom Schaul
'''

# level = """
# wwwwwwwwwwwww
# w01  A  1 0ww
# wwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwww
# w       w   w
# w 1  A  1  ww
# w 0        ww
# wwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwww
# w    A 1   ww
# w 0 1    w0ww
# wwwwwwwwwwwww
# """

# level = """
# wwwwwwwwww
# w A   w0ww
# w01 1   ww
# wwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwww
# wA       w  ww
# w   1       ww
# w       w 0www
# www w   wwwwww
# w       w 0 ww
# w 1        www
# w          www
# wwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwww
# wA       w  ww
# w   1       ww
# w     1 w 0www
# www w1  wwwwww
# w       w 0 ww
# w 1        www
# w          www
# wwwwwwwwwwwwww
# """


level = """
wwwwwwwww
ww   w  w
wA      w
w  1w 0ww
w   wwwww
w 1 w 0 w
w      ww
ww     ww
wwwwwwwww
"""

# level = """
# wwwwwww
# wwww ww
# w01 1 w
# www A w
# wwwwwww
# """
        
game = """
BasicGame frame_rate=30
    SpriteSet        
        hole   > Immovable color=PINK
        avatar > MovingAvatar color=DARKBLUE
        box    > Passive  color=LIGHTBLUE              
    LevelMapping
        0 > hole
        1 > box            
    InteractionSet
        avatar wall > stepBack        
        box avatar  > bounceForward
        box wall    > undoAll        
        box box     > undoAll
        box hole    > killSprite        
    TerminationSet
        SpriteCounter stype=box    limit=0 win=True 
"""
#Timeout limit=5000 win=False         

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    