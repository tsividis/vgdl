level="""
22222222222222222222222222
21          0        0   2
2       0    0           2
2     0          0       2
2  0         0    c      2
2          0          0  2
2   0          0         2
2      d           0     2
2                        2
22222222222222222222222222
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=BLACK
		c9 > Resource color=RED
		c8 > Resource color=ORANGE
		avatar > MovingAvatar color=WHITE
		c2 > Resource color=GREEN
		c13 > ResourcePack color=GOLD
		c12 > Resource color=PURPLE
		c11 > ResourcePack color=LIGHTGREEN
		c10 > Resource color=LIGHTORANGE
		c7 > Resource color=YELLOW
		c6 > Resource color=BLUE
		c5 > Resource color=LIGHTBLUE
		c4 > ResourcePack color=PINK
	InteractionSet
		c2 avatar > killSprite
		c11 avatar > killSprite
		c4 c2 > killSprite
		c2 c4 > killSprite
		c5 EOS > stepBack
		c10 c2 > killSprite
		c2 c10 > killSprite
		c6 avatar > killSprite
		c12 EOS > stepBack
		c8 EOS > stepBack
		c5 c3 > killSprite
		c3 c5 > killSprite
		c4 c3 > killSprite
		c3 c4 > killSprite
		c12 avatar > killSprite
		c5 c2 > killSprite
		c2 c5 > killSprite
		c9 c3 > killSprite
		c3 c9 > killSprite
		c4 EOS > stepBack
		c10 c3 > killSprite
		c3 c10 > killSprite
		c7 avatar > killSprite
		c8 c2 > killSprite
		c2 c8 > killSprite
		c12 c2 > killSprite
		c2 c12 > killSprite
		c13 c3 > killSprite
		c3 c13 > killSprite
		avatar c3 > stepBack
		c13 avatar > killSprite
		c11 EOS > stepBack
		c6 c2 > killSprite
		c2 c6 > killSprite
		c8 c3 > killSprite
		c3 c8 > killSprite
		c7 c3 > killSprite
		c3 c7 > killSprite
		c9 c2 > killSprite
		c2 c9 > killSprite
		c12 c3 > killSprite
		c3 c12 > killSprite
		c2 c2 > killSprite
		c7 EOS > stepBack
		c13 c2 > killSprite
		c2 c13 > killSprite
		c10 EOS > stepBack
		c3 c3 > killSprite
		c3 EOS > stepBack
		c7 c2 > killSprite
		c2 c7 > killSprite
		c8 avatar > killSprite
		c11 c3 > killSprite
		c3 c11 > killSprite
		c6 c3 > killSprite
		c3 c6 > killSprite
		c10 avatar > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c6 EOS > stepBack
		c5 avatar > killSprite
		c4 avatar > killSprite
		c2 EOS > stepBack
		c13 EOS > stepBack
		c9 avatar > killSprite
		c9 EOS > stepBack
		c11 c2 > killSprite
		c2 c11 > killSprite
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c2 win=True
		NoveltyTermination s1=c4 s2=c3 win=True
		NoveltyTermination s1=c5 s2=avatar win=True
		NoveltyTermination s1=c5 s2=c2 win=True
		NoveltyTermination s1=c5 s2=c3 win=True
		NoveltyTermination s1=c6 s2=avatar win=True
		NoveltyTermination s1=c6 s2=c2 win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		NoveltyTermination s1=c7 s2=avatar win=True
		NoveltyTermination s1=c7 s2=c2 win=True
		NoveltyTermination s1=c7 s2=c3 win=True
		NoveltyTermination s1=c8 s2=avatar win=True
		NoveltyTermination s1=c8 s2=c2 win=True
		NoveltyTermination s1=c8 s2=c3 win=True
		NoveltyTermination s1=c9 s2=avatar win=True
		NoveltyTermination s1=c9 s2=c2 win=True
		NoveltyTermination s1=c9 s2=c3 win=True
		NoveltyTermination s1=c10 s2=c2 win=True
		NoveltyTermination s1=c10 s2=c3 win=True
		NoveltyTermination s1=c11 s2=c2 win=True
		NoveltyTermination s1=c11 s2=c3 win=True
		NoveltyTermination s1=c12 s2=avatar win=True
		NoveltyTermination s1=c12 s2=c2 win=True
		NoveltyTermination s1=c12 s2=c3 win=True
		NoveltyTermination s1=c13 s2=avatar win=True
		NoveltyTermination s1=c13 s2=c2 win=True
		NoveltyTermination s1=c13 s2=c3 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c2 limit=0 win=True
	LevelMapping
		4 > c6
		7 > c4
		d > c13
		8 > c5
		c > c12
		3 > c7
		9 > c11
		b > c10
		2 > c3
		6 > c8
		0 > c2
		1 > avatar
		5 > c9
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
