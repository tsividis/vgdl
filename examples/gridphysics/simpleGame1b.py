'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

box_level = """
wwwwwwwwwwwww
w  2 m   w  w
w   1       w
w t A 1 p  gw
www    hwwwww
w c  m  w   w
w 1  t     3w
w  2 c  p  ww
wwwwwwwwwwwww
"""

        
push_game = """
BasicGame frame_rate=30
    SpriteSet        
        hole   > ResourcePack color=LIGHTBLUE
        avatar > MovingAvatar color=DARKBLUE #cooldown=4 
        box    > ResourcePack 
            box1 > color=ORANGE               
            box2 > color=PINK
        treasure > Portal color=GREEN limit=500
        goal > ResourcePack color=GOLD
        trap > ResourcePack color=RED limit=5
        cloud > ResourcePack color=BLUE
        medicine > ResourcePack limit=3 color=WHITE
        poison > ResourcePack limit=3 color=BROWN
        wall > ResourcePack color=BLACK      
        score > ResourcePack color=PINK limit=10         
    LevelMapping
        0 > hole
        1 > box1
        2 > box2  
        3 > treasure 
        t > trap    
        c > cloud 
        m > medicine
        p > poison
        w > wall   
        g > goal 
        h > hole
    InteractionSet
        wall avatar > killSprite
        hole avatar > killSprite
        treasure avatar > changeResource resource=score value=5
        treasure avatar > killSprite
        trap avatar > changeResource resource=score value=-5
        trap avatar > killSprite
        cloud avatar > killSprite
        avatar medicine > changeResource resource=medicine value=1
        medicine avatar > killSprite
        avatar poison > changeResource resource=medicine value=-1
        poison avatar > killSprite
        avatar poison > killIfHasLess resource=medicine limit=-1
        box avatar  > bounceForward
        box wall    > undoAll        
        box box     > undoAll
        box hole    > killSprite
        box treasure > undoAll
        box poison > undoAll
        box medicine > undoAll
        goal avatar > killSprite  
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""

#        treasure avatar > collectResource scoreChange=5
#        trap avatar > collectResource scoreChange=-5
#        avatar wall > stepBack  

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(push_game, box_level)    