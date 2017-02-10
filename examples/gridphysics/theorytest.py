level="""
000000000
0  1    0
0    3  0
0 4  0A00
0 G  0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > Passive color=BLUE
		c2 > Immovable color=ORANGE
		c6 > Resource color=BROWN
		c5 > Resource color=GOLD
		goal > Resource color=GOLD
		c4 > Immovable color=BLACK
	InteractionSet
		c3 avatar > killSprite
		c4 avatar > killSprite
		goal avatar > killSprite
		c6 avatar > killSprite
		avatar c4 > stepBack
		avatar c6 > killSprite
		c2 avatar > bounceForward
		c2 c4 > undoAll
		goal avatar > killSprite
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		4 > c3
		3 > c6
		2 > c5
		A > avatar
		0 > c4
		1 > c2
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
