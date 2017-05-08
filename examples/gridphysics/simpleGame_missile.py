'''
VGDL example: Urgent

@author: Jake
'''
# level = """
# wwwwwwwww
# w   1   w
# w   1   w
# A   1   G
# w   1   w
# w   1   w
# wwwwwwwww
# """

level = """
wwwwwwwwwwwww
w     1     w
w     1     w
A     1     G
w     1     w
w     1     w
wwwwwwwwwwwww
"""

# box_level = """
# wwwwwwwwwwwww
# wA    w     w
# w  b  w     w
# wwwpwww     G
# w     w     w
# w           w
# wwwwwwwwwwwww
# """


game = """
BasicGame
  SpriteSet         
    goal > Immovable color=GREEN
    wall > Immovable color=BLACK
    glass > Immovable color=BLUE
    bullet > Missile speed=1 singleton=True color=RED
    avatar  > ShootAvatar stype=bullet

  LevelMapping
    w > wall       
    G > goal
    b > bullet
    1 > glass

  InteractionSet
    glass bullet > killSprite 
    bullet wall > killSprite    
    goal avatar > killSprite

    bullet EOS > killSprite

    avatar EOS > stepBack
    avatar wall > stepBack
    avatar glass > stepBack
  TerminationSet
    SpriteCounter stype=goal win=True
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)  