level="""
000000000
0     1 0
0    A  0
0 2  0G00
0    0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		wall > Immovable color=BLACK
		box1 > ResourcePack color=GREEN
		box2 > Immovable color=LIGHTBLUE
		goal > Passive color=GOLD
		poison > ResourcePack color=BROWN
	InteractionSet
		wall avatar > killSprite
		poison avatar > killSprite
		goal avatar > killSprite
		box2 avatar > killSprite
		avatar poison > killSprite
		box1 avatar > bounceForward
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		0 > wall
		1 > box1
		G > goal
		2 > poison
		3 > box2
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
