
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
        avatar  > MovingAvatar color=DARKBLUE
        wall > Immovable color=DARKGRAY
    LevelMapping
        C > cloner
        F > flicker
        0 > base
        1 > box
        2 > box2
        3 > box3
        4 > random
        w > wall
        c > cannon
        s > sam
        A > avatar
    InteractionSet
        avatar wall > stepBack
        box avatar > killSprite
        avatar box2 > killSprite
        box3 avatar > killSprite

    TerminationSet
        SpriteCounter stype=box2 limit=0 win=True
        # SpriteCounter stype=box3 limit=0 win=False
        Termination


"""