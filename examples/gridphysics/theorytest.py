level="""
000000000000000000
0    1  2        0
0         2      0
0 2       A  0G 00
0    0  1    0  00
000000000000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		box1 > ResourcePack color=GREEN
		wall > Immovable color=BLACK
		box2 > Resource color=LIGHTBLUE
		goal > Immovable color=GOLD
		poison > Passive color=BROWN
	InteractionSet
		wall avatar > killSprite
		poison avatar > killSprite
		goal avatar > killSprite
		goal avatar > killSprite
		box2 avatar > killSprite
		avatar wall > stepBack
		avatar poison > killSprite
		box1 avatar > bounceForward
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		G > goal
		0 > wall
		2 > poison
		O > oldGl
		1 > box1
		3 > box2
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
