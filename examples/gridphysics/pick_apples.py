### Modulat absolute numbrs

level1 = """
wwwwwwwwwwwwwwwwwwwwwwwwww
wA                       w
w        a               w
w                        w
w                        w
w    o                   w
w  a               o     w
w                a       w
w                        w
wwwwwwwwwwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwwwwwwwwwww
wA                       w
w        a     o         w
w              a         w
w  o     a  a      o     w
w                o       w
w  a               o     w
w       o     a  a       w
w  o       a             w
wwwwwwwwwwwwwwwwwwwwwwwwww
"""

level3 = """
wwwwwwwwwwwwwwwwwwwwwwwwww
w                        w
w        a     o         w
w                 o ooooow
w                 o      w
w                o    A  w
w  a              oooooo w
w       o     a  a       w
w  o       a             w
wwwwwwwwwwwwwwwwwwwwwwwwww
"""

level4 = """
wwwwwwwwwwwwwwwwwwwwwwwwww
wA                       w
w     b  a     o         w
w              a         w
w  o     a  a      o     w
w           b    o       w
w  a               o     w
w       o     a  a       w
w  o       a             w
wwwwwwwwwwwwwwwwwwwwwwwwww
"""

level5 = """
wwwwwwwwwwwwwwwwwwwwwwwwww
w            s          Aw
w    a    s        s     w
w              a         w
w      o a  a   s     s  w
w    s      b    o       w
w  a   s   b       o     w
w       o   s            w
w   s         s       s  w
wwwwwwwwwwwwwwwwwwwwwwwwww
"""

        
game = """
BasicGame frame_rate=30
    SpriteSet
        fruit > Immovable
            apple > color=GREEN
            orange > color=ORANGE
        avatar  > MovingAvatar color=WHITE
        wall > Immovable color=BLACK
    LevelMapping
        w > wall   
        a > apple
        o > orange
    InteractionSet
        avatar wall > stepBack
        fruit wall > undoAll
        fruit fruit > undoAll
        avatar orange > killSprite
        apple avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False          
        SpriteCounter stype=apple limit=0 win=True

"""

game_with_blueberries = """
BasicGame frame_rate=30
    SpriteSet
        fruit > Immovable
            apple > color=GREEN
            orange > color=ORANGE
            blueberry >color=BLUE
            strawberry > color=RED
        avatar  > MovingAvatar color=WHITE
        wall > Immovable color=BLACK
    LevelMapping
        w > wall   
        a > apple
        b > blueberry
        o > orange
        s > strawberry
    InteractionSet
        avatar wall > stepBack
        fruit wall > undoAll
        fruit fruit > undoAll
        avatar orange > killSprite
        apple avatar > killSprite
        blueberry avatar > killSprite
        strawberry avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False          
        SpriteCounter stype=apple limit=0 win=True
        SpriteCounter stype=blueberry limit=0 win=True
        SpriteCounter stype=strawberry limit=0 win=True

"""

level_game_pairs = [[game, level1], [game, level2], [game, level3], [game_with_blueberries, level4], [game_with_blueberries, level5]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random
    level_game = random.choice(level_game_pairs)
    VGDLParser.playGame(*level_game)
    # VGDLParser.playGame(game_with_blueberries, level5)

