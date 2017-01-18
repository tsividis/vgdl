level="""
000000000
0       0
0    A  0
0 3  0200
0    0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		poison > RandomNPC color=BROWN
		box1 > Passive color=ORANGE
		box2 > Chaser color=RED
		goal > Missile color=GOLD
		wall > Resource color=BLACK
	InteractionSet
		poison avatar > bounceForward
		wall avatar > bounceForward
		goal avatar > bounceForward
		box1 avatar > killSprite
		box2 avatar > killSprite
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		0 > wall
		1 > box1
		2 > goal
		3 > poison
		4 > box2
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
