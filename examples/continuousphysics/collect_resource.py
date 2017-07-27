'''
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
'''


level = """
wwwwwwww
w     kw
w      w
w      w
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
        key > Resource limit=1 color=GOLD

    TerminationSet
        SpriteCounter stype=goal      win=True     
        SpriteCounter stype=avatar     win=False     
           
    InteractionSet
        
        avatar EOS  > killSprite
        avatar wall > wallStop
        key avatar > killSprite
        avatar key > changeResource resource=key value=1
        goal avatar > killIfOtherHasMore resource=key
        avatar goal > stepBack

        
    LevelMapping
        w > wall
        G > goal
        k > key
"""



if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)