'''
VGDL example: a simplified Zelda variant: Link has a sword, needs to get a key and open the door.

@author: Tom Schaul
'''

zelda_level = """
wwwwwwwwwwwww
wA       w  w
w  w        w
w   w   w +ww
www w1  wwwww
w       w G w
w 1        ww
w     1    ww
wwwwwwwwwwwww
"""

        
zelda_game = """
BasicGame
  SpriteSet         
    goal  > Immovable color=GREEN
    key   > Resource color=ORANGE limit=1
    sword > Flicker limit=5 singleton=True
    movable > 
      avatar  > ShootAvatar   stype=sword
    monster > Immovable color=PURPLE
  LevelMapping
    G > goal
    + > key        
    A > avatar
    1 > monster            
  InteractionSet
    movable wall  > stepBack
    goal avatar  > killSprite        
    monster sword > killSprite        
    avatar monster> killSprite
    key avatar    > collectResource scoreChange=1
    key avatar    > killSprite
  TerminationSet
    SpriteCounter stype=goal   win=True
    SpriteCounter stype=avatar win=False
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(zelda_game, zelda_level)    
