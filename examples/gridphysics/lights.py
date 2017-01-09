'''
Amidar.

@author: Jake
'''


test_game = """
BasicGame
    SpriteSet    
        avatar > HorizontalAvatar speed=0.5
        lightOn > Immovable color=WHITE
        lightOff > Immovable color=BLACK
        switchOn > Immovable color=WHITE
        switchOff > Immovable color=BLACK
         
    TerminationSet  
        SpriteCounter stype=avatar  limit=0 win=False   

    InteractionSet
        switchOff avatar > transformTo stype=switchOn
        
        avatar EOS > stepBack

    ConditionalSet
        SpriteCount stype=switchOn count=2 > transformTo stype=lightOn applyto=lightOff


    LevelMapping
        l > lightOff
        s > switchOff
"""

test_level = """
wwwwwwwwwwwwwwwwwww
w        l        w
w                 w
w                 w
w                 w
w                 w
w                 w
ws       A       sw
wwwwwwwwwwwwwwwwwww
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(test_game, test_level)
        