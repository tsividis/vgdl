levels = [
"""
wwwwwwwwwwwww
w           w
w           w
w       b   w
w       b   w
w       A   w
wwwwwwwwwwwww
""",
"""
wwwwwwwwwwwww
w           w
w           w
w       b   w
w       b   w
w       A   w
wwwwwwwwwwwww
""",
]

'''
stepBack
killSprite
bounceForward
~~cloneSprite~~
~~transformTo~~


flipDirection
reverseDirection


'''
game = """
BasicGame
    SpriteSet
        box    > Immovable color=WHITE 
        avatar  > MovingAvatar color=DARKBLUE speed=1
        wall > Immovable color=DARKGRAY
    LevelMapping
        A > avatar
        b > box
    InteractionSet
        avatar wall > stepBack
        box avatar > killSprite

        wall avatar > stepBack
        wall box > stepBack

        box wall > stepBack
        avatar box > stepBack
        box avatar > stepBack


        avatar EOS > stepBack
        wall EOS > stepBack
        box EOS > stepBack

        avatar avatar > stepBack
        box box > stepBack
        wall wall > stepBack

    TerminationSet
        SpriteCounter stype=box limit=0 win=True
        SpriteCounter stype=avatar limit=0 win=False
"""