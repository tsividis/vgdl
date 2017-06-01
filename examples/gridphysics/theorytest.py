level="""
22222222222222222222222222222222
2  0                           2
2     0            0      0    2
2       0                      2
2               0              2
2         4    5   3           2
2     0     0            1111112
2     0   0              1     2
222                  0   1     2
22222222222222222222222222222222
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=DARKGRAY
		c2 > ResourcePack color=PINK
		c6 > ResourcePack color=PURPLE
		c5 > Chaser color=LIGHTGREEN fleeing=False stype=c4
		c4 > Resource color=YELLOW
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c2 c4 > killSprite
		c5 EOS > stepBack
		c6 avatar > killSprite
		c4 c5 > killSprite
		avatar c3 > stepBack
		c2 c5 > killSprite
		c5 c2 > killSprite
		c4 EOS > stepBack
		c4 c3 > stepBack
		c6 c2 > killSprite
		c2 c6 > killSprite
		c6 c4 > killSprite
		c4 c6 > killSprite
		c2 c2 > killSprite
		c6 c5 > killSprite
		c5 c6 > killSprite
		c3 c3 > killSprite
		c3 EOS > stepBack
		c6 c3 > killSprite
		c3 c6 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c6 EOS > stepBack
		avatar c5 > nothing
		c4 avatar > bounceForward
		c5 c5 > killSprite
		c2 EOS > stepBack
		c2 avatar > killSprite
		c4 c4 > killSprite
		c3 avatar > killSprite
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c6 s2=avatar win=True
		NoveltyTermination s1=c6 s2=c2 win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		NoveltyTermination s1=c6 s2=c4 win=True
		NoveltyTermination s1=c6 s2=c5 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=False
		SpriteCounter stype=c2 limit=0 win=True
	LevelMapping
		0 > c2
		1 > c6
		2 > c3
		3 > c4
		4 > c5
		5 > avatar
		8 > avatar c5
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
