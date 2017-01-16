'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''

# box_level = """
# wwww
# wp w
# wAgw
# wwww
# """

box_level = """
wwwwwwwww
w  g    w
w    2  w
wAp  w3ww
w    w ww
wwwwwwwww
"""

# box_level = """
# wwwwwwwww
# w     m w
# w       w
# wAp  wgww
# w    w ww
# wwwwwwwww
# """

push_game = """
BasicGame frame_rate=30
    SpriteSet     

        avatar > MovingAvatar color=DARKBLUE
        poison > ResourcePack limit=3 color=BROWN
        box1  > ResourcePack color=ORANGE
        box2 > ResourcePack color=RED
        walll > ResourcePack color=BLACK      
        missile > Missile color=BLUE speed=.2      
        goal > ResourcePack color=ORANGE
        goal_substitute > ResourcePack color=GOLD
    LevelMapping
        p > poison
        1 > box2
        2 > box2
        w > walll   
        g > goal 
        3 > goal_substitute
        m > missile
    InteractionSet
        box1 avatar > bounceForward
        box2 avatar > bounceForward
        walll avatar > bounceForward
        poison avatar > bounceForward
        goal_substitute avatar > bounceForward
        goal avatar > killSprite
    TerminationSet
        SpriteCounter stype=goal    limit=0 win=True
        SpriteCounter stype=avatar  limit=0 win=False          
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(push_game, box_level)    