level="""
1111111111111
1 0         1
1           1
1      333331
1    A  G  21
1111111111111
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=WHITE
		c2 > Resource color=BROWN
		goal > Resource color=BROWN
		c5 > ResourcePack color=GOLD
		c4 > ResourcePack color=BLACK
	InteractionSet
		c4 EOS > stepBack
		goal c4 > stepBack
		c5 EOS > stepBack
		c5 avatar > killSprite
		c4 avatar > killSprite
		c3 c4 > stepBack
		goal EOS > stepBack
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
		3 > c2
		0 > c3
		1 > c4
		2 > c5
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
