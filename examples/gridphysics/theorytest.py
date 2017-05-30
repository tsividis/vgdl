level="""
888888888888888888
8   5   b        8
8    88888 1     8
8            8  88
8    8       85 88
8 5  8     6     8
8   b 8          8
8     8    0 6   8
8   4 8         98
888888888888888888
"""
game = """
BasicGame
	SpriteSet
		c8 > ResourcePack color=RED
		avatar > MovingAvatar color=DARKBLUE
		c3 > Missile color=LIGHTBLUE speed=0.5 orientation=DOWN
		c2 > Missile color=PINK speed=0.3 orientation=RIGHT
		c7 > ResourcePack color=BLACK
		c6 > ResourcePack color=GREEN
		c5 > Resource color=LIGHTGREEN
		c4 > Missile color=YELLOW speed=0.2 orientation=LEFT
	InteractionSet
		c2 avatar > killSprite
		c6 c7 > killSprite
		c7 c6 > killSprite
		c8 c8 > killSprite
		c2 c4 > killSprite
		c4 c2 > killSprite
		c4 c8 > killSprite
		c8 c4 > killSprite
		c6 avatar > killSprite
		c4 c5 > killSprite
		c5 c4 > killSprite
		c3 c5 > turn
		c8 EOS > stepBack
		c3 c4 > killSprite
		c4 c3 > killSprite
		c2 c5 > turn
		c4 EOS > stepBack
		avatar c7 > stepBack
		c2 c8 > killSprite
		c8 c2 > killSprite
		c5 c7 > killSprite
		c7 c5 > killSprite
		c3 avatar > killSprite
		c5 EOS > stepBack
		c5 c8 > killSprite
		c8 c5 > killSprite
		c6 c8 > killSprite
		c8 c6 > killSprite
		c2 c6 > killSprite
		c6 c2 > killSprite
		c3 c8 > killSprite
		c8 c3 > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c3 c7 > killSprite
		c7 c3 > killSprite
		c2 c2 > killSprite
		c5 c6 > killSprite
		c6 c5 > killSprite
		c7 EOS > stepBack
		c3 c3 > killSprite
		c7 c8 > killSprite
		c8 c7 > killSprite
		c3 EOS > stepBack
		c2 c7 > killSprite
		c7 c2 > killSprite
		c8 avatar > killSprite
		c4 c7 > turn
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c7 c7 > killSprite
		c6 EOS > stepBack
		c5 avatar > killSprite
		avatar c4 > killSprite
		c5 c5 > killSprite
		c2 EOS > stepBack
		c4 c4 > killSprite
	TerminationSet
		# NoveltyTermination s1=c2 s2=avatar win=True
		# NoveltyTermination s1=c2 s2=c2 win=True
		# NoveltyTermination s1=c2 s2=c3 win=True
		# NoveltyTermination s1=c2 s2=c4 win=True
		# NoveltyTermination s1=c2 s2=c6 win=True
		# NoveltyTermination s1=c2 s2=c7 win=True
		# NoveltyTermination s1=c2 s2=c8 win=True
		# NoveltyTermination s1=c3 s2=avatar win=True
		# NoveltyTermination s1=c3 s2=c3 win=True
		# NoveltyTermination s1=c3 s2=c4 win=True
		# NoveltyTermination s1=c3 s2=c6 win=True
		# NoveltyTermination s1=c3 s2=c7 win=True
		# NoveltyTermination s1=c3 s2=c8 win=True
		# NoveltyTermination s1=c4 s2=c4 win=True
		# NoveltyTermination s1=c4 s2=c5 win=True
		# NoveltyTermination s1=c4 s2=c6 win=True
		# NoveltyTermination s1=c4 s2=c8 win=True
		# NoveltyTermination s1=c5 s2=avatar win=True
		# NoveltyTermination s1=c5 s2=c5 win=True
		# NoveltyTermination s1=c5 s2=c6 win=True
		# NoveltyTermination s1=c5 s2=c7 win=True
		# NoveltyTermination s1=c5 s2=c8 win=True
		# NoveltyTermination s1=c6 s2=avatar win=True
		# NoveltyTermination s1=c6 s2=c6 win=True
		# NoveltyTermination s1=c6 s2=c7 win=True
		# NoveltyTermination s1=c6 s2=c8 win=True
		# NoveltyTermination s1=c7 s2=c7 win=True
		# NoveltyTermination s1=c7 s2=c8 win=True
		# NoveltyTermination s1=c8 s2=c8 win=True
		SpriteCounter stype=avatar limit=0 win=False
		# SpriteCounter stype=c8 limit=0 win=True
	LevelMapping
		0 > c2
		1 > c3
		4 > avatar
		5 > c4
		6 > c5
		8 > c7
		9 > c6
		b > c8
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
