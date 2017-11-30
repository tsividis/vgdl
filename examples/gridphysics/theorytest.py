level="""
5555555555555
5  36    1  5
5 7  4    8 5
5   2 0   2 5
5555555555555
"""
game = """
BasicGame
	SpriteSet
		c9 > ResourcePack color=RED speed=0.9 cooldown=3
		c8 > ResourcePack color=GREEN speed=0.9 cooldown=3
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=LIGHTBLUE speed=0.9 cooldown=3
		c2 > ResourcePack color=BLUE speed=0.9 cooldown=3
		c7 > ResourcePack color=ORANGE speed=0.9 cooldown=3
		c6 > ResourcePack color=PINK speed=0.9 cooldown=3
		c5 > ResourcePack color=BLACK speed=0.9 cooldown=3
		c4 > ResourcePack color=YELLOW speed=0.9 cooldown=3
	InteractionSet
		c2 avatar > stepBack
		c6 c7 > nothing
		c7 c6 > nothing
		c8 c8 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c4 c8 > nothing
		c8 c4 > nothing
		c6 avatar > killSprite
		c7 c9 > nothing
		c9 c7 > nothing
		c4 c5 > nothing
		c5 c4 > nothing
		c5 c9 > nothing
		c9 c5 > nothing
		c3 c5 > nothing
		c5 c3 > nothing
		c3 c4 > nothing
		c4 c3 > nothing
		c8 c9 > nothing
		c9 c8 > nothing
		c2 c5 > nothing
		c5 c2 > nothing
		c3 c9 > nothing
		c9 c3 > nothing
		c4 c9 > nothing
		c9 c4 > nothing
		c7 avatar > killSprite
		c2 c8 > nothing
		c8 c2 > nothing
		c5 c7 > nothing
		c7 c5 > nothing
		avatar EOS > stepBack
		c3 avatar > killSprite
		c5 c8 > nothing
		c8 c5 > nothing
		c8 avatar > killSprite
		c6 c8 > nothing
		c8 c6 > nothing
		c2 c6 > nothing
		c6 c2 > nothing
		c3 c8 > nothing
		c8 c3 > nothing
		c4 c6 > nothing
		c6 c4 > nothing
		c3 c7 > nothing
		c7 c3 > nothing
		c2 c9 > nothing
		c9 c2 > nothing
		c9 c9 > nothing
		c2 c2 > nothing
		c5 c6 > nothing
		c6 c5 > nothing
		c3 c3 > nothing
		c6 c9 > nothing
		c9 c6 > nothing
		c2 c7 > nothing
		c7 c2 > nothing
		c7 c8 > nothing
		c8 c7 > nothing
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
		c8 EOS > stepBack
		c5 EOS > stepBack
		c7 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c9 EOS > stepBack
		c2 EOS > stepBack
		c4 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c2 s2=c6 win=True
		NoveltyTermination s1=c2 s2=c7 win=True
		NoveltyTermination s1=c2 s2=c8 win=True
		NoveltyTermination s1=c2 s2=c9 win=True
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
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c8 win=True
		NoveltyTermination s1=c4 s2=c9 win=True
		NoveltyTermination s1=c5 s2=avatar win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
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
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c7 s2=EOS win=True
		NoveltyTermination s1=c8 s2=EOS win=True
		NoveltyTermination s1=c9 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c6
		1 > c3
		2 > c2
		3 > avatar
		4 > c4
		5 > c5
		6 > c7
		7 > c8
		8 > c9
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
