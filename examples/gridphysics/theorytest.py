level="""
5555555555555
54       5  5
5  5        5
5   50  5 755
555 5   55555
5 0     5 6 5
5           5
5      0    5
5555555555555
"""
game = """
BasicGame
	SpriteSet
		avatar > ShootAvatar color=DARKBLUE stype=sword
		sword > OrientedFlicker color=BLUE singleton=True
		c3 > RandomNPC color=PINK cooldown=8
		c6 > ResourcePack color=ORANGE
		c5 > ResourcePack color=GREEN
		c4 > ResourcePack color=DARKGRAY
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c6 avatar > killSprite
		c4 c5 > killSprite
		c5 c4 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
		sword avatar > killSprite
		sword c5 > killSprite
		c5 sword > killSprite
		c3 avatar > killSprite
		sword c3 > killSprite
		c3 sword > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c5 c6 > killSprite
		c6 c5 > killSprite
		sword c6 > killSprite
		c6 sword > killSprite
		sword c4 > nothing
		c3 c3 > killSprite
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		sword sword > killSprite
		c5 avatar > killSprite
		avatar c4 > stepBack
		c5 c5 > killSprite
		c4 c4 > killSprite
		c5 EOS > stepBack
		sword EOS > stepBack
		c4 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=sword s2=avatar win=True
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=sword s2=c3 win=True
		NoveltyTermination s1=sword s2=c5 win=True
		NoveltyTermination s1=sword s2=c6 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c5 s2=avatar win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c6 s2=avatar win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c3
		1 > sword
		4 > avatar
		5 > c4
		8 > sword c4
		6 > c5
		7 > c6
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
