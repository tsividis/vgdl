level="""
000000000000000000
0  1    2        0
0    G    2      0
0A2       3  0O 00
0    01      0  00
000000000000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		box1 > Passive color=GREEN
		box2 > Passive color=LIGHTBLUE
		goal > Passive color=LIGHTBLUE
		poison > ResourcePack color=BROWN
		oldGl > ResourcePack color=GOLD
		wall > Resource color=BLACK
	InteractionSet
		box2 avatar > killSprite
		box1 avatar > killSprite
		wall avatar > killSprite
		goal avatar > killSprite
		poison avatar > killSprite
		avatar poison > killSprite
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
