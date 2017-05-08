

# level = """
# wwwwwwwwwwwwwwww
# w  A           w
# w   w       x  w
# w   w          w
# w   w          w
# w   w x        w
# w   w          w
# w   w          w
# w        g     w
# wwwwwwwwwwwwwwww

# """

level = """
wwwwwwwwwwwwww
w    A       w
w          x w
w            w
w            w
w    x       w
w            w
w            w
w    g       w
wwwwwwwwwwwwww
"""

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                 w                 w
# w              a  w         w       w
# w   a        x    w         w       w
# w                           w   x   w
# w       A                   w       w
# w                           w       w
# w               a           w     g w
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """
     
# level = """
# wwwwwwwwwwwwwwwwwww
# w                 w
# w         w       w
# w         w       w
# w         w       w
# w         w       w
# w         w       w
# w         w       w
# w         wwwwwwwww
# w      A          w
# w                 w
# w    w     x      w
# w    w            w
# w    w            g
# wwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                 w                 w
# w                 w         w       w
# w                 w         w       w
# w                 w         w       w
# w                 w         w       w
# w                 w         w       w
# w                 w         w       w
# w                 w         wwwwwwwww
# w wwwwww          w      A          w
# w      w          w                 w
# w      w          w    w     x      w
# w      w          w    w            w
# w      w          w    w            g
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# w                 w                 w
# w              a  w         w       w
# w   a             w         w       w
# w                     A     w   x   w
# w                           w       w
# w                           w       w
# w               a           w       w
# w                           wwwwwwwww
# w wwwwww                            w
# w      w         2       x       a  w
# w      w               w            w
# w      w               w            w
# w      w               w            g
# wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
# """
        
game = """
BasicGame frame_rate=30
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE
        box > Passive
            box1 > color=ORANGE
            box2 > color=LIGHTGREEN
        mover > VGDLSprite
            rand > RandomNPC cooldown=5
                rand1 > color=LIGHTORANGE
                rand2 > color=BROWN
        chaser > Chaser color=BLUE stype=avatar cooldown=5
        wall > Immovable color=BLACK
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
        missile EOS > wrapAround
        missile avatar > killSprite
        missile missile > reverseDirection
        mover mover > stepBack
        mover missile > stepBack
        mover box > stepBack
        goal avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False          
        SpriteCounter stype=goal limit=0 win=True
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random
    levels = [l for l in locals().keys() if 'level' in l]
    index = random.choice(range(len(levels)))
    VGDLParser.playGame(game, locals()[levels[index]])   