
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
w              w
w A            w
w     y     x  w
w              w
w  x   w       w
w         y    w
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
        apple > Immovable color=GREEN
        orange > Immovable color=ORANGE
        box > Immovable color=LIGHTGREEN
        goal2 > Immovable color=ORANGE  
        avatar > MovingAvatar color=WHITE
        wall > Immovable color=BLACK
    LevelMapping
        w > wall   
        a > box1
        b > box2
        c > box3
        d > box4
        e > box5
        x > apple
        y > orange
        g > goal2
    InteractionSet
        avatar wall > stepBack
        box avatar > bounceForward
        box apple > undoAll
        box box > undoAll
        box wall > undoAll
        apple wall > undoAll
        orange wall > undoAll
        apple orange > undoAll
        apple apple > undoAll
        orange box > bounceForward
        #avatar apple > changeScore value=.5
        avatar orange > killSprite
        apple avatar > killSprite
        goal2 avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False          
        SpriteCounter stype=apple limit=0 win=True
"""
"""


"""
if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random
    levels = [l for l in locals().keys() if 'level' in l]
    index = random.choice(range(len(levels)))
    VGDLParser.playGame(game, locals()[levels[index]])     