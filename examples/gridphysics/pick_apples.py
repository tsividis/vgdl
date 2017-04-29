
# level = """
# wwwwwwwwww
# wx  A   xw
# wwwwwwwwww
# """


# level = """
# wwwwwwwwwwwwww
# w    x       w
# w   xAx      w
# w            w
# wwwwwwwwwwwwww
# """

level = """
wwwwwwwwwwwwwwww
w A            w
w           x  w
w              w
w  x   w       w
w              w
w              w
w       x      w
wwwwwwwwwwwwwwww
"""


# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwww
# wA                       w
# w    a    x              w
# w     a          a       w
# w            z           w
# w                  z     w
# w   x    z           z   w
# w              a  x      w
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
        goal2 > Immovable color=ORANGE  
        avatar > MovingAvatar color=WHITE
        wall > Immovable
    LevelMapping
        w > wall   
        a > box1
        b > box2
        c > box3
        d > box4
        e > box5
        x > probe
        z > converter1
        y > converter2
        g > goal2
    InteractionSet
        avatar wall > stepBack
        box avatar > bounceForward
        box probe > undoAll
        box box > undoAll
        box wall > undoAll
        probe wall > undoAll
        converter wall > undoAll
        probe converter > undoAll
        probe probe > undoAll
        converter box > bounceForward
        #avatar probe > changeScore value=.5
        probe avatar > killSprite
        avatar converter > undoAll
        goal2 avatar > killSprite
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