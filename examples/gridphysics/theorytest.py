level="""
55555555555555555555555555
53331366313333331336166335
53331111113333333313313335
53333666333333333131611315
56333333333333333161333115
55555555553333333313335665
5  333214   33333333335665
58 3333333  13333 33335665
51113333333333333 33335335
53333336333355556 63115335
5   3333363311661 33335335
5  233733333333331  8  335
55555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		c9 > Chaser color=RED fleeing=True cooldown=5 stype=c9
		c8 > ResourcePack color=GREEN
		avatar > ShootAvatar color=DARKBLUE stype=sword
		sword > Flicker color=PINK singleton=True limit=5
		c3 > ResourcePack color=BROWN
		c7 > ResourcePack color=YELLOW
		c6 > ResourcePack color=DARKGRAY
		c5 > Missile color=GRAY speed=0.2 orientation=DOWN cooldown=1
		c4 > Chaser color=GOLD fleeing=False cooldown=5 stype=c9
	InteractionSet
		c7 c9 > nothing
		c9 c7 > nothing
		c6 c7 > nothing
		c7 c6 > nothing
		c8 c8 > nothing
		c3 avatar > killSprite
		c6 c8 > nothing
		c8 c6 > nothing
		c4 c8 > nothing
		c8 c4 > nothing
		avatar c6 > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c8 c9 > nothing
		c9 c8 > nothing
		sword c9 > nothing
		c9 sword > nothing
		c3 c9 > nothing
		c9 c3 > nothing
		c4 c9 > nothing
		c9 c4 > nothing
		sword avatar > killSprite
		c7 avatar > killSprite
		sword c7 > nothing
		c7 sword > nothing
		sword c5 > nothing
		c5 sword > nothing
		avatar EOS > stepBack
		c7 c8 > nothing
		c8 c7 > nothing
		c5 c8 > nothing
		c8 c5 > nothing
		sword c3 > nothing
		c3 sword > nothing
		c3 c8 > nothing
		c8 c3 > nothing
		c3 c7 > nothing
		c7 c3 > nothing
		sword c6 > nothing
		c6 sword > nothing
		sword c4 > nothing
		c4 sword > nothing
		c3 c3 > nothing
		c8 avatar > killSprite
		c4 c7 > nothing
		c7 c4 > nothing
		c3 c6 > nothing
		c6 c3 > nothing
		c6 c6 > nothing
		sword sword > nothing
		c7 c7 > nothing
		avatar c5 > stepBack
		c4 avatar > killSprite
		sword c8 > nothing
		c8 sword > nothing
		c9 c9 > nothing
		c9 avatar > killSprite
		c4 c4 > nothing
		sword EOS > stepBack
		c8 EOS > stepBack
		c9 c5 > stepBack
		c5 c3 > stepBack
		c4 c5 > stepBack
		c9 c6 > stepBack
		c5 c7 > stepBack
		c5 EOS > stepBack
		c4 c6 > stepBack
		c5 c5 > stepBack
		c5 c6 > stepBack
		c7 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c9 EOS > stepBack
		c4 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=sword s2=avatar win=True
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=sword s2=c3 win=True
		NoveltyTermination s1=sword s2=c4 win=True
		NoveltyTermination s1=sword s2=c5 win=True
		NoveltyTermination s1=sword s2=c6 win=True
		NoveltyTermination s1=sword s2=c7 win=True
		NoveltyTermination s1=sword s2=c8 win=True
		NoveltyTermination s1=sword s2=c9 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c3 s2=c8 win=True
		NoveltyTermination s1=c3 s2=c9 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c8 win=True
		NoveltyTermination s1=c4 s2=c9 win=True
		NoveltyTermination s1=c5 s2=c8 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c8 win=True
		NoveltyTermination s1=c7 s2=avatar win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		NoveltyTermination s1=c7 s2=c8 win=True
		NoveltyTermination s1=c7 s2=c9 win=True
		NoveltyTermination s1=c8 s2=avatar win=True
		NoveltyTermination s1=c8 s2=c8 win=True
		NoveltyTermination s1=c8 s2=c9 win=True
		NoveltyTermination s1=c9 s2=avatar win=True
		NoveltyTermination s1=c9 s2=c9 win=True
		NoveltyTermination s1=sword s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c7 s2=EOS win=True
		NoveltyTermination s1=c8 s2=EOS win=True
		NoveltyTermination s1=c9 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c3 limit=0 win=True
	LevelMapping
		0 > sword
		1 > c5
		2 > c4
		3 > c3
		4 > avatar
		5 > c6
		6 > c7
		7 > c8
		8 > c9
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
