'''
Simple interactions: get/lose points, can't pass through walls, object gets pushed.
'''


# level = """
# wwwwwwwww
# w  1    w
# w    2  w
# wAp  wgww
# w    w ww
# wwwwwwwww
# """

# level2 = """
# wwwwwwwww
# wA 1    w
# w    2  w
# w p  w ww
# w   gw ww
# wwwwwwwww
# """

level = """
000000000
0  1  A 0
0    2  0
0 G  0 00
0 O  0 00
000000000
"""
game = """
BasicGame frame_rate=30
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE
        poison > Passive color=BROWN
        box1 > Immovable color=ORANGE
        box2 > ResourcePack color=BLUE
        goal > ResourcePack color=BLUE
        oldGl > ResourcePack color=GOLD
        wall > Resource color=BLACK
    InteractionSet
        box1 avatar > killSprite
        poison avatar > killSprite
        wall avatar > killSprite
        oldGl avatar > killSprite
        box2 avatar > killSprite
        goal avatar > killSprite
        avatar wall > stepBack
    TerminationSet
        SpriteCounter stype=avatar limit=0 win=False
        SpriteCounter stype=goal limit=0 win=True
    LevelMapping
        G > goal
        0 > wall
        2 > poison
        A > avatar
        O > oldGl
        1 > box1
        3 > box2    
"""


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)    