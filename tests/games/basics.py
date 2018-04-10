from tests.locals import *
# These games will test mostly interactions
# None of the other objects should be moving

level1 ="""
wwwwwwwwwwwww
w           w
w           w
w       b   w
w       b   w
w       A   w
wwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwww
w           w
w           w
w       b   w
w       b   w
w       A   w
wwwwwwwwwwwww
"""
'''
stepBack
killSprite
bounceForward
~~cloneSprite~~
~~transformTo~~


flipDirection
reverseDirection


'''

# Win the game when you destroy all the boxes

sSet = """
SpriteSet
    box    > Immovable color=WHITE 
    avatar  > MovingAvatar color=DARKBLUE speed=1
    wall > Immovable color=DARKGRAY
LevelMapping
    A > avatar
    b > box
"""

iSet = """
InteractionSet
    avatar wall > stepBack
    box avatar > killSprite

    wall avatar > stepBack
    wall box > stepBack

    box wall > stepBack
    # avatar box > stepBack
    # box avatar > stepBack

"""
tSet1 = """
TerminationSet
    SpriteCounter stype=box limit=0 win=True
    SpriteCounter stype=avatar limit=0 win=False
"""

# Don't win the game when you destroy all the boxes
tSet2 = """
TerminationSet
    # SpriteCounter stype=box limit=0 win=True
    SpriteCounter stype=avatar limit=0 win=False
"""

'''
You can piece together a full game description this way.
Place in as many or as few combinations of sets as you want.
'''
game1 = catDescriptions(sSet, iSet, tSet1)
game2 = catDescriptions(sSet, iSet, tSet2)

# print game1

test1 = TestCase(game1, level1, [[K_UP, K_UP]])
test2 = TestCase(game1, level1, [[K_UP, K_RIGHT, K_RIGHT]])
test3 = TestCase(game1, level1, [[K_UP]])

test4 = TestCase(game2, level1, [[K_UP, K_UP]])