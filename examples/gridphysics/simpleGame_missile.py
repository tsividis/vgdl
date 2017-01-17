'''
<<<<<<< HEAD
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

# box_level = """
# wwww
# wp w
# wAgw
# wwww
# """

box_level = """
wwwwwwwww
wA      w
w2 2    w
w       w
w      gw
wwwwwwwww
""" 

# box_level = """
# wwwwwwwww
# w       w
# w2 2    w
# w       w
# w  A w gw
# wwwwwwwww
# """

# box_level = """
# wwwwwwwwww
# w2    A  w
# w      p w
# w2       w
# w        w
# w      www
# w     1g w
# w      www
# wwwwwwwwww
# """ # with no problem of aliens killing gold sprite.

push_game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > Passive color=GOLD
        poison > Resource limit=3 color=BROWN
        box  > ResourcePack color=ORANGE
        wall > Immovable color=BLACK     
        missile > Missile
            bomb > orientation=DOWN  color=RED  speed=0.5 
        alien   > Bomber       stype=bomb   prob=0  cooldown=3 speed=0.5
        score > Resource color=PINK limit=10         
    LevelMapping
        p > poison
        1 > box
        w > wall   
        g > goal 
        h > hole
        2 > alien
    InteractionSet
        avatar wall > stepBack  
        poison avatar > killSprite
        avatar poison > killSprite
        goal avatar > killSprite
        box avatar  > bounceForward
        goal box > bounceForward
        goal wall > undoAll
        goal poison > undoAll
        box wall    > undoAll    
        box treasure > undoAll
        box poison > undoAll
        alien   EOS  > turnAround
        avatar alien > killSprite
        avatar bomb  > killSprite
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False      
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser

