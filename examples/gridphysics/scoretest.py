
# level = """
# wwwwwwwwwww
# w  w      w
# wA   1   gw
# wwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwww
# w Aw1     11pw
# w1   p2    h w
# wwwwwwwwwwwwww
# """


level = """
wwwwwwwwwwwwwwwwww
w  1    w  A    2w
w    2  w        w
w  111    2   1 ww
w     1         ww
ww 2222          w
w              p w
w     wwwww      w
w  g             w
wwwwwwwwwwwwwwwwww
"""

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

game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > ResourcePack
            goal1 > color=GOLD
            goal2 > color=ORANGE
        poison > ResourcePack 
            poison1 > color=WHITE
            poison2 > color=PINK
        box > ResourcePack
            box1 > color=RED
            box2 > color=LIGHTBLUE
        entry > Portal color=YELLOW stype=exit1 
        exit1 > Portal color=PURPLE
        wall > Immovable
        score > Resource color=SCORECOLOR limit=10 
        medicine > Resource limit=2 color=YELLOW 
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
        m > medicine
    InteractionSet
        avatar wall > stepBack  
        avatar poison > killSprite
        avatar entry > teleportToExit
        goal avatar > changeScore value=1
        goal avatar > killSprite
        box1 avatar > changeScore value=.5
        box2 avatar > changeScore value=-.5
        box1 avatar > killSprite
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
        avatar medicine > changeResource resource=medicine value=2
        medicine avatar > killSprite
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random
    levels = [l for l in locals().keys() if 'level' in l]
    index = random.choice(range(len(levels)))
    VGDLParser.playGame(game, locals()[levels[index]])   