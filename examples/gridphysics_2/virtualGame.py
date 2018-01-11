level="""
000000000
0  A    0
0    4  0
0 3  0200
0    0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		poison > ResourcePack color=BROWN
		box1 > Chaser color=ORANGE
		goal > Chaser color=GOLD
		box2 > Chaser color=RED
		wall > Missile color=BLACK
	InteractionSet
		poison avatar > bounceForward
		wall avatar > bounceForward
		box2 avatar > bounceForward
		goal avatar > bounceForward
		box1 avatar > killSprite
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
