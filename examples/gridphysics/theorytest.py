level="""
000000000
0  1    0
0  G 3  0
0 4  0A00
0 2  0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > Resource color=BROWN
		c2 > Resource color=ORANGE
		c6 > Passive color=BLUE
		c5 > Passive color=GOLD
		c4 > Resource color=BLACK
		goal > Passive color=LIGHTRED
	InteractionSet
		c2 avatar > killSprite
		c3 avatar > killSprite
		c4 avatar > killSprite
		c5 avatar > killSprite
		c6 avatar > killSprite
		goal avatar > killSprite
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		4 > c6
		3 > c3
		2 > c5
		A > avatar
		0 > c4
		1 > c2
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
