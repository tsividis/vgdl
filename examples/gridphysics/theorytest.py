level="""
3333333333333333333
3                 3
3                 3
3                 3
3                13
3   2          0033
3  333         0  3
3              0  3
3              0  3
3              0  3
3              0  3
3              0  3
3              0  3
3              0  3
3              0  3
3333333333333333333
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=BLACK
		c2 > ResourcePack color=BLUE
		avatar > MarioAvatar color=WHITE
		c4 > ResourcePack color=GREEN
	InteractionSet
		c2 avatar > killSprite
		c2 c4 > nothing
		c4 c2 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c2 c2 > nothing
		c3 c3 > nothing
		avatar EOS > stepBack
		avatar c3 > killIfTooFast speed=20
		avatar c3 > wallStop
		c4 avatar > killSprite
		c4 c4 > nothing
		c3 c4 > nothing
		c4 c3 > nothing
		c4 EOS > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c2
		3 > c3
		2 > avatar
		1 > c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
