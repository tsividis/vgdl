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
		c3 > Resource color=BROWN
		c2 > Passive color=ORANGE
		c6 > Immovable color=RED
		c5 > ResourcePack color=GOLD
		c4 > Immovable color=BLACK
	InteractionSet
		c3 avatar > bounceForward
		c4 avatar > bounceForward
		c5 avatar > bounceForward
		c6 avatar > bounceForward
		c2 avatar > killSprite
	TerminationSet

	LevelMapping
		2 >c5
		0 >c4
		3 >c3
		A >avatar
		1 >c2
		4 >c6
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
