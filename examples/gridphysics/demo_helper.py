
# level = """
# wwwwwwww
# w b    w
# wab   xw
# w bbbA w
# wwwwwwww
# """

level = """
wwwwwwwwwwwwww
w    bbb     w
w a  b       w
w    b   x   w
w    bbbA    w
wwwwwwwwwwwwww
"""

# level = """
# wwwwwwwwwwwwww
# w    bbb     w
# w a  bbb     w
# w    bbb     w
# w    bbb     w
# w    bbb   x w
# w    bbb   A w
# wwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwww
# w                 b    w
# w              b  b  a w
# w   a             bbbbbw
# w       w   a      x   w
# w   A                  w
# wwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwww
# w                 b    w
# w              b  b A  w
# w   a             wwwwww
# w       w   a      x   w
# w                      w
# w                 bbbb w
# w              www  wwww
# wbbbbbbb     b         w
# w      b               w
# w  a   b        x      w
# w      b               w
# w      b   a           w
# wwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                 b    b            w
# w              b  b A  b  a    a    w
# w   a             wwwwww            w
# w           a                   x   w
# w                           b       w
# w                 bbbb      b       w
# w     x                     b       w
# w                      a    www  wwww
# wbbbbbbb     b                      w
# w      b                        a   w
# w  a   b              a             w
# w      b                            w
# w      b   a              b         w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """
        
game = """
BasicGame frame_rate=30
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE
        box > Passive
            box1 > color=RED
            box2 > color=ORANGE
        mover > VGDLSprite
            rand > RandomNPC cooldown=5
                rand1 > color=LIGHTORANGE
                rand2 > color=BROWN
        chaser > Chaser color=BLUE stype=box1 cooldown=0
        wall > Immovable
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
        #box1 avatar > bounceForward
        box2 avatar > changeScore value=-1
        box2 avatar > killSprite
        avatar rand > killSprite
        rand wall > stepBack  
        chaser wall > stepBack
        box1 chaser > killSprite
        chaser box2 > stepBack
        missile EOS > wrapAround
        missile avatar > killSprite
        missile missile > reverseDirection
        mover mover > stepBack
        mover missile > stepBack
        mover box > stepBack
        goal avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False          
        SpriteCounter stype=box1 limit=0 win=True
"""
"""
show agent killing a moving item.
same prediction should be highest for other moving items of same speed, then for non-moving items.
also vice-versa.
"""
if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random
    levels = [l for l in locals().keys() if 'level' in l]
    index = random.choice(range(len(levels)))
    VGDLParser.playGame(game, locals()[levels[index]])   