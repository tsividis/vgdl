level="""
55555555555555555555555555
52223244232222223224344225
52223333332222222232232225
52222444222222222323433235
54222222222222222343222335
55555555552222222232225445
5 022283222222222222225445
5  22222222792222 22225445
53332222222222222322225225
52222224222255554 42335225
5   2222242233443022225225
58  2262222222222      225
55555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		c9 > RandomNPC color=RED cooldown=2
		c8 > ResourcePack color=BLACK
		avatar > ShootAvatar color=WHITE stype=sword
		sword > Flicker color=BLUE singleton=True
		c3 > RandomNPC color=PINK cooldown=5
		c7 > ResourcePack color=GREEN
		c6 > ResourcePack color=YELLOW
		c5 > Missile color=DARKGRAY speed=0.2 orientation=DOWN
		c4 > ResourcePack color=BROWN
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c6 c7 > killSprite
		c7 c6 > killSprite
		c8 c8 > killSprite
		c6 c8 > killSprite
		c8 c6 > killSprite
		c4 c8 > killSprite
		c8 c4 > killSprite
		c6 avatar > killSprite
		c7 c9 > killSprite
		c9 c7 > killSprite
		c5 c9 > killSprite
		c9 c5 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
		c8 c9 > killSprite
		c9 c8 > killSprite
		sword c9 > killSprite
		c9 sword > killSprite
		c6 c9 > killSprite
		c9 c6 > killSprite
		c3 c9 > killSprite
		c9 c3 > killSprite
		c4 c9 > killSprite
		c9 c4 > killSprite
		sword avatar > killSprite
		c7 avatar > killSprite
		sword c7 > killSprite
		c7 sword > killSprite
		c5 sword > nothing
		sword c5 > nothing
		c5 c7 > killSprite
		c7 c5 > killSprite
		c3 avatar > killSprite
		c5 c8 > killSprite
		c8 c5 > killSprite
		sword c3 > killSprite
		c3 sword > killSprite
		c3 c8 > killSprite
		c8 c3 > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c3 c7 > killSprite
		c7 c3 > killSprite
		sword c6 > killSprite
		c6 sword > killSprite
		sword c4 > killSprite
		c4 sword > killSprite
		c3 c3 > killSprite
		c7 c8 > killSprite
		c8 c7 > killSprite
		c8 avatar > killSprite
		c4 c7 > killSprite
		c7 c4 > killSprite
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		sword sword > killSprite
		c7 c7 > killSprite
		c5 avatar > killSprite
		c4 avatar > killSprite
		sword c8 > killSprite
		c8 sword > killSprite
		c9 c9 > killSprite
		c9 avatar > killSprite
		c4 c4 > killSprite
		sword EOS > stepBack
		c8 EOS > stepBack
		c5 c4 > stepBack
		c5 EOS > stepBack
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
		NoveltyTermination s1=sword s2=c6 win=True
		NoveltyTermination s1=sword s2=c7 win=True
		NoveltyTermination s1=sword s2=c8 win=True
		NoveltyTermination s1=sword s2=c9 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c3 s2=c8 win=True
		NoveltyTermination s1=c3 s2=c9 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c8 win=True
		NoveltyTermination s1=c4 s2=c9 win=True
		NoveltyTermination s1=c5 s2=avatar win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c8 win=True
		NoveltyTermination s1=c5 s2=c9 win=True
		NoveltyTermination s1=c6 s2=avatar win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c8 win=True
		NoveltyTermination s1=c6 s2=c9 win=True
		NoveltyTermination s1=c7 s2=avatar win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		NoveltyTermination s1=c7 s2=c8 win=True
		NoveltyTermination s1=c7 s2=c9 win=True
		NoveltyTermination s1=c8 s2=avatar win=True
		NoveltyTermination s1=c8 s2=c8 win=True
		NoveltyTermination s1=c8 s2=c9 win=True
		NoveltyTermination s1=c9 s2=avatar win=True
		NoveltyTermination s1=c9 s2=c9 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c3
		1 > sword
		9 > c5 sword
		2 > c4
		3 > c5
		4 > c6
		5 > c8
		6 > c7
		7 > avatar
		8 > c9
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
