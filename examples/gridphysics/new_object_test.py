
level = """
wwwwwwwwwww
w  w      w
wA   1   gw
wwwwwwwwwww
"""

level2 = """
wwwwwwwwwww
w  w 1    w
wA   2   hw
wwwwwwwwwww
"""

# level3 = """
# wwwwwwwwwww
# w  w m    w
# wA   2   gw
# wwwwwwwwwww
# """

# level2 = """
# wwwwwwwwwww
# w iw 1    w
# wA w 2  ogw
# wwwwwwwwwww
# """

# level1 = """
# wwwwwwwwwwwwwwwwww
# w  1    w       2w
# w    2  w        i
# o         2     ww
# w     1         ww
# ww         q A   w
# w        q  m  p w
# w     wwwww  n   w
# w  g          q  w
# wwwwwwwwwwwwwwwwww
# """

# level2 = """
# wwwwwwwwwwwwwwwwww
# wA w    p        w
# w  w 2    ip     w
# w       w 2  w nww
# w    w1      w  ww
# wwwww q    q     w
# w m p    q     1 w
# w    2       o   w
# w        2     g w
# wwwwwwwwwwwwwwwwww
# """

# level3 = """
# wwwwwwwwwwwwwwwwww
# w   n   p   o    w
# w    2     p   g w
# w      w  2  w  ww
# w q          w  ww
# wwwww q  w  m    w
# w  iw    w     1 w
# w   w2       q   w
# wA  w    2       w
# wwwwwwwwwwwwwwwwww
# """

# level4 = """
# wwwwwwwwwwwwwwwwww
# wp      w    A  2w
# w  g 2  w        w
# w         2     iw
# o     1         ww
# ww   www   m     w
# w   q          p w
# w    2           w
# w        2n   1  w
# wwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwiwwwwwww
# wp      w    A  2w
# w  g 2  w  n wwwww
# w         2      w
# o     1         ww
# ww   www   m     w
# w   q          p w
# w    2           w
# w        2    1  w
# wwwwwwwwwwwwwwwwww
# """


# level4 = """
# wwwwwwwwwwwwwwwwww
# wp     Aw    g  2w
# w    2  w        w
# w          1    ww
# w  1  1  1      ww
# ww   www   q     w
# w              p w
# w                w
# w    1   2    1  w
# wwwwwwwwwwwwwwwwww
# """

# level5 = """
# wwwwwwwwwwwwwwwwww
# wp     Aw       2w
# w    11111       w
# w  2       1www ww
# w  2  2  1      ww
# ww   www   q w   w
# w            w g w
# w            w   w
# w    1   2    1  w
# wwwwwwwwwwwwwwwwww
# """

# level6 = """
# wwwwwwwwwwwwwwwwww
# wp      w       2w
# w       1    11  w
# w   g      1    ww
# w  1  12 1      ww
# ww         q     w
# w              A w
# w  ww     q      w
# w    1   2    1  w
# wwwwwwwwwwwwwwwwww
# """

game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > ResourcePack
            goal1 > color=GOLD
            goal2 > color=ORANGE
        poison1 > ResourcePack color=WHITE
        poison2 > ResourcePack color=PINK
        box1 > ResourcePack color=RED
        box2 > ResourcePack color=LIGHTBLUE
        entry > Portal color=GRAY stype=exit1 
        exit1 > Portal color=PURPLE
        wall > Immovable color=BLACK      
        score > Resource color=PINK limit=10  
        missile > Missile
            missile1 > color=GREEN  speed=.5 
            missile2 > color=ORANGE speed=1
    LevelMapping
        p > poison1
        q > poison2
        1 > box1
        2 > box2
        i > entry
        o > exit1
        w > wall   
        g > goal1
        h > goal2 
        m > missile1
        n > missile2
    InteractionSet
        avatar wall > stepBack  
        poison1 avatar > killSprite
        poison2 avatar > killSprite
        avatar poison1 > killSprite
        avatar poison2 > killSprite
        avatar entry > teleportToExit
        goal avatar > killSprite
        box1 avatar > bounceForward
        box2 avatar  > killSprite
        goal box1 > bounceForward
        goal box2 > bounceForward
        goal wall > undoAll
        goal poison1 > undoAll
        goal poison2 > undoAll
        box1 wall    > undoAll    
        box2 wall    > undoAll    
        box1 poison1 > undoAll
        box2 poison1 > undoAll
        box1 poison2 > undoAll
        box2 poison2 > undoAll
        missile wall > turn
        missile box1 > turn
        missile box2 > turn
        missile poison1 > turn
        missile poison2 > turn
        avatar missile > killSprite
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    