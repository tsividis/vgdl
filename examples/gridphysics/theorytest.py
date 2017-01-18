level="""
000000000
0       0
0    3  0
0 2  0A00
0    0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		poison > Passive color=BROWN
		box1 > Passive color=ORANGE
		goal > Passive color=ORANGE
		oldGoal > Immovable color=GOLD
		box2 > Immovable color=RED
		wall > Passive color=BLACK
	InteractionSet
		wall avatar > bounceForward
		poison avatar > killSprite
		avatar poison > killSprite
		box1 avatar > killSprite
		box2 avatar > killSprite
		goal avatar > killSprite
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		G > goal
		0 > wall
		2 > poison
		O > oldGoal
		1 > box1
		3 > box2
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
