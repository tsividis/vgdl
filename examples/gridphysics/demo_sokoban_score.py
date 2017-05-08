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
# wwwwwwww
# wwww www
# w01 1 ww
# www A ww
# wwwwwwww
# """
 

# level = """
# wwwwwwwwwwwwww
# w        w   w
# w     A  1  ww
# w 0    1   0ww
# wwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwww
# w A   w0ww
# w01 1   ww
# wwwwwwwwww
# """

level = """
wwwwwwwwwwwww
wA       w  w
w   1       w
w     1 w 0ww
www w1  wwwww
w       w 0 w
w 1        ww
w          ww
wwwwwwwwwwwww
"""

        
game = """
BasicGame frame_rate=30
    SpriteSet        
        hole   > Immovable color=PINK
        avatar > MovingAvatar color=DARKBLUE
        box    > Passive  color=RED              
    LevelMapping
        0 > hole
        1 > box            
    InteractionSet
        avatar wall > stepBack        
        box avatar  > bounceForward
        box wall    > undoAll        
        box box     > undoAll
        box hole > changeScore value=100
        box hole    > killSprite        
    TerminationSet
        SpriteCounter stype=box    limit=0 win=True 
"""
#Timeout limit=5000 win=False         

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    