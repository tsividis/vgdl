'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

box_level = """
wwwwwwwwwwwww
w m      w  w
w2  1  3    w
w   A 1    gw
wwwn    wwwww
w c     w   w
w 1 2    4  w
w    c 3   ww
wwwwwwwwwwwww
"""

        
push_game = """
BasicGame frame_rate=30
    SpriteSet        
        breakbox   > ResourcePack 
            breakbox1 > color=LIGHTBLUE
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        box    > ResourcePack 
            box1 > color=ORANGE               
            box2 > color=PINK
            box3 > color=RED
        goal > ResourcePack color=GOLD
        cloud > ResourcePack color=BLUE
        wall > ResourcePack color=BLACK  
        missile > Missile orientation=RIGHT speed=0.2
            missile1 > color=YELLOW
            missile2 > color=GRAY             
    LevelMapping
        0 > breakbox
        1 > box1
        2 > box2  
        3 > breakbox1
        4 > box3
        c > cloud 
        w > wall   
        g > goal 
        m > missile1
        n > missile2
    InteractionSet
        avatar wall > stepBack  
        breakbox avatar > killSprite
        cloud avatar > killSprite
        cloud box > killSprite
        box avatar  > bounceForward
        box wall    > undoAll        
        box box     > undoAll
        box breakbox    > killSprite
        goal avatar > killSprite  
        missile wall > reverseDirection
        missile avatar > killSprite 
        box missile > killSprite
    TerminationSet
        SpriteCounter stype=box     limit=0 win=True
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(push_game, box_level)    