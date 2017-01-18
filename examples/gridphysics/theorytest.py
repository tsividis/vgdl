level="""
000000000
0  A    0
0    G  0
0 2  0O00
0    0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		poison > Resource color=BROWN
		box1 > Resource color=ORANGE
		box2 > Immovable color=RED
		goal > Immovable color=RED
		oldGoal > Passive color=GOLD
		wall > Chaser color=BLACK
	InteractionSet
		poison avatar > bounceForward
		wall avatar > bounceForward
		goal avatar > bounceForward
		box2 avatar > bounceForward
		box1 avatar > killSprite
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
