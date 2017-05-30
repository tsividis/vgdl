level="""
3333333333333333333333
3                    3
3         0          3
3            1       3
3           5        3
3          2         3
3   0    4           3
3                    3
3                    3
3333333333333333333333
"""
game = """
BasicGame
	SpriteSet
		c8 > Resource color=PINK
		avatar > MovingAvatar color=WHITE
		c3 > ResourcePack color=ORANGE
		c2 > Resource color=BLUE
		c7 > Resource color=PURPLE
		c6 > ResourcePack color=RED
		c5 > ResourcePack color=YELLOW
		c4 > ResourcePack color=BLACK
	InteractionSet
		c2 avatar > bounceForward
		c8 c2 > killSprite
		c2 c8 > killSprite
		c3 c5 > stepBack
		c5 EOS > stepBack
		c6 avatar > transformTo stype=c5
		c4 c5 > killSprite
		c5 c4 > killSprite
		c8 EOS > stepBack
		c3 c4 > stepBack
		c2 c5 > killSprite
		c5 c2 > killSprite
		c4 EOS > stepBack
		avatar c7 > stepBack
		c2 c4 > stepBack
		c7 c5 > killSprite
		c3 avatar > bounceForward
		c8 c4 > killSprite
		c4 c8 > killSprite
		c8 c5 > killSprite
		c5 c8 > killSprite
		c2 c6 > stepBack
		c8 c3 > killSprite
		c3 c8 > killSprite
		c6 c4 > killSprite
		c4 c6 > killSprite
		c3 c7 > transformTo stype=c5
		c2 c2 > stepBack
		c6 c5 > killSprite
		c5 c6 > killSprite
		c7 EOS > stepBack
		c3 c3 > stepBack
		c3 EOS > stepBack
		c2 c7 > stepBack
		c8 avatar > transformTo stype=c3
		c7 c4 > killSprite
		c4 c7 > killSprite
		c6 c3 > killSprite
		c3 c6 > killSprite
		c3 c2 > stepBack
		c6 EOS > stepBack
		avatar c5 > stepBack
		avatar c4 > stepBack
		c5 c5 > killSprite
		c2 EOS > stepBack
		c4 c4 > killSprite
	TerminationSet
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		NoveltyTermination s1=c6 s2=c4 win=True
		NoveltyTermination s1=c6 s2=c5 win=True
		NoveltyTermination s1=c7 s2=c4 win=True
		NoveltyTermination s1=c8 s2=c2 win=True
		NoveltyTermination s1=c8 s2=c3 win=True
		NoveltyTermination s1=c8 s2=c4 win=True
		NoveltyTermination s1=c8 s2=c5 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c2 limit=0 win=True
	LevelMapping
		0 > c2
		8 > c7 c5
		7 > avatar c5
		b > avatar c3
		1 > c7
		2 > c5
		3 > c4
		9 > c8
		4 > c3
		5 > avatar
		6 > c6
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
