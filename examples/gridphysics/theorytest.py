level="""
000000000
0  1    0
0    3  0
0    0G00
0    0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		poison > Resource color=BROWN
		box1 > Immovable color=ORANGE
		box2 > Passive color=RED
		goal > Resource color=GOLD
		wall > Immovable color=BLACK
	InteractionSet
		box1 avatar > bounceForward
		wall avatar > bounceForward
		goal avatar > bounceForward
		box2 avatar > bounceForward
		poison avatar > killSprite
		avatar poison > killSprite
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		0 > wall
		1 > box1
		G > goal
		2 > poison
		3 > box2
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
