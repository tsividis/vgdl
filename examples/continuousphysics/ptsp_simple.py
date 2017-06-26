'''
VGDL example: a simplified version the physical TSP benchmark.

@author: Tom Schaul
'''


game = """
BasicGame
    SpriteSet    
        pad    > Immovable color=BLUE
        avatar > InertialAvatar
            
    TerminationSet
        SpriteCounter stype=pad    win=True     
        SpriteCounter stype=avatar win=False     
           
    InteractionSet
        avatar wall > wallStop
        pad avatar    > killSprite
        
    LevelMapping
        G > pad
"""


level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwww
w        w    w    w       w
w    A    wwww    www      w
w                   w     ww
w             G     w  G   w
w   w                      w
w    www                w  w
w      wwwwwww        www  w
w                    ww    w
w  G                  w    w
w        ww  G           G w
w     wwwwwwwwww           w
wwwwwwwwwwwwwwwwwwwwwwwwwwww
"""


'''
level = """
wwwwwwwwwwwwwwwwwwwwwwwwwwww
w        w    w    w       w
w    A    wwww    www      w
w                   w     ww
w                   w      w
w   w                      w
w    www                w  w
w      wwwwwww        www  w
w                    ww    w
w                     w    w
w        ww              G w
w     wwwwwwwwww           w
wwwwwwwwwwwwwwwwwwwwwwwwwwww
"""
'''

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)
        
