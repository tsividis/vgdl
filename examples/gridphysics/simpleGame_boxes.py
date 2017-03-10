'''
VGDL example: UndoAll Problem

@author: Jake
'''
# level = """
# wwwwwwwwwwwww
# w     w     w
# w     w     w
# A     w     G
# w     w     w
# w     w     w
# wwwwwwwwwwwww
# """

level = """
wwwwwwwwwwwww
wA    w     w
w     w     w
w x x w     G
w     w     w
wb          w
wwwwwwwwwwwww
"""

    # avatar  > ShootAvatar stype=bullet

game = """
BasicGame
  SpriteSet         
    goal > Immovable color=GREEN
    wall > Immovable color=BLACK
    bullet > Missile speed=.6 orientation=RIGHT color=RED
    box1 > ResourcePack color=GREEN

    avatar > MovingAvatar color=DARKBLUE
  LevelMapping
    w > wall       
    G > goal
    b > bullet
    x > box1

  InteractionSet
    goal avatar > killSprite

    box1 avatar > bounceForward
    box2 avatar > bounceForward
    box1 wall > stepBack
    box1 box1 > stepBack
    avatar box1 > stepBack
    bullet wall > reverseDirection
    bullet box1 > reverseDirection
    avatar bullet > killSprite
    avatar EOS > stepBack
    avatar wall > stepBack

  TerminationSet
    SpriteCounter stype=goal win=True
    SpriteCounter stype=avatar win=False
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)  