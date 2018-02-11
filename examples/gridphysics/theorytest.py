level="""
3333333333333333333333
35                   3
3    4    0          3
3              2     3
3                    3
3      2             3
3                 0  3
3          4         3
3                    3
3333333333333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=WHITE
		c3 > ResourcePack color=ORANGE
		c2 > ResourcePack color=BLUE
		c5 > ResourcePack color=YELLOW
		c4 > ResourcePack color=BLACK
	InteractionSet
		c2 avatar > killSprite
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
		c3 c5 > nothing
		c5 c3 > nothing
		c4 c4 > nothing
		c3 avatar > killSprite
		c4 EOS > stepBack
		c5 EOS > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
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
		0 > c2
		2 > c5
		3 > c4
		4 > c3
		5 > avatar
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
