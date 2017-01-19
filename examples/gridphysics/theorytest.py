level="""
000000000000000000
0    1  2        0
0    3    2     A0
0 2       3  0G 00
0    01      0  00
000000000000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		box1 >  color=GREEN
		box2 > Immovable color=LIGHTBLUE
		poison > Passive color=BROWN
		goal > Passive color=GOLD
		wall > Passive color=BLACK
	InteractionSet
		box2 avatar > killSprite
		wall avatar > killSprite
		goal avatar > killSprite
		poison avatar > killSprite
		avatar poison > killSprite
		box1 avatar > bounceForward
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
