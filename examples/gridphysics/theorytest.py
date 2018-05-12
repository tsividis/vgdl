level="""
55555555555555555555555555
53331366313333331336166335
53331111113333333313313335
53333666333333333131611315
56333333333333333161333115
55555555553333333313335665
53 33331333333333333335665
5  3333333  13333 33335665
5111333333 333333 33335335
533333  33 355556 63115335
5   33      11661 33335335
5   33933   333331     335
55555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		avatar > ShootAvatar color=DARKBLUE stype=sword
		sword > Flicker color=PINK singleton=True limit=5
		c3 > ResourcePack color=BROWN
		c7 > Missile color=GRAY speed=0.2 orientation=DOWN cooldown=1
		c6 > ResourcePack color=YELLOW
		c5 > ResourcePack color=GREEN
		c4 > ResourcePack color=DARKGRAY
		diamond > Resource color=RESOURCETOADD limit=10
	InteractionSet
		c3 c5 > nothing
		c5 c3 > nothing
		avatar c6 > changeResource resource=diamond limit=10 value=1
		c6 avatar > killSprite
		c4 c5 > nothing
		c5 c4 > nothing
		c3 c4 > nothing
		c4 c3 > nothing
		sword avatar > killSprite
		sword avatar > killIfOtherHasMore resource=diamond limit=1
		c7 avatar > killIfOtherHasMore resource=diamond limit=1
		avatar c7 > stepBack
		sword c7 > nothing
		c7 sword > nothing
		sword c5 > nothing
		c5 sword > nothing
		c5 c7 > nothing
		c7 c5 > nothing
		avatar EOS > stepBack
		c3 avatar > killSprite
		sword c3 > nothing
		c3 sword > nothing
		c4 c6 > nothing
		c6 c4 > nothing
		c5 c6 > nothing
		c6 c5 > nothing
		sword c6 > nothing
		c6 sword > nothing
		sword c4 > nothing
		c4 sword > nothing
		c3 c3 > nothing
		c3 c6 > nothing
		c6 c3 > nothing
		c6 c6 > nothing
		sword sword > nothing
		c5 avatar > nothing
		c4 avatar > killIfOtherHasMore resource=diamond limit=1
		avatar c4 > stepBack
		c5 c5 > nothing
		c4 c4 > nothing
		c7 c6 > stepBack
		c5 EOS > stepBack
		sword EOS > stepBack
		c4 EOS > stepBack
		c7 c3 > stepBack
		c7 EOS > stepBack
		c3 EOS > stepBack
		c7 c4 > stepBack
		c7 c7 > stepBack
		c6 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=sword s2=avatar win=True
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=sword s2=c3 win=True
		NoveltyTermination s1=sword s2=c4 win=True
		NoveltyTermination s1=sword s2=c5 win=True
		NoveltyTermination s1=sword s2=c6 win=True
		NoveltyTermination s1=sword s2=c7 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=sword s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c7 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c4 s2=avatar win=True args={item:diamond,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=sword s2=avatar win=True args={item:diamond,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c7 s2=avatar win=True args={item:diamond,num:0,negated:False,operator_name:>}
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c3 limit=0 win=True
		SpriteCounter stype=c6 limit=0 win=True
	LevelMapping
		0 > sword
		1 > c7
		3 > c3
		4 > avatar
		5 > c4
		6 > c6
		9 > avatar c5
		7 > c5
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
