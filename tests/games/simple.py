
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
        cloner > Immovable color=GREEN
        box    > Immovable color=WHITE # orientation=RIGHT cooldown=1
        box2 > Immovable color=GREEN
        box3 > Immovable color=YELLOW
        flicker > Flicker timeout=1 color=ORANGE
        random > RandomNPC color=PURPLE speed=1 cooldown=1
        chaser > Chaser color=BLACK speed=1 cooldown=1 stype=box
        avatar  > MovingAvatar color=DARKBLUE
        cannon > SpawnPoint color=RED stype=sam spawnCooldown=1
        missile > Missile
            sam  > orientation=UP color=BLUE singleton=True
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