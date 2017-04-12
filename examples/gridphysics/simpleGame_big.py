'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

# level = """
# wwww
# wp w
# wAgw
# wwww
# """

# TODO: make it twice as big, 4 times as big, 8 times as big.
# TODO: add more poison sprites.
# TODOL add more boxes (larger state space)
# TODO: add medicine -> ceheck if planner can figure out that this helps with poison.

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwww
# w                        ww
# w     p                 1 w
# w    pAp               1  w
# w    p mp             1 1 w
# w     ppp              wgww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# wwwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwww
# w                    1   ww
# w     p1                w w
# w    p p              Awgww
# w    p mp              w ww
# w     ppp         1    w ww
# w         1            w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                        ww
# wwwwwwwwwwwwwwwwwwwwwwwwwww
# """

level = """
wwwwwwwwwwwwwwwwwwwwwwwwwww
w                    1   ww
w     p1                1 w
w    p p               wgww
w    pAmp              w ww
w     ppp         1    w ww
w         1            w ww
w                      w ww
w                      w ww
w                      w ww
w                      w ww
w                      w ww
w                      w ww
w                      w ww
w                      w ww
w                      w ww
w                      w ww
wwwwwwwwwwwwwwwwwwwwwwwwwww
"""


# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwwww
# w                    1   ww
# w     p1                w w
# w    p p               wgww
# w    pAmp              w ww
# w     ppp         1    w ww
# w         1            w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                      w ww
# w                        ww
# wwwwwwwwwwwwwwwwwwwwwwwwwww
# """

game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > Passive color=GOLD
        poison > Resource limit=3 color=BROWN
        box  > ResourcePack color=ORANGE
        wall > Immovable color=BLACK      
        score > Resource color=PINK limit=10 
        medicine > Resource limit=3 color=WHITE        
    LevelMapping
        p > poison
        1 > box
        w > wall   
        g > goal 
        h > hole
        m > medicine
    InteractionSet
        avatar wall > stepBack
        avatar medicine > changeResource resource=medicine value=1
        medicine avatar > killSprite  
        poison avatar > killSprite
        avatar poison > changeResource resource=medicine value=-1
        avatar poison > killIfHasLess resource=medicine limit=-1
        goal avatar > killSprite
        box avatar  > bounceForward
        goal box > bounceForward
        goal wall > undoAll
        box wall    > undoAll
        box box     > bounceForward
        box poison > undoAll
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    