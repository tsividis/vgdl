

level = """
wwwwwwwwwwwwwwwwwwww
w..................w
w..................w
wG.........A.......w
wwww...wwlww....wwww
wk.......l.........w
w..................w
w..................w
wwwl..ccccccc...lwww
w..l............l..w
w..l............l..w
w.........1........w
wwwwwwwwwwwwwwwwwwww
"""

level = """
wwwwwwwwwwwwwwwwwwww
w..................w
w..................w
wG.........A.......w
wwww...wwlww....wwww
wk.......l.........w
w..................w
w..................w
wwwl..ccccccc...lwww
w..l............l..w
w..l............l..w
w.........1........w
wwwwwwwwwwwwwwwwwwww
"""

game = """
BasicGame
    SpriteSet
        background > Immovable color=LIGHTGRAY
        goomba > Missile orientation=LEFT color=BROWN speed=0.2
        goal > Immovable color=GREEN
        key > Resource limit=1 color=GOLD
        wall > Immovable color=BLACK
        ladder > Immovable color=YELLOW

        avatar > MarioAvatar strength=15 physicstype=GravityPhysics color=WHITE
        ladderavatar > VerticalAvatar speed=0.3 color=WHITE

        conveyor > Conveyor strength=5


    TerminationSet
        SpriteCounter stype=goal      win=True
        MultiSpriteCounter stype1=avatar stype2=ladderavatar win=False

    InteractionSet

        avatar goomba > killSprite
        avatar EOS  > killSprite
        goomba EOS > killSprite
        ladderavatar goomba > killSprite

        
        goal avatar > killIfOtherHasMore resource=key
        key avatar > killSprite
        avatar key > changeResource resource=key value=1
        avatar wall > killIfTooFast speed=26
        avatar wall > wallStop
        goomba wall > wallBounce
        avatar goal > stepBack
        
        avatar conveyor > killIfTooFast speed=26
        avatar conveyor > conveySprite
        avatar conveyor > wallStop

        ladderavatar background > transformTo stype=avatar
        avatar ladder > transformTo stype=ladderavatar


    LevelMapping
        . > background
        w > background wall
        G > background goal
        1 > background goomba
        l > background ladder
        k > background key
        A > background avatar
        c > background conveyor

"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
