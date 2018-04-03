
levels = ["""
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                              w
w                              w
w                              w
w                              w
w              A               w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww

""", """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                              w
w                              w
w                              w
w                              w
w              A               w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
""", """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                              w
w                              w
w                              w
w                              w
w              A               w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
""", """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                              w
w                              w
w                              w
w                              w
w              A               w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""]


game = """
BasicGame
    SpriteSet
        box    > Immovable color=WHITE 
        avatar  > MovingAvatar color=DARKBLUE speed=2
        wall > Immovable color=DARKGRAY
    InteractionSet
        avatar wall > stepBack
        box avatar > killSprite

    TerminationSet
        SpriteCounter stype=box limit=0 win=True
"""

game2 = """
BasicGame
    SpriteSet
        white_box    > Immovable color=WHITE 
        avatar  > MovingAvatar color=DARKBLUE speed=2
        wall > Immovable color=DARKGRAY
    InteractionSet
        
        white_box avatar > killSprite
        avatar wall > stepBack

    TerminationSet
        SpriteCounter stype=white_box limit=0 win=True
"""