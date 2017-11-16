'''
Frostbite.

@author: Jake
'''

test_game = """
BasicGame
    SpriteSet    

        igloo_part > Immovable color=WHITE
        igloo > FrostbiteIgloo stype=igloo_part platforms=8
            opened > color=GREEN
            closed > color=BLACK
            

        wall > Immovable color=LIGHTBLUE
        ground    > Immovable color=GRAY speed=0
        moving > Floe trigger=igloo can_switch=False
            ice > 
                blue > color=BLUE
                white > color=WHITE
            
            killWater > color=LIGHTBLUE

        water > Immovable color=LIGHTBLUE


        ground    > Immovable color=WHITE
        land      > Immovable color=LIGHTGRAY
        avatar    > FrostBiteAvatar speed=0.25 strength=20 color=YELLOW

    TerminationSet
        SpriteCounter stype=avatar win=False
        SpriteCounter stype=igloo   win=True 

    ConditionalSet

        SpriteCount stype=igloo_part count=0 op=grt > canActivateSwitch applyto=moving
        SpriteCount stype=igloo_part count=5 > cannotActivateSwitch applyto=moving
        SpriteCount stype=igloo_part count=0 > cannotActivateSwitch applyto=moving

        SpriteCount stype=igloo_part count=5 > transformTo stype=opened applyto=igloo
        SpriteCount stype=blue count=36 > transformTo stype=white applyto=blue
        SpriteCount stype=igloo_part count=5 > transformTo stype=blue applyto=white

    InteractionSet
        moving EOS > wrapAround
        avatar ice > collideFromAbove


        white avatar > triggerOnLanding strigger=igloo
        white avatar > transformToOnLanding stype=blue dim=y

        moving avatar > reverseFloeIfActivated dim=y strigger=igloo
        avatar killWater > killSpriteOnLanding


        opened avatar > killSprite
        avatar ground > collideFromAbove
        avatar wall > stepBack
        avatar  EOS  > killSprite



    LevelMapping
        ~ > water
        G > closed
        H > ground
        N > land
        I > white
        ^ > killWater
    Groups

"""

test_level = """
NNNNNNNNNNNNNNNNNNNNNNNNNNNNN
N                           N
N    A                  G   N
HHHHHHHHHHHHHHHHHHHHHHHHHHHHH
w~~~~~~~~~~~~~~~~~~~~~~~~~~~w
w~~~~~~~~~~~~~~~~~~~~~~~~~~~w
^III^^^III^^^III^^^^^^^^^^^^^
w~~~~~~~~~~~~~~~~~~~~~~~~~~~w
w~~~~~~~~~~~~~~~~~~~~~~~~~~~w
^^^^^^^^^^^^^III^^^III^^^III^
w~~~~~~~~~~~~~~~~~~~~~~~~~~~w
w~~~~~~~~~~~~~~~~~~~~~~~~~~~w
^III^^^III^^^III^^^^^^^^^^^^^
w~~~~~~~~~~~~~~~~~~~~~~~~~~~w
w~~~~~~~~~~~~~~~~~~~~~~~~~~~w
^^^^^^^^^^^^^III^^^III^^^III^
w~~~~~~~~~~~~~~~~~~~~~~~~~~~w
"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(test_game, test_level)
        