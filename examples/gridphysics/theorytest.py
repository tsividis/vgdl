level="""
33333333333333333333333333
3                        3
3        1     0         3
3                 0 000003
3                 0      3
3                0    2  3
3  1              000000 3
3       0     1  1       3
3  0       1             3
33333333333333333333333333
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=GREEN
		c2 > Resource color=ORANGE
		avatar > MovingAvatar color=WHITE
		c4 > ResourcePack color=BLACK
	InteractionSet
		avatar c2 > killSprite
		c4 EOS > stepBack
		c2 c4 > killSprite
		c4 c2 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c2 c2 > killSprite
		c3 c3 > killSprite
		c3 avatar > killSprite
		c2 EOS > stepBack
		avatar c4 > stepBack
		c3 EOS > stepBack
		c4 c4 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c3 limit=0 win=True
	LevelMapping
		0 > c2
		3 > c4
		2 > avatar
		1 > c3
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
