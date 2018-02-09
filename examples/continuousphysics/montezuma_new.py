

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
wwwwwwwwwwwwwwwwwwwwwwwww
w.......................w
w.......................w
wG.........A............w
wwwwwwww...wl....wwwwwwww
wk..........l..$.r.$....w
w..............$.r.$....w
w..............$.r.$....w
wwllw.....ccccc$...$wllww
w.l............$$$$$..l.w
w.l...................l.w
w............1..........w
wwwwwwwwwwwwwwwwwwwwwwwww
"""

game = """
BasicGame
    SpriteSet
        background > Immovable color=LIGHTGRAY
        offrope > Immovable color=LIGHTGRAY
        goomba > Missile orientation=LEFT color=BROWN speed=0.2
        goal > Immovable color=GREEN
        key > Resource limit=1 color=GOLD
        wall > Immovable color=BLACK
        ladder > Immovable color=YELLOW
        rope > Immovable color=RED

        avatar > MarioAvatar strength=15 physicstype=GravityPhysics color=WHITE
        ladderavatar > VerticalAvatar speed=0.3 color=WHITE
        ropeavatar > RopeAvatar physicstype=ContinuousPhysics color=WHITE

        conveyor > Conveyor strength=3


    TerminationSet
        SpriteCounter stype=goal      win=True
        MultiSpriteCounter stype1=avatar stype2=ladderavatar stype3=ropeavatar win=False

    InteractionSet

        avatar goomba > killSprite
        avatar EOS  > killSprite
        goomba EOS > killSprite
        ladderavatar goomba > killSprite

        
        goal avatar > killIfOtherHasMore resource=key
        key avatar > killSprite
        avatar key > changeResource resource=key value=1
        avatar wall > killIfTooFast speed=23
        avatar wall > wallStop
        ropeavatar wall > wallStop
        goomba wall > wallBounce
        avatar goal > stepBack
        
        avatar conveyor > killIfTooFast speed=23
        avatar conveyor > conveySprite
        avatar conveyor > wallStop

        ladderavatar background > transformTo stype=avatar
        avatar ladder > transformTo stype=ladderavatar

        ropeavatar offrope > transformTo stype=avatar
        avatar rope > transformTo stype=ropeavatar


    LevelMapping
        . > background
        w > background wall
        G > background goal
        1 > background goomba
        l > background ladder
        k > background key
        A > background avatar
        c > background conveyor
        r > background rope
        $ > background offrope
        W > background wall offrope

"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
