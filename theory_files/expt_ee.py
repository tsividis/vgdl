level="""
44444444444444444444444444
4                        4
4                1       4
4      0     6           4
4444                     4
4 64                 6   4
4444       6             4
4 3            1         4
4                    0   4
44444444444444444444444444
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=GREEN
		c2 > ResourcePack color=DARKGRAY
		c5 > ResourcePack color=LIGHTBLUE
		c4 > ResourcePack color=PINK
	InteractionSet
		avatar c2 > stepBack
		c5 c2 > nothing
		c4 c2 > nothing
		c2 c3 > nothing
		c2 c2 > nothing
		c5 avatar > killSprite
		c3 c3 > nothing
		avatar EOS > stepBack
		c4 c3 > nothing
		c4 avatar > killSprite
		c5 c3 > nothing
		c3 avatar > killSprite
		c4 EOS > stepBack
		c5 EOS > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c3 limit=0 win=True
	LevelMapping
		0 > c4
		1 > c5
		3 > avatar
		4 > c2
		6 > c3
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
