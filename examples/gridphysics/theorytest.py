level="""
000000000
0  1    0
0    3  0
0 4  0A00
0 2  0 00
00G000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > Immovable color=BROWN
		c2 > ResourcePack color=BLUE
		c6 > ResourcePack color=ORANGE
		c5 > Resource color=GOLD
		c4 > ResourcePack color=BLACK
		goal > ResourcePack color=BLACK
	InteractionSet
		c2 avatar > killSprite
		c3 avatar > killSprite
		c4 avatar > killSprite
		goal avatar > killSprite
		c5 avatar > killSprite
		c6 avatar > killSprite
		avatar c4 > stepBack
		avatar goal > stepBack
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		4 > c2
		3 > c3
		2 > c5
		A > avatar
		0 > c4
		1 > c6
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
