game = """
BasicGame
    SpriteSet 
        avatar > InertialAvatar color=WHITE
        evil   >  orientation=LEFT 
                fast     >  Walker color=BROWN speed=0.2
                slow     > Walker color=BROWN speed=0.1
        goal > Immovable color=GREEN
        wall > Immovable color=BLACK
        poison > Immovable color=RED
            
    TerminationSet
        SpriteCounter stype=goal  limit=0  win=True     
        SpriteCounter stype=avatar    win=False     
           
    InteractionSet
        goal avatar > killSprite
        avatar wall > wallStop friction=0.0
        evil wall > wallStop friction=0.0
        avatar evil > killIfAlive
        evil EOS > wrapAround
        
        
    LevelMapping
        w > wall
        G > goal
        1 > slow
        2 > fast
"""

level = """
wwwwwww
w    Gw
2      
w     w
w     w
   1   
w     w
w     w
      1
wA    w
wwwwwww
"""#works!


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)