level="""
555555555555555555
5    5  6        5
5  4 5    6      5
53  0     1  5  55
5555554      5  55
55         0     5
5   6    0     4 5
5    1           5
5        1      25
555555555555555555
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=LIGHTBLUE
		c2 > Resource color=PINK
		c7 > ResourcePack color=RED
		c6 > ResourcePack color=BLACK
		c5 > Resource color=GREEN
		c4 > Resource color=GOLD
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c6 c7 > killSprite
		c7 c6 > killSprite
		c2 c4 > killSprite
		c4 c2 > killSprite
		c5 EOS > stepBack
		avatar c6 > stepBack
		c4 c5 > killSprite
		c5 c4 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
		c2 c5 > killSprite
		c4 EOS > stepBack
		c7 avatar > killSprite
		avatar c7 > killSprite
		c5 c7 > killSprite
		c7 c5 > killSprite
		c3 avatar > killSprite
		c2 c6 > killSprite
		c6 c2 > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c3 c7 > killSprite
		c7 c3 > killSprite
		c2 c2 > killSprite
		c5 c6 > undoAll
		c7 EOS > stepBack
		c3 c3 > killSprite
		c3 EOS > stepBack
		c2 c7 > killSprite
		c7 c2 > killSprite
		c4 c7 > killSprite
		c7 c4 > killSprite
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c7 c7 > killSprite
		c6 EOS > stepBack
		c5 avatar > bounceForward
		c4 avatar > killSprite
		c5 c5 > killSprite
		c2 EOS > stepBack
		c2 avatar > killSprite
		avatar c2 > killSprite
		c4 c4 > killSprite
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c2 limit=0 win=False
		SpriteCounter stype=c7 limit=0 win=False
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c6 win=True
		NoveltyTermination s1=c2 s2=c7 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c7 win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		SpriteCounter stype=c3 limit=0 win=True
	LevelMapping
		0 > c2
		1 > c3
		2 > c4
		3 > avatar
		7 > c5 c3
		5 > c6
		4 > c5
		6 > c7
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
