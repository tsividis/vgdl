level = """
wwwwwwww
w      w
w      w
w     kw
wA  wwww
ww     w
w      w
w  G   w
wwwwwwww
"""

game = """
BasicGame
    SpriteSet 
        avatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE
        keyavatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
        key > Resource color=GOLD

    TerminationSet
        SpriteCounter stype=goal      win=True     
        MultiSpriteCounter stype1=avatar stype2=keyavatar   win=False     
           
    InteractionSet
        
        avatar EOS  > killSprite
        keyavatar EOS  > killSprite
        goal keyavatar > killSprite
        avatar wall > wallStop
        keyavatar wall > wallStop
        key avatar > killSprite
        avatar key > transformTo stype=keyavatar

        
    LevelMapping
        w > wall
        G > goal
        k > key
"""



if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)