level="""
000000000
0  1    0
0    2  0
0 3  0A00
0 G  0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		poison > Immovable color=BROWN
		box1 > Immovable color=ORANGE
		box2 > Immovable color=BLUE
		goal > Resource color=GOLD
		wall > Resource color=BLACK
	InteractionSet
		poison avatar > killSprite
		wall avatar > killSprite
		goal avatar > killSprite
		goal avatar > killSprite
		box2 avatar > killSprite
		avatar wall > stepBack
		box1 avatar > bounceForward
		avatar poison > killSprite
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
