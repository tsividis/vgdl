level="""
000000000
0   1   0
0       0
0  A  G 2
000000000
"""
game = """
BasicGame
	SpriteSet
		laog > Passive color=LIGHTRED
		goal > Passive color=LIGHTRED
		wall > Immovable color=DARKGRAY
		avatar > MovingAvatar color=DARKBLUE
		c3 > Resource color=GREEN
		c2 > ResourcePack color=LIGHTBLUE
		c5 > Resource color=GOLD
		c4 > ResourcePack color=BLACK
	InteractionSet
		c2 avatar > killSprite
		c4 EOS > stepBack
		c2 c4 > stepBack
		c5 EOS > stepBack
		c5 avatar > bounceForward
		avatar c4 > stepBack
		avatar EOS > stepBack
		c3 c4 > stepBack
		c2 EOS > stepBack
		c5 c4 > stepBack
		c3 EOS > stepBack
		c3 avatar > killSprite
		goal avatar > killSprite
		avatar EOS > stepBack
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		A > avatar
		2 > c3
		0 > c4
		1 > c5
		3 > c2
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
