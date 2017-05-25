'''
VGDL example: a simple dodge-the-bullets game

@author: Tom Schaul
'''

level = """
wwwwwwwwwwwwwwwwwwww
w   w  <  -      Gww
w   w-            ww
w            ww   ww
w   < w ^      w  ww
w ^   w   V    V www
w   -        v    ww
ww   <    www     ww
wA                ww
www     v       wwww
wwwwwwwwwwwwwwwwwwww
"""

game = """
BasicGame
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE
        bullet > Missile
            slowbullet > speed=0.1 color=ORANGE
                upslow    >     orientation=UP    
                downslow  >     orientation=DOWN  
                leftslow  >     orientation=LEFT  
                rightslow >     orientation=RIGHT
            fastbullet > speed=0.2  color=RED
                rightfast >     orientation=RIGHT
                downfast  >     orientation=DOWN  
        wall      > Immovable color=BLACK
        goal      > Immovable  color=GREEN
        
    InteractionSet
        goal   avatar > killSprite
        avatar bullet > killSprite
        avatar wall   > stepBack
        bullet EOS    > wrapAround
    
    TerminationSet
        SpriteCounter stype=goal   limit=0 win=True
        SpriteCounter stype=avatar limit=0 win=False
    
    LevelMapping
        ^ > upslow
        < > leftslow
        v > downslow
        - > rightslow
        = > rightfast
        V > downfast
        G > goal
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    