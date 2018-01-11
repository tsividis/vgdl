

level = """
wwwwwwwww
w A1    w
w 1  2  w
w 2  wgww
w  3 w ww
wwwwwwwww
"""

game = """
BasicGame frame_rate=30
    SpriteSet        
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        goal > ResourcePack color=GOLD
        poison > ResourcePack limit=3 color=BROWN
        box  > ResourcePack 
            box1 > color=GREEN
            box2 > color=LIGHTBLUE
            box3 > color=RED
        wall > Immovable color=BLACK      
        score > Resource color=PINK limit=10  
    LevelMapping
        p > poison
        3 > box3
        1 > box1
        2 > box2
        w > wall   
        g > goal 
    InteractionSet
        avatar wall > stepBack  
        missile wall > reverseDirection
        poison avatar > killSprite
        avatar poison > killSprite
        goal avatar > killSprite
        box avatar > bounceForward
        goal box > bounceForward
        goal wall > undoAll
        goal poison > undoAll
        box poison > undoAll
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    