level="""
000000000000000000
0A 1    3        0
0    4    3      0
0 3       0  0 G00
0    0 1     0  00
000000000000000000
"""
game = """
BasicGame
	SpriteSet
		laog > ResourcePack color=GOLD
		goal > ResourcePack color=GOLD
		wall > Immovable color=BLACK
		poison > ResourcePack color=BROWN
		missile > Missile color=RED
		score > Resource color=PINK
		avatar > MovingAvatar color=DARKBLUE
		box1 > ResourcePack color=GREEN
		box2 > ResourcePack color=LIGHTBLUE
	InteractionSet
		avatar wall > stepBack
		missile wall > reverseDirection
		poison avatar > killSprite
		avatar poison > killSprite
		goal avatar > killSprite
		box1 avatar > bounceForward
		box2 avatar > killSprite
		goal box1 > bounceForward
		goal box2 > bounceForward
		goal wall > undoAll
		goal poison > undoAll
		box1 wall > undoAll
		box2 wall > undoAll
		box1 poison > undoAll
		box2 poison > undoAll
		goal avatar > killSprite
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		4 > box2
		2 > laog
		3 > poison
		A > avatar
		1 > box1
		0 > wall
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
