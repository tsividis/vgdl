'''
VGDL example: a simple teleport-and-avoid-fire game. 

@author: Tom Schaul
'''





portal_level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w A                                 w
w                o                  w
w                                   w
w                                   w
w                                   w
w   2                      2   2    w
w     i                      p      w
w   1                      1   1    w
w                                   w
w                                   w
w                                   w
w                3                  w
w                                   g
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

"""
wwwwwwwwwwwwwwwwwwwwwwwww
w                       w
w   A            2      w
w            3      2   w
w   2                   w
w                 p     w
w     i                 w
w              1        w
w   1              1    w
w          o            w
w                       g
wwwwwwwwwwwwwwwwwwwwwwwww
"""

portal_game = """
BasicGame
    SpriteSet
        structure > Immovable            
            portalentry > Portal 
                entry1 > stype=exit1 color=GRAY 
            portalexit  > color=BROWN
                exit1  > 
        box > Immovable
            box_a > color=BLUE
            box_b > 
                box_b1 >color=RED
                box_b2 >color=PURPLE
        probe > Immovable color=YELLOW
        goal > Immovable color=BLACK
        avatar > MovingAvatar color=WHITE
    InteractionSet
        goal   avatar    > killSprite
        avatar wall      > stepBack
        box avatar > bounceForward
        avatar portalentry > teleportToExit
        box_a portalentry > teleportToExit
        box_b portalentry > undoAll
        box_a probe > killSprite
        probe box_b > bounceForward
        box box > undoAll
        box wall > undoAll
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
        SpriteCounter stype=goal limit=0 win=True

    LevelMapping
        1 > box_a
        2 > box_b1
        3 > box_b2
        i > entry1
        o > exit1
        p > probe  
        g > goal      
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(portal_game, portal_level)    