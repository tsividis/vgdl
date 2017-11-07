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

level = """
wwwwwwww
w      w
w      w
w    kGw
wA  wwww
wwwwww w
w      w
w      w
wwwwwwww
"""

game = """
BasicGame
    SpriteSet 
        avatar > MarioAvatar strength=22 physicstype=GravityPhysics color=WHITE
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
        key > Resource limit=1 color=GOLD
        

    TerminationSet
        SpriteCounter stype=goal      win=True     
        SpriteCounter stype=avatar     win=False     
           
    InteractionSet
        
        avatar EOS  > killSprite
        avatar wall > wallStop
        avatar key > changeResource resource=key value=1
        key avatar > killSprite
        goal avatar > killIfOtherHasMore resource=key

        
    LevelMapping
        w > wall
        G > goal
        k > key
"""


level_game_pairs = [[game, level]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)