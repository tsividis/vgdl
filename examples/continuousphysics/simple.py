game = """
BasicGame
    SpriteSet 
        inertial >
            avatar > InertialAvatar color=WHITE
        evil   >  
            goomba     > Immovable color=BROWN 
        goal > Immovable color=GREEN
        wall > ResourcePack color=BLACK
        poison > Immovable color=RED
            
    TerminationSet
        SpriteCounter stype=goal      win=True     
        SpriteCounter stype=avatar    win=False     
           
    InteractionSet
        goal avatar > killSprite
        avatar wall > wallStop friction=0
        avatar poison > killSprite
        avatar evil > killIfAlive
        
        
    LevelMapping
        w > wall
        G > goal
        P > poison
        1 > goomba
"""


level = """
wwwwwwwwww
w       Gw
w        w
w        w
w        w
w        w
w        w
w        w
w A      w
wwwwwwwwww
"""

level = """
wwwwwww
w    Gw
w  1  w
w  1  w
w  1  w
wA 1  w
wwwwwww
"""
level = """
wwwwwwwwww
wA      Gw
wwwwwwwwww
"""

level = """
      
    G 
      
      
 A    
      
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)