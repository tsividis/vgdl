level="""
4444444444444444444444
4  5    6            4
4    3    6          4
4   2         4     44
4    45       4 4    4
44          2        4
4   6    2      5    4
4             0      4
4                    4
4444444444444444444444
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=LIGHTBLUE
		c2 > ResourcePack color=PINK
		c7 > ResourcePack color=ORANGE
		c6 > ResourcePack color=GREEN
		c5 > ResourcePack color=DARKGRAY
		c4 > ResourcePack color=GOLD
	InteractionSet
		c2 avatar > killSprite
		c6 c7 > killSprite
		c7 c6 > killSprite
		c2 c4 > killSprite
		c4 c2 > killSprite
		c5 EOS > stepBack
		c6 avatar > bounceForward
		c4 c5 > killSprite
		c5 c4 > killSprite
		c3 c5 > killSprite
		c5 c3 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
		c2 c5 > killSprite
		c5 c2 > killSprite
		c4 EOS > stepBack
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
		c5 c6 > killSprite
		c6 c5 > killSprite
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
		avatar c5 > stepBack
		avatar c4 > killSprite
		c5 c5 > killSprite
		c2 EOS > stepBack
		c4 c4 > killSprite
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c2 s2=c6 win=True
		NoveltyTermination s1=c2 s2=c7 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c7 win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c2
		1 > c3
		2 > c4
		3 > avatar
		4 > c5
		5 > c6
		6 > c7
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
