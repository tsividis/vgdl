'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

box_level = """
wwwwwwwwwwwwwwwwwwwwwwwww
w 1                     w
w     c                 w
w   A            a      w
w  3                    w
w      2                w
w             b         w
w                  4    w
w          1            w
w                       g
wwwwwwwwwwwwwwwwwwwwwwwww
"""

        
push_game = """
BasicGame frame_rate=30
    SpriteSet        
        box > Passive
            box1 > color=RED
            box2 > color=LIGHTBLUE
            box3 > color=PURPLE
        wall > ResourcePack color=BLACK  
        missile > Missile orientation=RIGHT
            missile1 > color=YELLOW speed=0.2
            missile2 > color=GREEN   speed=0.2
            missile3 > color=PINK   speed=0.1       
            missile4 > color=ORANGE  speed=0.1
        goal > Immovable color=BLACK
        avatar > MovingAvatar color=WHITE
    LevelMapping
        w > wall   
        a > box1
        b > box2
        c > box3
        1 > missile1
        2 > missile2
        3 > missile3
        4 > missile4
        g > goal
        A > avatar
    InteractionSet
        avatar wall > stepBack  
        box avatar > killSprite  
        missile wall > reverseDirection
        missile avatar > killSprite 
        goal avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False          
        SpriteCounter stype=goal limit=0 win=True
"""
"""
show agent killing a moving item.
same prediction should be highest for other moving items of same speed, then for non-moving items.
also vice-versa.
"""
if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(push_game, box_level)    