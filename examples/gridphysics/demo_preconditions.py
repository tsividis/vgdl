'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

# level = """
# wwwwwwwwwwwww
# w pmAmp  w  w
# w  pmp      w
# w  pppp  pp w
# w       p  gw
# wwwwwwwwwwwww
# """

# level2 = """
# wwwwwwwwwwwww
# w           w
# w  pmp      w
# w  pppppppp w
# w A     p  gw
# wwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwww
# wm           w
# w            w
# w       pppppw
# w     A p   gw
# wwwwwwwwwwwwww
# """
# level = """
# wwwww
# wmA g
# wwwww
# """

# level = """
# wwwwwwwwwwwwwwwwww
# w b c   w    m   w
# w   c   w    wwwww
# wcccc      p     w
# w     c p       ww
# ww   www A       w
# wpppp          c w
# w   pc           w
# w g p    c    c  w
# wwwwwwwwwwwwwwwwww
# """

level = """
wwwwwwwwwwwwwwwwww
w b p   w    m   w
w   p   w A  wwwww
wpppp      p     w
w     p p       ww
ww   www         w
wpppp          p w
w   pp           w
w g p    p    p  w
wwwwwwwwwwwwwwwwww
"""
# level = """
# wwwwwwwwwwwwwwwwww
# w b     w    m   w
# w       w A  wwwww
# w                w
# w               ww
# ww   www         w
# w                w
# w                w
# w g              w
# wwwwwwwwwwwwwwwwww
# """


        
game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4              
        goal > Passive color=GOLD
        cloud > Passive color=BLUE
        box > Passive color=ORANGE
        medicine > Resource limit=2 color=WHITE
        poison > Resource limit=3 color=RED
        wall > Immovable color=BLACK  
    LevelMapping
        0 > hole
        c > cloud 
        b > box
        m > medicine
        p > poison
        w > wall   
        g > goal 
    InteractionSet
        avatar wall > stepBack  
        medicine avatar > killSprite
        avatar poison > changeResource resource=medicine value=-1
        avatar poison > killIfHasLess resource=medicine limit=-1
        avatar medicine > changeResource resource=medicine value=1
        box avatar > killSprite
        poison avatar > killSprite
        box avatar  > bounceForward
        box wall    > undoAll        
        box poison > undoAll
        box medicine > undoAll
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