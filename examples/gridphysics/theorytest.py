level="""
000000000
0  A    0
0    3  0
0 2  0O00
0    0 00
00000G000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		poison > Passive color=BROWN
		box1 > Resource color=ORANGE
		oldGoal > Resource color=GOLD
		box2 > ResourcePack color=RED
		wall > Passive color=BLACK
		goal > Passive color=BLACK
	InteractionSet
		wall avatar > bounceForward
		box2 avatar > bounceForward
		goal avatar > bounceForward
		poison avatar > killSprite
		avatar poison > killSprite
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
