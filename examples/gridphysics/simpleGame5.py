'''
VGDL example: Urgent

@author: Jake
'''
box_level = """
wwwwwwwwwwwww
w     w     w
w     w     w
A     w     G
w     w     w
w     w     w
wwwwwwwwwwwww
"""

push_game = """
BasicGame
  SpriteSet         
    goal > Immovable color=GREEN
    wall > Immovable color=BLACK
    bullet > Missile speed=1 singleton=True color=RED
    avatar  > ShootAvatar stype=bullet

  LevelMapping
    w > wall       
    G > goal

  InteractionSet
    wall bullet > killSprite 
    bullet wall > killSprite    
    goal avatar > killSprite

    bullet EOS > killSprite

    avatar EOS > stepBack
    avatar wall > stepBack

  TerminationSet
    SpriteCounter stype=goal win=True
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(push_game, box_level)  