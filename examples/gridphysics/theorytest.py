level="""
55555555555555555555555555
5   324423      3  43442 5
5   333333      2 322322 5
5   244422       323433235
54  22222        343222335
5555555555       232  5445
5 02  832        22   5445
5  2  22    322223    5445
533322222   2    2    5225
52222 242   55554 42335  5
5    222  7 33443 22225  5
5    262    22222        5
55555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		c9 > RandomNPC color=RED cooldown=2
		c8 > ResourcePack color=GREEN
		avatar > ShootAvatar color=WHITE stype=sword
		sword > Flicker color=BLUE singleton=True
		c3 > RandomNPC color=PINK cooldown=6
		c7 > ResourcePack color=BLACK
		c6 > ResourcePack color=YELLOW
		c5 > Missile color=DARKGRAY speed=0.2 orientation=DOWN
		c4 > ResourcePack color=BROWN
		diamond > Resource color=RESOURCETOADD limit=5
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c6 c7 > killSprite
		c7 c6 > killSprite
		c8 c8 > killSprite
		avatar c3 > killSprite
		c6 c8 > killSprite
		c8 c6 > killSprite
		c4 c8 > killSprite
		c8 c4 > killSprite
		c6 avatar > changeScore value=5
		avatar c6 > changeResource limit=5 resource=diamond value=1
		c6 avatar > killSprite
		sword EOS > stepBack
		c9 c7 > stepBack
		c8 EOS > stepBack
		c9 c5 > stepBack
		c5 c4 > stepBack
		c7 c8 > killSprite
		c8 c7 > killSprite
		c8 c9 > killSprite
		c9 c8 > killSprite
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
		c5 c7 > stepBack
		c3 c4 > stepBack
		c5 EOS > stepBack
		c5 c8 > killSprite
		c8 c5 > killSprite
		sword c3 > killSprite
		c3 sword > killSprite
		c3 c8 > killSprite
		c8 c3 > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c3 c7 > stepBack
		c5 c5 > stepBack
		c5 c6 > stepBack
		c7 EOS > stepBack
		c6 sword > nothing
		c4 sword > killSprite
		c3 c3 > killSprite
		avatar c7 > stepBack
		c3 EOS > stepBack
		c8 avatar > nothing
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
		avatar c9 > killSprite
		c4 c4 > killSprite
	TerminationSet
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=sword s2=c3 win=True
		NoveltyTermination s1=sword s2=c9 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c8 win=True
		NoveltyTermination s1=c3 s2=c9 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c8 win=True
		NoveltyTermination s1=c5 s2=c8 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c8 win=True
		NoveltyTermination s1=c6 s2=c9 win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		NoveltyTermination s1=c7 s2=c8 win=True
		NoveltyTermination s1=c8 s2=c8 win=True
		NoveltyTermination s1=c8 s2=c9 win=True
		NoveltyTermination s1=c9 s2=c9 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=True
		SpriteCounter stype=c6 limit=0 win=True
	LevelMapping
		0 > c3
		1 > sword
		9 > c5 sword
		h > c9 sword
		2 > c4
		3 > c5
		d > sword c7
		4 > c6
		e > c8 sword
		f > avatar c8 sword
		5 > c7
		c > c6 sword
		b > avatar sword
		6 > c8
		7 > avatar
		8 > c9
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
