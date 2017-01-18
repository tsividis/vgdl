level="""
000000000
0       0
0    G  0
0 2  0O00
0   A0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		poison > Immovable color=BROWN
		box1 > Passive color=ORANGE
		box2 > ResourcePack color=RED
		goal > ResourcePack color=RED
		oldGoal > Passive color=GOLD
		wall > ResourcePack color=BLACK
	InteractionSet
		wall avatar > bounceForward
		goal avatar > bounceForward
		box2 avatar > bounceForward
		poison avatar > stepBack
		avatar poison > stepBack
		box1 avatar > killSprite
		avatar wall > stepBack
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
