level="""
000000000
0  1    0
0    G  0
0A2  0O00
0    0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		box2 > Passive color=BLUE
		goal > Passive color=BLUE
		box1 > Immovable color=ORANGE
		poison > Resource color=BROWN
		oldGl > Resource color=GOLD
		wall > Passive color=BLACK
	InteractionSet
		box1 avatar > killSprite
		box2 avatar > killSprite
		goal avatar > killSprite
		wall avatar > killSprite
		oldGl avatar > killSprite
		poison avatar > killSprite
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
