
level0 = """
wwwwwwwwwwwwwwwwwwwwww
wA                   w
w    a    x          w
w              f     w
w                    w
w      f             w
w                 x  w
w          a         w
w                    w
wwwwwwwwwwwwwwwwwwwwww
"""

level1 = """
wwwwwwwwwwwwwwwwwwwwww
wA                   w
w    a    x          w
w                    w
w                    w
w              z     w
w   x    z           w
w          a         w
w                    w
wwwwwwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwwwwwww
w                    w
w    a    x          w
w                    w
w                    w
w              y     w
w   x    y           w
w          a         w
w          A         w
wwwwwwwwwwwwwwwwwwwwww
"""

level3 = """
wwwwwwwwwwwwwwwwwwwwww
w                    w
w         x          w
w            y       w
w                    w
w          y   z     w
w   x    z           w
w                    w
w          A         w
wwwwwwwwwwwwwwwwwwwwww
"""

        
game0 = """
BasicGame frame_rate=30
    SpriteSet
        probe > Immovable color=BLUE
        converter > Immovable 
            converter1 > color=RED
            converter2 > color=PURPLE
        box > Immovable
            box1 > color=ORANGE
        fire > Immovable color=YELLOW     
        avatar > MovingAvatar color=WHITE
        wall > Immovable color=BLACK
    LevelMapping
        w > wall   
        a > box1
        b > box2
        f > fire
        x > probe
        z > converter1
        y > converter2
    InteractionSet
        avatar wall > stepBack
        avatar fire > stepBack 
        box avatar > bounceForward
        box probe > stepBack
        probe box > stepBack
        box box > stepBack
        box wall > stepBack
        probe wall > stepBack
        converter wall > stepBack
        probe converter > stepBack
        converter1 box > bounceForward  
        converter2 box > transformTo stype=fire 
        box fire > stepBack
        fire box > stepBack
        box fire > killSprite
        probe probe > stepBack
        probe avatar > bounceForward
        converter1 avatar > transformTo stype=fire
        probe fire > killSprite
        fire probe > killSprite
        avatar converter > stepBack
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False          
        SpriteCounter stype=probe limit=0 win=True
"""

game3 = """
BasicGame frame_rate=30
    SpriteSet
        probe > Immovable color=BLUE
        converter > Immovable 
            converter1 > color=RED
            converter2 > color=PURPLE
            converter3 > color=PINK
        box > Immovable
            box1 > color=ORANGE
            box2 > color=GREEN
        fire > Immovable color=YELLOW     
        avatar > MovingAvatar color=WHITE
        wall > Immovable color=BLACK
    LevelMapping
        w > wall   
        a > box1
        b > box2
        f > fire
        x > probe
        z > converter1
        y > converter2
        z > converter3
    InteractionSet
        avatar wall > stepBack
        avatar fire > stepBack 
        box avatar > bounceForward
        box probe > stepBack
        probe box > stepBack
        box box > stepBack
        box wall > stepBack
        probe wall > stepBack
        converter wall > stepBack
        probe converter > stepBack
        converter1 box1 > bounceForward  
        converter2 box1 > transformTo stype=fire 
        converter3 avatar > transformTo stype=box1
        box fire > stepBack
        fire box > stepBack
        box fire > killSprite
        probe probe > stepBack
        probe avatar > bounceForward
        converter1 avatar > transformTo stype=fire
        probe fire > killSprite
        fire probe > killSprite
        avatar converter > stepBack
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False          
        SpriteCounter stype=probe limit=0 win=True
"""


level_game_pairs = [[game0, level0], [game0, level1], [game0, level2],
                    [game3, level3]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random, sys
    if len(sys.argv)==2:
        level_game = level_game_pairs[int(sys.argv[1])]
    else:
        level_game = random.choice(level_game_pairs)
    VGDLParser.playGame(*level_game)
     