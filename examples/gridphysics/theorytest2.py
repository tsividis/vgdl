level="""
000000000
0  1    0
0  G 3 A0
0 4  0 00
0 2  0 00
000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > Chaser color=BROWN
		c2 > ResourcePack color=ORANGE
		c6 > Chaser color=BLUE
		c5 > Chaser color=GOLD
		c4 > Missile color=BLACK
		goal > Passive color=LIGHTRED
	InteractionSet
		c2 avatar > killSprite
		c3 avatar > killSprite
		c5 avatar > killSprite
		c6 avatar > killSprite
		avatar c4 > stepBack
		avatar c3 > killSprite
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
