'''
VGDL example: a simple teleport-and-avoid-fire game. 

@author: Tom Schaul
'''


# level = """
# wwwwwwww
# wAiwwwww
# wwwwwwww
# w o wwww
# wwwwwwww
# w   o Gw
# wwwwwwww
# """

# level = """
# wwwwwwwwww
# w        w
# w        w
# w    i   w
# w    A   w
# w        w
# w        w
# w    o   w
# wo      Gw
# wwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwww
# wA  w  v  <  wO  Gw
# w   w        wx   w
# www w        wwww w
# w     w        w  w
# w <   wwwwwww     w
# w      x     <    w
# wwwww     www     w
# w         o       w
# wwwIw   v    x  www
# wwwwwwwwwwwwwwwwwww
# """

#Simplified; fewer portals.
# level = """
# wwwwwwwwwwwwwwwwwww
# wA  w  v  <  wO  Gw
# w  iw        wx   w
# wwwww        wwwwww
# w     w r      w  w
# w <   wwwwwww    ww
# w  r   x     <    w
# wwwww     www     w
# w         o       w
# wwwIw   v    x  www
# wwwwwwwwwwwwwwwwwww
# """

# Original.
level = """
wwwwwwwwwwwwwwwwwww
wA  w  v  <  wO  Gw
wo iw        wx   w
wwwww      o wwwwww
w     w r      w ow
w <   wwwwwww    ww
w  r   x     <    w
wwwww     www     w
w         i       w
wwwIw   v    x  www
wwwwwwwwwwwwwwwwwww
"""

game = """
BasicGame
    SpriteSet
        bullet > color=RED
            sitting  > Immovable
            random   > RandomNPC speed=0.25
            straight > Missile   speed=0.5
                vertical   > orientation=UP
                horizontal > orientation=LEFT
        structure > Immovable            
            goal  > color=GREEN
            portalentry > Portal 
                entry1 > stype=exit1 color=LIGHTBLUE 
                entry2 > stype=exit2 color=BLUE
            portalexit  > color=BROWN
                exit1  > 
                exit2  > 
    InteractionSet
        goal   avatar    > killSprite
        avatar bullet    > killSprite
        avatar wall      > stepBack
        random structure > stepBack
        random wall      > stepBack
        straight wall    > reverseDirection
        avatar portalentry > teleportToExit
        
    TerminationSet
        SpriteCounter stype=goal   limit=0 win=True
        SpriteCounter stype=avatar limit=0 win=False
    
    LevelMapping
        < > horizontal
        v > vertical
        x > sitting
        r > random
        G > goal
        i > entry1
        I > entry2
        o > exit1
        O > exit2
        
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    