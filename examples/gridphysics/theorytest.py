level="""
000000000
0  G  A 0
0    2  0
0 3  0 00
0 O  0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		poison > Immovable color=BROWN
		box1 > Passive color=ORANGE
		goal > Passive color=ORANGE
		box2 > Immovable color=BLUE
		oldGl > Passive color=GOLD
		wall > Resource color=BLACK
	InteractionSet
		box1 avatar > killSprite
		goal avatar > killSprite
		poison avatar > killSprite
		wall avatar > killSprite
		oldGl avatar > killSprite
		box2 avatar > killSprite
		avatar wall > stepBack
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		G > goal
		0 > wall
		2 > poison
		A > avatar
		O > oldGl
		1 > box1
		3 > box2
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
