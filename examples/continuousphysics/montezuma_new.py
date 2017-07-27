# level = """
# wwwwwwwwwwwwwwwwwwww
# w                  w
# wG       A        Gw
# wwww   wwlww    wwww
# w        l         w
# w                  w
# wwwl  wwwwwww   lwww
# w  l            l  w
# wG        1        w
# wwwwwwwwwwwwwwwwwwww
# """

level = """
wwwwwwwwwwwwwwwwwwww
w..................w
w..................w
wG.........A.......w
wwww...wwlww....wwww
wk.......l.........w
w..................w
w..................w
wwwl..wwwwwww...lwww
w..l............l..w
w..l............l..w
w..................w
wwwwwwwwwwwwwwwwwwww
"""

'''
level = """
wwwwwwwwwwwwwwwwwwww
w..................w
w..................w
wG.................w
wwww...wwlww....wwww
w........l.........w
w..................w
wA.................w
wwwl..wwwwwww...lwww
w..l............l..w
w..l............l..w
w..................w
wwwwwwwwwwwwwwwwwwww
"""
'''


#avatar goal > stepBack
#        keyavatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE
#        keyladderavatar > VerticalAvatar speed=0.3 color=WHITE
'''
game = """
BasicGame
    SpriteSet
        background > Immovable color=LIGHTGRAY
        goomba > Missile orientation=LEFT color=BROWN speed=0.2
        goal > Immovable color=GREEN
        key > Immovable color=GOLD
        wall > Immovable color=BLACK
        ladder > Immovable color=YELLOW

        avatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE
        ladderavatar > VerticalAvatar speed=0.3 color=WHITE
        keyavatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE
        keyladderavatar > VerticalAvatar speed=0.3 color=WHITE


    TerminationSet
        SpriteCounter stype=goal      win=True
        MultiSpriteCounter stype1=avatar stype2=ladderavatar stype3=keyavatar stype4=keyladderavatar win=False

    InteractionSet

        avatar goomba > killSprite
        avatar EOS  > killSprite
        goomba EOS > killSprite
        ladderavatar goomba > killSprite

        avatar goal > stepBack
        goal keyavatar > killSprite
        key avatar > killSprite
        avatar key > transformTo stype=keyavatar
        avatar wall > wallStop
        goomba wall > wallBounce
        keyavatar goomba > killSprite
        keyavatar EOS  > killSprite
        keyavatar wall > wallStop
        ladderavatar background > transformTo stype=avatar
        avatar ladder > transformTo stype=ladderavatar
        keyladderavatar background > transformTo stype=keyavatar
        keyavatar ladder > transformTo stype=keyladderavatar

    LevelMapping
        . > background
        w > background wall
        G > background goal
        1 > background goomba
        l > background ladder
        k > background key
        A > background avatar
"""
'''
game = """
BasicGame
    SpriteSet
        background > Immovable color=LIGHTGRAY
        goomba > Missile orientation=LEFT color=BROWN speed=0.2
        goal > Immovable color=GREEN
        key > Resource limit=1 color=GOLD
        wall > Immovable color=BLACK
        ladder > Immovable color=YELLOW

        avatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE
        ladderavatar > VerticalAvatar speed=0.3 color=WHITE

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
        avatar wall > wallStop
        goomba wall > wallBounce
        avatar goal > stepBack

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
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
