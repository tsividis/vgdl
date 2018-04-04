
levels = ["""
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                              w
w          BBBBB               w
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
        avatar  > MovingAvatar color=DARKBLUE speed=1
        wall > Immovable color=DARKGRAY
    LevelMapping
        A > avatar
        B > box
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
        avatar  > MovingAvatar color=DARKBLUE speed=1
        wall > Immovable color=DARKGRAY
    InteractionSet
        
        white_box avatar > killSprite
        avatar wall > stepBack

    TerminationSet
        SpriteCounter stype=white_box limit=0 win=True
"""

test_hypothesis = """
BasicGame
    SpriteSet
        box > ResourcePack color=WHITE
        wall > ResourcePack color=DARKGRAY
        avatar > MovingAvatar color=DARKBLUE
    InteractionSet
        avatar box > nothing
        box avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""