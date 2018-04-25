from tests.locals import *


base_game = """
BasicGame
	SpriteSet
		wall > Immovable color=DARKGRAY
		avatar  > MovingAvatar color=DARKBLUE
		box1 > ResourcePack color=WHITE
		box2 > ResourcePack color=GREEN
		box3 > ResourcePack color=YELLOW
		box4 > ResourcePack color=PURPLE
		box5 > ResourcePack color=BLUE

	LevelMapping
		1 > box1
		2 > box2
		3 > box3
		4 > box4
		5 > box5
		w > wall
		A > avatar

	InteractionSet

		box1 avatar > bounceForward
		box1 box2 > stepBack
		box1 box3 > killSprite
		box4 box1 > bounceForward
		box5 box1 > killSprite
		avatar wall > stepBack

		box1 wall > stepBack
		box4 wall > stepBack

	TerminationSet
		SpriteCounter stype=box5 limit=0 win=True
		SpriteCounter stype=avatar limit=0 win=False
		Termination
"""

base_level = """
wwwwwwwwwww
w 222 444 w
w 2 1A1 4 w
w 3 1 1 5 w
w 333 555 w
wwwwwwwwwww
"""

level2 = """
wwwwwwwwwww
w         w
w   A 1 4 w
w         w
w         w
wwwwwwwwwww

"""

action_sequences = [[K_LEFT, K_LEFT, K_RIGHT, K_RIGHT, K_RIGHT, K_LEFT, K_DOWN, K_DOWN, K_LEFT, K_LEFT, K_LEFT]]*2

test_case = TestCase(base_game, base_level, action_sequences)

as2 = [[K_RIGHT]*4]*2
test_case2 = TestCase(base_game, level2, as2)
"""
K_LEFT
wwwwwwwwwww
w 222 444 w
w 2 1A1 4 w
w 3 1 1 5 w
w 333 555 w
wwwwwwwwwww
9.328s 

K_LEFT
wwwwwwwwwww
w 222 444 w
w 21A 1 4 w
w 3 1 1 5 w
w 333 555 w
wwwwwwwwwww
0.383

K_RIGHT
wwwwwwwwwww
w 222 444 w
w 21 A1 4 w
w 3 1 1 5 w
w 333 555 w
wwwwwwwwwww
0.28

K_RIGhT
wwwwwwwwwww
w 222 444 w
w 21  A14 w
w 3 1 1 5 w
w 333 555 w
wwwwwwwwwww
0.166

K_RIGHT
wwwwwwwwwww
w 222 444 w
w 21   A14w
w 3 1 1 5 w
w 333 555 w
wwwwwwwwwww
148.216

K_LEFT
wwwwwwwwwww
w 222 444 w
w 21  A 14w
w 3 1 1 5 w
w 333 555 w
wwwwwwwwwww
3.452

K_DOWN
wwwwwwwwwww
w 222 444 w
w 21    14w
w 3 1 A 5 w
w 333 155 w
wwwwwwwwwww
104.065

K_DOWN
wwwwwwwwwww
w 222 444 w
w 21    14w
w 3 1 A 5 w
w 333 155 w
wwwwwwwwwww
1.984

K_LEFT
wwwwwwwwwww
w 222 444 w
w 21    14w
w 3 1A  5 w
w 333 155 w
wwwwwwwwwww
2.221


K_LEFT
wwwwwwwwwww
w 222 444 w
w 21    14w
w 31A   5 w
w 333 155 w
wwwwwwwwwww
2.156


K_LEFT
wwwwwwwwwww
w 222 444 w
w 21    14w
w 3A    5 w
w 333 155 w
wwwwwwwwwww
34.015





"""