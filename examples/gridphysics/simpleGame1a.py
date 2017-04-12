'''
Simple interactions: get/lose points, can't pass through c11s, object gets pushed.
'''

box_level = """
wwwwwwwwwwwww
w  2 m   w  w
w   1       w
w t A 1 p  gw
www     wwwww
w c  m  w   w
w 1  t     3w
w  2 c  p  ww
wwwwwwwwwwwww
"""

        
push_game = """
BasicGame frame_rate=30
    SpriteSet        
        c2   > Immovable color=LIGHTBLUE
        c5 > MovingAvatar color=DARKBLUE #cooldown=4 
        box    > Passive 
            c3 > Passive color=ORANGE               
            c4 > Passive color=PINK
        c6 > ResourcePack color=GREEN limit=5
        c1 > Passive color=GOLD
        c7 > ResourcePack color=RED limit=5
        c8 > Passive color=BLUE
        c9 > Resource limit=3 color=WHITE
        c10 > Resource limit=3 color=BROWN
        c11 > Immovable color=BLACK               
    LevelMapping
        0 > c2
        1 > c3
        2 > c4  
        3 > c6 
        t > c7    
        c > c8 
        m > c9
        p > c10
        w > c11   
        g > c1 
    InteractionSet
        c5 c11 > stepBack  
        c6 c5 > collectResource scoreChange=5
        c6 c5 > killSprite
        c7 c5 > collectResource scoreChange=-5
        c7 c5 > killSprite
        c8 c5 > killSprite
        c5 c9 > changeResource resource=c9 value=1
        c9 c5 > killSprite
        c5 c10 > changeResource resource=c9 value=-1
        c10 c5 > killSprite
        c5 c10 > killIfHasLess resource=c9 limit=-1
        box c5  > bounceForward
        box c11    > undoAll        
        box box     > undoAll
        box c2    > killSprite
        box c6 > undoAll
        box c10 > undoAll
        box c9 > undoAll
        c1 c5 > killSprite  
    TerminationSet
        SpriteCounter stype=box     limit=0 win=True
        SpriteCounter stype=c1    limit=0 win=True
        SpriteCounter stype=c5  limit=0 win=False          
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(push_game, box_level)    