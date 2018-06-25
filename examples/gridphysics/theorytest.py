level="""
77777777777777777777777777777777
7              b       0      e7
7cccccccccccccccccccccccccccccc7
7                              7
7   1        1     1           7
7       1                1     7
7             1              1 7
7     1    1         1         7
7        1      1         1    7
7    1            1            7
7                      1   1   7
7       1         1            7
5 d            6               2
77777777777777777777777777777777
"""
game = """
BasicGame
	SpriteSet
		c9 > Missile color=RED speed=0.4 orientation=RIGHT cooldown=1
		c8 > ResourcePack color=WHITE
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=BROWN
		c2 > Missile color=BLUE speed=0.4 orientation=RIGHT cooldown=1
		c7 > Missile color=GREEN speed=0.7 orientation=LEFT cooldown=4
		c6 > ResourcePack color=BLACK
		c5 > ResourcePack color=YELLOW
		c4 > ResourcePack color=GOLD
	InteractionSet
		c2 avatar > killSprite
		c8 c8 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c4 c8 > nothing
		c8 c4 > nothing
		avatar c6 > stepBack
		c9 c6 > nothing
		c6 c9 > nothing
		c9 c7 > nothing
		c7 c9 > nothing
		c4 c5 > nothing
		c5 c4 > nothing
		c9 c5 > nothing
		c5 c9 > nothing
		c3 c5 > nothing
		c5 c3 > nothing
		c3 c4 > nothing
		c4 c3 > nothing
		c9 c8 > nothing
		c8 c9 > nothing
		c9 c4 > nothing
		c4 c9 > nothing
		c2 c5 > nothing
		c5 c2 > nothing
		c9 c3 > nothing
		c3 c9 > nothing
		c7 avatar > killSprite
		c2 c8 > nothing
		c8 c2 > nothing
		c5 c7 > nothing
		c7 c5 > nothing
		avatar EOS > stepBack
		c3 avatar > killSprite
		c5 c8 > nothing
		c8 c5 > nothing
		c6 c8 > nothing
		c8 c6 > nothing
		c3 c8 > nothing
		c8 c3 > nothing
		c4 c6 > nothing
		c6 c4 > nothing
		c3 c7 > nothing
		c7 c3 > nothing
		c9 c2 > nothing
		c2 c9 > nothing
		c2 c2 > nothing
		c5 c6 > nothing
		c6 c5 > nothing
		c3 c3 > nothing
		c7 c8 > nothing
		c8 c7 > nothing
		c7 c2 > nothing
		c2 c7 > nothing
		c8 avatar > killSprite
		c4 c7 > nothing
		c7 c4 > nothing
		c3 c6 > nothing
		c6 c3 > nothing
		c6 c6 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c7 c7 > nothing
		c5 avatar > killSprite
		c4 avatar > killSprite
		c5 c5 > nothing
		c9 avatar > killSprite
		c4 c4 > nothing
		c7 c6 > stepBack
		c8 EOS > stepBack
		c4 EOS > stepBack
		c5 EOS > stepBack
		c2 c6 > stepBack
		c7 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c9 EOS > stepBack
		c2 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c2 s2=c8 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c3 s2=c8 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c8 win=True
		NoveltyTermination s1=c5 s2=avatar win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c8 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c8 win=True
		NoveltyTermination s1=c7 s2=avatar win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		NoveltyTermination s1=c7 s2=c8 win=True
		NoveltyTermination s1=c8 s2=avatar win=True
		NoveltyTermination s1=c8 s2=c8 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c7 s2=EOS win=True
		NoveltyTermination s1=c8 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c9 s2=avatar win=True
		NoveltyTermination s1=c9 s2=EOS win=True
		NoveltyTermination s1=c9 s2=c2 win=True
		NoveltyTermination s1=c9 s2=c3 win=True
		NoveltyTermination s1=c9 s2=c4 win=True
		NoveltyTermination s1=c9 s2=c6 win=True
		NoveltyTermination s1=c9 s2=c7 win=True
		NoveltyTermination s1=c9 s2=c8 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c2
		1 > c3
		2 > c4
		f > c9 c5
		5 > c5
		e > c7 c2
		6 > avatar
		7 > c6
		b > c7
		c > c8
		d > c9
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
