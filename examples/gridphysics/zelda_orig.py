'''
VGDL example: a simplified Zelda variant: Link has a sword, needs to get a key and open the door.

@author: Tom Schaul
'''

level = """
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

        
game = """
BasicGame
  SpriteSet         
    goal  > Immovable color=GREEN
    key   > Immovable color=ORANGE
    sword > Flicker limit=5 singleton=True
    movable > 
      avatar  > ShootAvatar  stype=sword 
        nokey   > color=PINK
        withkey > color=RED
      monster > RandomNPC color=PURPLE cooldown=4 
  LevelMapping
    G > goal
    + > key        
    A > nokey
    1 > monster            
  InteractionSet
    movable wall  > stepBack
    nokey goal    > stepBack
    goal withkey  > killSprite 
    monster sword > changeScore value=1       
    monster sword > killSprite        
    nokey monster> killSprite
    withkey monster> killSprite
    key  nokey   > killSprite
    nokey key     > transformTo stype=withkey                
  TerminationSet
    SpriteCounter stype=goal   win=True
    # SpriteCounter stype=avatar win=False
    MultiSpriteCounter stype1=nokey stype2=withkey limit=0 win=False

"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    