level="""
000000000
0  G    0
0    3  0
0A2  0O00
0    0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		poison > ResourcePack color=BROWN
		box1 > AStarChaser color=ORANGE
		goal > AStarChaser color=ORANGE
		oldGoal > Chaser color=GOLD
		box2 > AStarChaser color=RED
		wall > Passive color=BLACK
	InteractionSet
		box1 avatar > bounceForward
		poison avatar > bounceForward
		wall avatar > bounceForward
		box2 avatar > bounceForward
		goal avatar > bounceForward
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
