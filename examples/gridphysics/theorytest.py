level="""
55555555555555555555555555
52223244232222223224344225
52223333332222222232232225
52222444222222222323433235
54222222222222222343222335
55555555552222222232225445
50 22283222222222222225445
5  22222222 32222 22225445
53332222222 22222322225225
52222224222755554 42335225
58  2222242 33443 22225225
5   22622222222220     225
55555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		c9 > RandomNPC color=RED cooldown=4
		c8 > ResourcePack color=BLACK
		avatar > ShootAvatar color=WHITE stype=sword
		sword > Flicker color=BLUE singleton=True
		c3 > Chaser color=PINK fleeing=False stype=c9
		c7 > ResourcePack color=GREEN
		c6 > ResourcePack color=YELLOW
		c5 > Missile color=DARKGRAY speed=0.2 orientation=DOWN
		c4 > ResourcePack color=BROWN
		diamond > Resource color=RESOURCETOADD limit=9
	InteractionSet
		c7 c9 > killSprite
		c9 c7 > killSprite
		c6 c7 > killSprite
		c7 c6 > killSprite
		c8 c8 > killSprite
		c6 c8 > killSprite
		c8 c6 > killSprite
		c4 c8 > killSprite
		c8 c4 > killSprite
		c6 avatar > changeScore value=5
		avatar c6 > changeResource resource=diamond limit=9 value=1
		c6 avatar > killSprite
		c7 c8 > killSprite
		c8 c7 > killSprite
		sword c9 > killSprite
		c9 sword > killSprite
		c6 c9 > killSprite
		c9 c6 > killSprite
		c3 c9 > killSprite
		c9 c3 > killSprite
		sword avatar > nothing
		sword c7 > killSprite
		c7 sword > killSprite
		c5 sword > nothing
		sword c5 > nothing
		c5 c7 > killSprite
		c7 c5 > killSprite
		c3 avatar > killSprite
		c3 avatar > killIfOtherHasMore resource=diamond limit=0
		sword c3 > killSprite
		c3 sword > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c3 c7 > killSprite
		c7 c3 > killSprite
		c6 sword > nothing
		c4 sword > killSprite
		c3 c3 > killSprite
		c7 avatar > nothing
		avatar c8 > stepBack
		c4 c7 > killSprite
		c7 c4 > killSprite
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		sword sword > killSprite
		c7 c7 > killSprite
		avatar c5 > stepBack
		c4 avatar > killSprite
		c8 sword > nothing
		c9 c9 > killSprite
		avatar c9 > killSprite
		c4 c4 > killSprite
		sword EOS > stepBack
		c3 c4 > stepBack
		c8 EOS > stepBack
		c9 c5 > stepBack
		c3 c5 > stepBack
		c5 c4 > stepBack
		c9 c8 > stepBack
		c4 EOS > stepBack
		c9 c4 > stepBack
		c5 EOS > stepBack
		c5 c8 > stepBack
		c3 c8 > stepBack
		c5 c5 > stepBack
		c5 c6 > stepBack
		c7 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c9 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=sword s2=c3 win=True
		NoveltyTermination s1=sword s2=c7 win=True
		NoveltyTermination s1=sword s2=c9 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
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
		NoveltyTermination s1=c9 s2=c9 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=True
		SpriteCounter stype=c6 limit=0 win=True
	LevelMapping
		0 > c3
		1 > sword
		c > c5 c3
		d > avatar c7
		2 > c4
		3 > c5
		b > sword c8
		e > c5 sword
		4 > c6
		5 > c8
		h > c6 sword
		9 > avatar sword
		6 > c7
		7 > avatar
		8 > c9
		f > c9 sword
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
