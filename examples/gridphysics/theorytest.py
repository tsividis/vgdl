level="""
55555555555555555555555555
5               8    6 4 5
5   7           4        5
5      3         6  4    5
5            2           5
5     0       4  2  1    5
5   6    1     01        5
5         8 8  6      0  5
5   2 0   2    8 4 1     5
55555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		c9 > ResourcePack color=RED
		c8 > ResourcePack color=YELLOW
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=GREEN
		c2 > ResourcePack color=BLACK
		c7 > ResourcePack color=ORANGE
		c6 > ResourcePack color=BLUE
		c5 > ResourcePack color=LIGHTBLUE
		c4 > ResourcePack color=PINK
	InteractionSet
		avatar c2 > stepBack
		c8 c2 > nothing
		c2 c8 > nothing
		c4 c2 > nothing
		c2 c4 > nothing
		c6 avatar > killSprite
		c9 c6 > nothing
		c6 c9 > nothing
		c9 c7 > nothing
		c7 c9 > nothing
		c9 c5 > nothing
		c5 c9 > nothing
		c5 c3 > nothing
		c3 c5 > nothing
		c4 c3 > nothing
		c3 c4 > nothing
		c5 c2 > nothing
		c2 c5 > nothing
		c9 c3 > nothing
		c3 c9 > nothing
		c7 avatar > killSprite
		c8 c6 > nothing
		c6 c8 > nothing
		c7 c5 > nothing
		c5 c7 > nothing
		avatar EOS > stepBack
		c3 avatar > killSprite
		c8 c4 > nothing
		c4 c8 > nothing
		c8 c5 > nothing
		c5 c8 > nothing
		c6 c2 > nothing
		c2 c6 > nothing
		c8 c3 > nothing
		c3 c8 > nothing
		c6 c4 > nothing
		c4 c6 > nothing
		c7 c3 > nothing
		c3 c7 > nothing
		c9 c2 > nothing
		c2 c9 > nothing
		c2 c2 > nothing
		c6 c5 > nothing
		c5 c6 > nothing
		c3 c3 > nothing
		c8 c7 > nothing
		c7 c8 > nothing
		c7 c2 > nothing
		c2 c7 > nothing
		c8 avatar > killSprite
		c7 c4 > nothing
		c4 c7 > nothing
		c6 c3 > nothing
		c3 c6 > nothing
		c9 c4 > nothing
		c4 c9 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		avatar c5 > stepBack
		c4 avatar > killSprite
		c9 avatar > killSprite
		c5 EOS > stepBack
		c8 EOS > stepBack
		c4 EOS > stepBack
		c7 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c2 EOS > stepBack
		c9 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c4 s2=c2 win=True
		NoveltyTermination s1=c4 s2=c3 win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c5 s2=c2 win=True
		NoveltyTermination s1=c5 s2=c3 win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c6 s2=c5 win=True
		NoveltyTermination s1=c6 s2=c4 win=True
		NoveltyTermination s1=c6 s2=c2 win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		NoveltyTermination s1=c7 s2=EOS win=True
		NoveltyTermination s1=c7 s2=c5 win=True
		NoveltyTermination s1=c7 s2=c4 win=True
		NoveltyTermination s1=c7 s2=c2 win=True
		NoveltyTermination s1=c7 s2=c3 win=True
		NoveltyTermination s1=c8 s2=avatar win=True
		NoveltyTermination s1=c8 s2=EOS win=True
		NoveltyTermination s1=c8 s2=c5 win=True
		NoveltyTermination s1=c8 s2=c4 win=True
		NoveltyTermination s1=c8 s2=c6 win=True
		NoveltyTermination s1=c8 s2=c7 win=True
		NoveltyTermination s1=c8 s2=c2 win=True
		NoveltyTermination s1=c8 s2=c3 win=True
		NoveltyTermination s1=c9 s2=avatar win=True
		NoveltyTermination s1=c9 s2=EOS win=True
		NoveltyTermination s1=c9 s2=c5 win=True
		NoveltyTermination s1=c9 s2=c4 win=True
		NoveltyTermination s1=c9 s2=c6 win=True
		NoveltyTermination s1=c9 s2=c7 win=True
		NoveltyTermination s1=c9 s2=c2 win=True
		NoveltyTermination s1=c9 s2=c3 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c3 limit=0 win=True
		SpriteCounter stype=c7 limit=0 win=True
	LevelMapping
		0 > c4
		1 > c5
		2 > c6
		3 > avatar
		4 > c8
		5 > c2
		6 > c7
		7 > c3
		8 > c9
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
