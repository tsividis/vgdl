level="""
55555555555555555555555555
53331366313333331336166335
53331111113333333313313335
53333666333333333131611315
56333333333333333161333115
555555d5553333333313335665
5  3   4333333333333335665
5 83 2  333 13333 33335665
511133 1333 33333 33335335
5333333   3 55556 63115335
5  233333   11661 33335335
5   337333  3333318    335
55555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		c9 > Chaser color=RED fleeing=False cooldown=5 stype=c4
		c8 > ResourcePack color=GREEN
		avatar > ShootAvatar color=DARKBLUE stype=sword
		sword > Flicker color=PINK singleton=True limit=5
		c3 > Missile color=GRAY speed=0.2 orientation=DOWN cooldown=1
		c7 > ResourcePack color=YELLOW
		c6 > ResourcePack color=DARKGRAY
		c5 > ResourcePack color=BROWN
		c4 > Chaser color=GOLD fleeing=False cooldown=5 stype=c9
		diamond > Resource color=RESOURCETOADD limit=10
	InteractionSet
		c7 c9 > nothing
		c9 c7 > nothing
		c6 c7 > nothing
		c7 c6 > nothing
		c8 c8 > nothing
		c6 c8 > nothing
		c8 c6 > nothing
		c4 c8 > nothing
		c8 c4 > nothing
		avatar c6 > stepBack
		c7 c8 > nothing
		c8 c7 > nothing
		c8 c9 > nothing
		c9 c8 > nothing
		sword c9 > nothing
		c9 sword > nothing
		c4 c9 > nothing
		c9 c4 > nothing
		sword avatar > killIfOtherHasMore resource=diamond limit=1
		sword avatar > nothing
		avatar c7 > changeResource limit=10 resource=diamond value=1
		c7 avatar > killSprite
		sword c7 > nothing
		c7 sword > nothing
		c5 sword > killSprite
		c5 c7 > nothing
		c7 c5 > nothing
		avatar EOS > stepBack
		avatar c3 > stepBack
		c5 c8 > nothing
		c8 c5 > nothing
		sword c3 > nothing
		c3 sword > nothing
		c3 c8 > nothing
		c8 c3 > nothing
		c9 c9 > nothing
		c5 c6 > nothing
		c6 c5 > nothing
		sword c6 > nothing
		sword c4 > nothing
		c4 sword > nothing
		c8 avatar > nothing
		c4 c7 > nothing
		c7 c4 > nothing
		c6 c6 > nothing
		sword sword > nothing
		c7 c7 > nothing
		c5 avatar > killSprite
		avatar c4 > killSprite
		c4 avatar > killIfOtherHasMore resource=diamond limit=1
		sword c8 > nothing
		c8 sword > nothing
		c5 c5 > nothing
		avatar c9 > killSprite
		c4 c4 > nothing
		sword EOS > stepBack
		c4 c3 > stepBack
		c8 EOS > stepBack
		c9 c5 > stepBack
		c3 c5 > stepBack
		c4 c5 > stepBack
		c9 c6 > stepBack
		c9 c3 > stepBack
		c5 EOS > stepBack
		c4 c6 > stepBack
		c3 c7 > stepBack
		c7 EOS > stepBack
		c3 c3 > stepBack
		c3 EOS > stepBack
		c3 c6 > stepBack
		c6 EOS > stepBack
		c9 EOS > stepBack
		c4 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=sword s2=c3 win=True
		NoveltyTermination s1=sword s2=c4 win=True
		NoveltyTermination s1=sword s2=c7 win=True
		NoveltyTermination s1=sword s2=c8 win=True
		NoveltyTermination s1=sword s2=c9 win=True
		NoveltyTermination s1=c3 s2=c8 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c8 win=True
		NoveltyTermination s1=c4 s2=c9 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c8 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c8 win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		NoveltyTermination s1=c7 s2=c8 win=True
		NoveltyTermination s1=c7 s2=c9 win=True
		NoveltyTermination s1=c8 s2=c8 win=True
		NoveltyTermination s1=c8 s2=c9 win=True
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
		NoveltyTermination s1=c4 s2=avatar win=True args={item:diamond,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=sword s2=avatar win=True args={item:diamond,num:0,negated:False,operator_name:>}
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c5 limit=0 win=True
		SpriteCounter stype=c7 limit=0 win=True
	LevelMapping
		0 > sword
		1 > c3
		2 > c4
		3 > c5
		4 > avatar
		5 > c6
		c > avatar sword
		6 > c7
		b > avatar c8
		7 > c8
		d > sword c6
		9 > c3 c9
		8 > c9
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
