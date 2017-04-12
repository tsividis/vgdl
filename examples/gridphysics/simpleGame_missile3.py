
level = """
wwwwwwwwwwwww
wA    wvzx  w
w     w     w
wwwpwww     w
w     w     w
wG          w
wwwwwwwwwwwww
"""

game = """
BasicGame
  SpriteSet         
    wall > Immovable color=BLACK
    goal > Missile speed=.6 orientation=RIGHT color=RED
    avatar > MovingAvatar color=DARKBLUE
    box1 > Resource color=ORANGE
    box2 > Resource color=PINK
    box3 > Resource color=LIGHTBLUE
  LevelMapping
    w > wall       
    G > goal
    v > box1
    z > box2
    x > box3
  InteractionSet
    goal avatar > killSprite
    goal wall > killSprite
    goal EOS > wrapAround
    avatar bullet > killSprite
    avatar EOS > stepBack
    avatar wall > stepBack
    box1 avatar > killSprite
    box2 avatar > killSprite
    box3 avatar > killSprite
  TerminationSet
    SpriteCounter stype=goal win=True
    SpriteCounter stype=avatar win=False
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)  