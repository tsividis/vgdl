'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

level = """
wwwwwwwwwwwwwwwwwwww
w  A               w
w               1  w
w                  w
w        2         w
w                  w
w   a              w
w                  g
wwwwwwwwwwwwwwwwwwww
"""
        
game = """
BasicGame frame_rate=30
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE
        box > Passive
            box1 > color=RED
            box2 > color=LIGHTGREEN
        mover > VGDLSprite
            rand > RandomNPC cooldown=10
                rand1 > color=LIGHTORANGE
                rand2 > color=BLUE
        chaser > AStarChaser color=BROWN stype=avatar
        wall > ResourcePack color=BLACK  
        missile > Missile
            missile1 > color=YELLOW orientation=RIGHT
            missile2 > color=PINK orientation=RIGHT
        goal > Immovable color=GREEN
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
        avatar rand > killSprite
        rand wall > stepBack  
        chaser wall > stepBack
        avatar chaser > killSprite
        missile wall > turn
        avatar missile > killSprite
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
    VGDLParser.playGame(game, level)    