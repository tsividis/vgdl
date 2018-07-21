level="""
7777777777777777777777
7    9   b    7  7 7 7
7  9 7 b      79  9 77
7 8  7     b  9   99 7
7777777777777777777 77
7   7  b  7 7    7  77
7777 d    7 9 7  7   7
7 c  977 d    7  77 77
7  7  7 7 7   7     77
7777777777777777777777
"""
game = """
BasicGame
	SpriteSet
		c8 > ResourcePack color=ORANGE
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=LIGHTBLUE
		c2 > ResourcePack color=PINK
		c7 > ResourcePack color=GREEN
		c6 > ResourcePack color=DARKGRAY
		c4 > ResourcePack color=GOLD
	InteractionSet
		c2 avatar > killSprite
		avatar c2 > stepBack
		avatar avatar > stepBack
		c2 c4 > nothing
		c4 c2 > nothing
		c4 c8 > nothing
		c8 c4 > nothing
		avatar c6 > stepBack
		c6 avatar > stepBack
		c8 EOS > nothing
		c3 avatar > killSprite
		avatar c3 > stepBack
		c8 c8 > nothing
		c4 EOS > nothing
		c7 avatar > bounceForward
		c2 c8 > nothing
		c8 c2 > nothing
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c6 c8 > nothing
		c8 c6 > nothing
		c2 c6 > nothing
		c6 c2 > nothing
		c3 c8 > nothing
		c8 c3 > nothing
		c4 c6 > nothing
		c6 c4 > nothing
		c7 c3 > reverseDirection
		c2 c2 > nothing
		c7 EOS > nothing
		c3 c3 > nothing
		c8 c7 > killSprite
		c7 c8 > nothing
		c3 EOS > nothing
		c2 c7 > nothing
		c7 c2 > nothing
		c8 avatar > killSprite
		avatar c8 > killSprite
		c4 c7 > nothing
		c7 c4 > nothing
		c3 c6 > nothing
		c6 c3 > nothing
		c6 c6 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c6 EOS > nothing
		c4 avatar > killSprite
		avatar c4 > killSprite
		c2 EOS > nothing
		c4 c4 > nothing
		c6 c7 > stepBack
		c7 c6 > stepBack
		c7 c7 > stepBack
	TerminationSet
		MultiSpriteCounter stype0=c4 stype1=c3 limit=0 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=avatar s2=avatar win=True
		NoveltyTermination s1=c6 s2=c8 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c8 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c8 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c7 s2=EOS win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c2 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c3 s2=c8 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c8 s2=EOS win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		NoveltyTermination s1=c2 s2=c6 win=True
		NoveltyTermination s1=c8 s2=c8 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		SpriteCounter stype=c8 limit=0 win=True
		SpriteCounter stype=c2 limit=0 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		8 > c2
		d > c4
		7 > c6
		c > avatar
		9 > c7
		b > c8
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
