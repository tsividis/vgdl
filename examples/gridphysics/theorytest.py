level="""
000000000000000000
0    1  2        0
0         2      0
0 2  A    3  0G 00
0    0 1     0  00
000000000000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		box1 > ResourcePack color=GREEN
		poison > Immovable color=BROWN
		box2 > Resource color=LIGHTBLUE
		goal > Passive color=GOLD
		wall > Immovable color=BLACK
	InteractionSet
		poison avatar > killSprite
		wall avatar > killSprite
		goal avatar > killSprite
		goal avatar > killSprite
		box2 avatar > killSprite
		avatar poison > killSprite
		box1 avatar > bounceForward
		avatar wall > stepBack
		box1 wall > undoAll
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
