level="""
000000000
0  1    0
0    3  0
0    0O00
0    0 00
00G000000
"""
game = """
BasicGame
	SpriteSet
		avatar > ontology.MovingAvatar color=DARKBLUE
		poison > core.Resource color=BROWN
		box1 > ontology.ResourcePack color=ORANGE
		oldGoal > ontology.AStarChaser color=GOLD
		box2 > core.Resource color=RED
		wall > core.Resource color=BLACK
		goal > core.Resource color=BLACK
	InteractionSet
		box1 avatar > bounceForward
		wall avatar > bounceForward
		box2 avatar > bounceForward
		goal avatar > bounceForward
		poison avatar > killSprite
		avatar poison > killSprite
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
