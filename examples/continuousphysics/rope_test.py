level = """
wwwwwwwwwwwww
w   $ r $   w
w   $ r $   w
w   $ r $   w
wA  $   $  Gw
wwww$$$$$wwww
w           w
w           w
wwwwwwwwwwwww
"""

game = """
BasicGame
    SpriteSet
        
        offrope > Immovable color=LIGHTGRAY
       
        goal > Immovable color=GREEN

        wall > Immovable color=BLACK

        rope > Immovable color=RED

        avatar > MarioAvatar strength=15 physicstype=GravityPhysics color=WHITE

        ropeavatar > RopeAvatar physicstype=ContinuousPhysics color=WHITE



    TerminationSet
        SpriteCounter stype=goal      win=True
        MultiSpriteCounter stype1=avatar stype2=ropeavatar win=False

    InteractionSet

        avatar goomba > killSprite
        avatar EOS  > killSprite
        goomba EOS > killSprite
        ladderavatar goomba > killSprite

        
        goal avatar > killSprite
        avatar wall > killIfTooFast speed=40
        avatar wall > wallStop
        ropeavatar wall > wallStop
        avatar goal > stepBack



        ropeavatar offrope > transformTo stype=avatar
        avatar rope > transformTo stype=ropeavatar


    LevelMapping
        w > wall
        G > goal
        A > avatar
        r > rope
        $ > offrope

"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
