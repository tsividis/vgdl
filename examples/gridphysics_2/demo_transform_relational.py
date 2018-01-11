level = """
wwwwwwwwwwww
w A        w
w   x      w
w        z w
wwwwwwwwwwww
"""



# level = """
# wwwwwwwwwwww
# w A        w
# w      a   w
# w   x      w
# w a      z w
# w  x       w
# w      z   w
# w          w
# w          w
# wwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w                        w
# w    a                   w
# w     a          a       w
# w            z x         w
# w                  z     w
# w   x   Az           z   w
# w              a         w
# w                        w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# """
        
game = """
BasicGame frame_rate=30
    SpriteSet
        probe > Immovable color=BLUE
        converter > Immovable 
            converter1 > color=RED
            converter2 > color=PURPLE
        box > Immovable
            box_a >
                box1 > color=ORANGE
                box2 > color=ORANGE
                box3 > color=LIGHTGREEN
            box_b >        
                box4 > color=LIGHTBLUE
                box5 > color=PINK
                box6 > color=YELLOW       
        goal > Immovable color=BLACK  
        avatar > MovingAvatar color=WHITE
        wall > Immovable color=BLACK
    LevelMapping
        w > wall   
        a > box1
        b > box2
        c > box3
        d > box4
        e > box5
        f > box6
        x > probe
        z > converter1
        y > converter2
        g > goal
    InteractionSet
        avatar wall > stepBack
        avatar box6 > undoAll 
        box avatar > bounceForward
        box probe > undoAll
        box box > undoAll
        box wall > stepBack
        probe probe > stepBack
        probe wall > stepBack
        probe converter > stepBack
        converter box > bounceForward
        probe avatar > bounceForward
        probe box6 > killSprite
        converter avatar > transformTo stype=box6
        avatar converter > undoAll
        goal avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False          
        SpriteCounter stype=probe limit=0 win=True
"""
"""


"""
if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random
    levels = [l for l in locals().keys() if 'level' in l]
    index = random.choice(range(len(levels)))
    VGDLParser.playGame(game, locals()[levels[index]])     