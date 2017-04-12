level="""
222222222222222222
2  2    4        2
2  2 7    54     2
2     A2  7  2  22
2    26     G2  22
22222 3    3     2
2   4    3     6 2
2    7       0   2
2        7     1 2
222222222222222222
"""
game = """
BasicGame
	SpriteSet
		laog > Passive color=LIGHTRED
		goal > Passive color=LIGHTRED
		wall > Immovable color=DARKGRAY
		c9 > Immovable color=GRAY
		c8 > Immovable color=BLACK
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=BROWN
		c2 > ResourcePack color=PINK
		c7 > Passive color=GREEN
		c6 > Immovable color=PURPLE
		c5 > Immovable color=LIGHTBLUE
		c4 > Passive color=GOLD
	InteractionSet
		c2 avatar > killSprite
		c3 avatar > killSprite
		c4 avatar > killSprite
		c5 avatar > killSprite
		c6 avatar > killSprite
		c8 avatar > killSprite
		c9 avatar > killSprite
		avatar c8 > stepBack
		avatar c3 > killSprite
		c7 avatar > bounceForward
		c7 c2 > undoAll
		avatar c9 > teleportToExit
		goal avatar > killSprite
		avatar EOS > stepBack
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		3 > c2
		5 > c9
		1 > c4
		4 > c3
		0 > c6
		A > avatar
		2 > c8
		6 > c7
		7 > c5
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
