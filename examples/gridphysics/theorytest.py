level="""
1111111111111
1 0         1
1           1
1      444441
1 A     4  G1
1111111111111
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=WHITE
		c2 > Resource color=BROWN
		c5 > Resource color=GOLD
		goal > Resource color=GOLD
		c4 > Resource color=BLACK
	InteractionSet
		c2 avatar > killSprite
		c4 EOS > stepBack
		c2 c4 > stepBack
		goal EOS > stepBack
		c4 avatar > killSprite
		c3 c4 > stepBack
		c2 EOS > stepBack
		goal c4 > stepBack
		c3 EOS > stepBack
		c3 avatar > killSprite
		goal avatar > killSprite
		avatar EOS > stepBack
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		4 > c2
		2 > c5
		A > avatar
		1 > c4
		0 > c3
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
