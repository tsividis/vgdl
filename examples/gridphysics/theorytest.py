level="""
22222222222222222222222222
20   3      4   5    6 3 2
2   1   7       3        2
2           5    6       2
21      3    4           2
2     8             7    2
2   6    7     8         2
2         5    6      8  2
2   4 8   4    5 3 7     2
22222222222222222222222222
"""
game = """
BasicGame
	SpriteSet
		c9 > Resource color=RED
		c8 > ResourcePack color=ORANGE
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=BLACK
		c2 > Resource color=GREEN
		c7 > ResourcePack color=PINK
		c6 > Resource color=YELLOW
		c5 > Resource color=LIGHTBLUE
		c4 > ResourcePack color=BLUE
	InteractionSet
		c2 avatar > killSprite
		c4 c2 > killSprite
		c2 c4 > killSprite
		c5 EOS > stepBack
		c6 avatar > killSprite
		c8 EOS > stepBack
		c5 c3 > killSprite
		c3 c5 > killSprite
		c4 c3 > killSprite
		c3 c4 > killSprite
		c5 c2 > killSprite
		c2 c5 > killSprite
		c9 c3 > killSprite
		c3 c9 > killSprite
		c4 EOS > stepBack
		c7 avatar > killSprite
		c8 c2 > killSprite
		c2 c8 > killSprite
		avatar c3 > stepBack
		c6 c2 > killSprite
		c2 c6 > killSprite
		c8 c3 > killSprite
		c3 c8 > killSprite
		c7 c3 > killSprite
		c3 c7 > killSprite
		c9 c2 > killSprite
		c2 c9 > killSprite
		c2 c2 > killSprite
		c7 EOS > stepBack
		c3 c3 > killSprite
		c3 EOS > stepBack
		c7 c2 > killSprite
		c2 c7 > killSprite
		c8 avatar > killSprite
		c6 c3 > killSprite
		c3 c6 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c6 EOS > stepBack
		c5 avatar > killSprite
		c4 avatar > killSprite
		c2 EOS > stepBack
		c9 avatar > killSprite
		c9 EOS > stepBack
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
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c2 limit=0 win=True
	LevelMapping
		4 > c4
		7 > c7
		8 > c5
		0 > avatar
		3 > c6
		2 > c3
		6 > c8
		1 > c2
		5 > c9
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
