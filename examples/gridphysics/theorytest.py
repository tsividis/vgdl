level="""
3333333333333333333
3                 3
3                 3
3                 3
3                 3
3                 3
3       5         3
3   1  45 2       3
3333333333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MarioAvatar color=WHITE
		c3 > ResourcePack color=GREEN
		c2 > ResourcePack color=BLACK
		c5 > ResourcePack color=GOLD
		c4 > ResourcePack color=RED
	InteractionSet
		c3 c5 > nothing
		c5 c3 > nothing
		c2 c5 > nothing
		c5 c2 > nothing
		c4 c5 > nothing
		c5 c4 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c2 c2 > nothing
		c5 avatar > killSprite
		c3 c3 > nothing
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c5 c5 > nothing
		c4 avatar > killSprite
		avatar c2 > wallStop
		c4 c4 > nothing
		c3 avatar > killSprite
		c4 EOS > stepBack
		c5 EOS > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c5 s2=avatar win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		1 > c5
		3 > c2
		2 > c3
		4 > avatar
		5 > c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
