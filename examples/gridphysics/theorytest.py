level="""
5555555555555
84       5  5
5  5        5
5   5   5 755
555 50  55555
5       5 6 5
5     0     5
5  0        5
5555555555555
"""
game = """
BasicGame
	SpriteSet
		avatar > ShootAvatar color=DARKBLUE stype=sword
		sword > OrientedFlicker color=BLUE singleton=True
		c3 > Chaser color=PINK fleeing=True cooldown=4 stype=sword
		c6 > ResourcePack color=ORANGE
		c5 > ResourcePack color=GREEN
		c4 > ResourcePack color=DARKGRAY
	InteractionSet
		c3 c5 > nothing
		c5 c3 > nothing
		c6 avatar > killSprite
		c4 c5 > nothing
		c5 c4 > nothing
		c3 avatar > killSprite
		sword avatar > killSprite
		sword c5 > nothing
		c5 sword > nothing
		avatar EOS > stepBack
		sword c3 > nothing
		c3 sword > nothing
		c4 c6 > nothing
		c6 c4 > nothing
		c5 c6 > nothing
		c6 c5 > nothing
		sword c6 > nothing
		c6 sword > nothing
		sword c4 > nothing
		c3 c3 > nothing
		c3 c6 > nothing
		c6 c3 > nothing
		c6 c6 > nothing
		sword sword > nothing
		c5 avatar > killSprite
		avatar c4 > stepBack
		c5 c5 > nothing
		c4 c4 > nothing
		c5 EOS > stepBack
		sword EOS > stepBack
		c4 EOS > stepBack
		c3 c4 > stepBack
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
		NoveltyTermination s1=sword s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
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
