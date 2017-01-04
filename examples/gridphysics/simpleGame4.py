'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

box_level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w      w          w                 w
w      w       b  w         w       w
w   a  w          w         w  y    w
w      w                    w       w
w      w          w         w       w
w      w          w         w       w
w                 wAz       w       w
w      wwww wwwwwwwwwwwwwww wwwwwwwww
w wwwwww               w            w
w      w         2     w            w
w      w               w      y     w
w      w               w            w
w      w               w            g
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""
        
push_game = """
BasicGame frame_rate=30
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        box > Passive
            box1 > color=ORANGE
            box2 > color=ORANGE
        mover > VGDLSprite
            rand > RandomNPC cooldown=10
                rand1 > color=PURPLE
                rand2 > color=PURPLE
        wall > ResourcePack color=BLACK  
        missile > Missile
            missile1 > color=PINK speed=0.05 orientation=UP
            missile2 > color=PINK   speed=0.05 orientation=RIGHT
        goal > Immovable color=GOLD
    LevelMapping
        w > wall   
        a > box1
        b > box2
        x > chaser
        y > rand1
        z > rand2
        1 > missile1
        2 > missile2
        g > goal
    InteractionSet
        avatar wall > stepBack 
        mover wall > stepBack
        box avatar > killSprite  
        missile wall > reverseDirection
        avatar missile > killSprite
        missile missile > reverseDirection
        avatar mover > killSprite
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