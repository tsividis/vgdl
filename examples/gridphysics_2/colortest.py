

level = """
wwwwwwwwwwwwwwwwwwwwww
wp      w    A      2w
w  g 2  w       6    w
w              ww   ww
w     1     5  4    hw
ww     w      w      w
w   q  w    a w    p w
w    2 w  9   w      w
w             1  b   w
wwwwwwwwwwwwwwwwwwwwww
"""



game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > ResourcePack
            goal1 > color=GREEN
            goal2 > color=BLUE
        poison1 > ResourcePack color=RED
        poison2 > ResourcePack color=WHITE
        box > ResourcePack 
            box1 > color=BROWN
            box2 > color=BLACK
            box3 > color=ORANGE
            box4 > color=YELLOW
            box5 > color=PINK
            box6 > color=GOLD
            box7 > color=LIGHTRED
            box8 > color=LIGHTORANGE
            box9 > color=LIGHTBLUE
            box10 > color=LIGHTGREEN
            box11 > color=DARKGRAY
            box12 > color=DARKBLUE


        wall > Immovable
        missile > Missile color=PURPLE speed=.2      
    LevelMapping
        p > poison1
        q > poison2
        1 > box1
        2 > box2
        3 > box3
        4 > box4
        5 > box5
        6 > box6
        7 > box7
        8 > box8
        9 > box9
        a > box10
        b > box11
        w > wall   
        g > goal1
        h > goal2 
        m > missile
    InteractionSet
        avatar wall > stepBack  
        missile wall > reverseDirection
        avatar poison1 > killSprite
        avatar poison2 > killSprite
        goal avatar > killSprite
        box1 avatar > bounceForward
        box2 avatar  > killSprite
        goal box1 > undoAll
        goal box2 > undoAll
        goal wall > undoAll
        goal poison1 > undoAll
        goal poison2 > undoAll
        box1 wall    > undoAll    
        box2 wall    > undoAll    
        box1 box1 > undoAll
        poison1 box1 > killSprite
        poison2 box1 > killSprite
        poison1 box2 > undoAll
        poison2 box2 >undoAll
    TerminationSet
        SpriteCounter stype=goal    limit=1 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random
    levels = [l for l in locals().keys() if 'level' in l]
    index = random.choice(range(len(levels)))
    VGDLParser.playGame(game, locals()[levels[index]])
