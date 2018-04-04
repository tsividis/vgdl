levels = ["""
wwwwwwwwwwwwwwwwwwww
w                  w
w                  w
w                  w
w                  w
w              A   w
wwwwwwwwwwwwwwwwwwww

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

    TerminationSet
        SpriteCounter stype=box limit=0 win=True
"""