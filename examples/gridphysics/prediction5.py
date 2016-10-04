'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

box_level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w      w          w                 w
w      w       c  w         w       w
w   a  w          w         w  y    w
w      w                    w       w
w      w          w         w       w
w      w          w         w       w
w                 w     z   w       w
w      wwww wwwwwwwwwwwwwww wwwwwwwww
w wwwwww               w            w
w      w         2     w            w
w   A  w               w      1     w
w      w               w            w
w      w               w            g
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""
        
push_game = """
BasicGame frame_rate=30
    SpriteSet
        box > Passive
            box1 > color=RED
            box2 > color=LIGHTBLUE
            box3 > color=LIGHTGREEN
        mover > VGDLSprite
            chaser > Chaser stype=avatar color=PINK cooldown=10
            rand > RandomNPC cooldown=10
                rand1 > color=LIGHTORANGE
                rand2 > color=BLUE
        wall > ResourcePack color=BLACK  
        missile > Missile
            missile1 > color=YELLOW speed=0.2 orientation=UP
            missile2 > color=GRAY   speed=0.2 orientation=UP
            missile3 > color=PINK   speed=0.2 orientation=RIGHT
            missile4 > color=GREEN  speed=0.1 orientation=RIGHT      
        goal > Immovable color=BLACK
    LevelMapping
        w > wall   
        a > box1
        b > box2
        c > box3
        x > chaser
        y > rand1
        z > rand2
        1 > missile1
        2 >missile3
        g > goal
    InteractionSet
        avatar wall > stepBack 
        mover wall > stepBack
        box avatar > killSprite  
        missile wall > reverseDirection
        missile avatar > killSprite
        missile missile > reverseDirection
        mover avatar > undoAll
        mover mover > stepBack
        mover missile > stepBack
        mover box > stepBack
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