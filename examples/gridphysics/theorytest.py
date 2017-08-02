level="""
55555555555555555555555555
5   324423      3  43442 5
5   333333      2 322322 5
5   244422       323433235
54  22222        343222335
5555555555       232  5445
50 2  832        22   5445
5  2  22   7322223    5445
533322222   2    2    5225
52222 24222255554 42335  5
5    222242233443 22225  5
5    262    22222        5
55555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		c9 > RandomNPC color=RED cooldown=1
		c8 > ResourcePack color=BLACK
		avatar > ShootAvatar color=WHITE stype=sword
		sword > Flicker color=BLUE singleton=True
		c3 > RandomNPC color=PINK cooldown=8
		c7 > ResourcePack color=GREEN
		c6 > ResourcePack color=YELLOW
		c5 > Missile color=DARKGRAY speed=0.2 orientation=DOWN
		c4 > ResourcePack color=BROWN
		diamond > Resource color=RESOURCETOADD limit=5
	InteractionSet
		c7 c9 > killSprite
		c9 c7 > killSprite
		c6 c7 > killSprite
		c7 c6 > killSprite
		c8 c8 > killSprite
		avatar c3 > killSprite
		c3 avatar > killIfOtherHasMore resource=diamond limit=5
		c6 c8 > killSprite
		c8 c6 > killSprite
		c4 c8 > killSprite
		c8 c4 > killSprite
		c6 avatar > changeScore value=5
		avatar c6 > changeResource resource=diamond limit=5 value=1
		c6 avatar > killSprite
		sword EOS > stepBack
		c8 EOS > stepBack
		c9 c5 > stepBack
		c3 c5 > stepBack
		c5 c4 > stepBack
		c7 c8 > killSprite
		c8 c7 > killSprite
		c9 c8 > stepBack
		sword c9 > killSprite
		c9 sword > killSprite
		c6 c9 > killSprite
		c9 c6 > killSprite
		c3 c9 > killSprite
		c9 c3 > killSprite
		c4 EOS > stepBack
		sword avatar > nothing
		c9 c4 > stepBack
		c7 sword > nothing
		c5 sword > nothing
		sword c5 > nothing
		c5 c7 > killSprite
		c7 c5 > killSprite
		c3 c4 > stepBack
		c5 EOS > stepBack
		c5 c8 > stepBack
		sword c3 > killSprite
		c3 sword > killSprite
		c3 c8 > stepBack
		c4 c6 > killSprite
		c6 c4 > killSprite
		c3 c7 > killSprite
		c7 c3 > killSprite
		c5 c5 > stepBack
		c5 c6 > stepBack
		c7 EOS > stepBack
		c6 sword > nothing
		c4 sword > killSprite
		c3 c3 > killSprite
		c7 avatar > killIfOtherHasMore resource=diamond limit=5
		c7 avatar > nothing
		c3 EOS > stepBack
		avatar c8 > stepBack
		c4 c7 > killSprite
		c7 c4 > killSprite
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		sword sword > killSprite
		c7 c7 > killSprite
		c6 EOS > stepBack
		c9 EOS > stepBack
		avatar c5 > stepBack
		c4 avatar > killSprite
		c8 sword > nothing
		c9 c9 > killSprite
		c9 avatar > killSprite
		c9 avatar > killIfOtherHasMore resource=diamond limit=5
		c9 avatar > killIfOtherHasMore resource=diamond limit=0
		c4 c4 > killSprite
	TerminationSet
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=sword s2=c3 win=True
		NoveltyTermination s1=sword s2=c9 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c3 s2=c9 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c8 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c8 win=True
		NoveltyTermination s1=c6 s2=c9 win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		NoveltyTermination s1=c7 s2=c8 win=True
		NoveltyTermination s1=c7 s2=c9 win=True
		NoveltyTermination s1=c8 s2=c8 win=True
		NoveltyTermination s1=c9 s2=avatar win=True
		NoveltyTermination s1=c9 s2=c9 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c7 s2=avatar win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=True
		SpriteCounter stype=c6 limit=0 win=True
	LevelMapping
		0 > c3
		1 > sword
		9 > c5 sword
		d > avatar c7
		2 > c4
		3 > c5
		b > sword c8
		4 > c6
		f > c7 sword
		5 > c8
		e > c6 sword
		c > avatar sword
		6 > c7
		7 > avatar
		8 > c9
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
