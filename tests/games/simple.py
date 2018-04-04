
levels = ["""
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w                              w
w                              w
w                              w
w          BBBBB               w
w              A               w
w                              w
w                              w
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
# game and game2 are identical (just with a name change)
# (keep for testing purposes)
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

game3 = """
BasicGame
    SpriteSet
        box    > Immovable color=WHITE 
        avatar  > MovingAvatar color=DARKBLUE speed=1
        wall > Immovable color=DARKGRAY

    LevelMapping
        A > avatar
        B > box

    InteractionSet
        # avatar box > stepBack
        # avatar wall > stepBack

    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""
# Write your own test hypothesis here
# This test_hypothesis passes after runing one execute step on levels[0]
test_hypothesis = """
BasicGame
    SpriteSet
        box > ResourcePack color=WHITE
        wall > ResourcePack color=DARKGRAY
        avatar > MovingAvatar color=DARKBLUE

    InteractionSet
        # should learn this rule after one step 
        box avatar > killSprite

    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""

test_hypothesis2 = """
BasicGame
    SpriteSet
        box > ResourcePack color=WHITE
        wall > ResourcePack color=DARKGRAY
        avatar > MovingAvatar color=DARKBLUE
        whale > ResourcePack color=ORANGE

    InteractionSet
        # should learn this rule after one step 
        avatar box > stepBack

    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
"""