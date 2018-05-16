level="""
55555555555555555555555555
5                        5
5                1       5
5                        5
5555                     5
5 75                 7   5
5555       7             5
5             31         5
5                    0   5
55555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=GREEN
		c2 > ResourcePack color=BLACK
		c5 > ResourcePack color=LIGHTBLUE
		c4 > ResourcePack color=PINK
	InteractionSet
		avatar c2 > stepBack
		c5 c2 > nothing
		c2 c5 > nothing
		c4 c2 > nothing
		c2 c4 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c2 c2 > nothing
		avatar c5 > stepBack
		c3 c3 > nothing
		avatar EOS > stepBack
		c4 c3 > nothing
		c3 c4 > nothing
		c4 avatar > killSprite
		c5 c3 > nothing
		c3 c5 > nothing
		c3 avatar > killSprite
		c4 EOS > stepBack
		c5 EOS > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c4 s2=c2 win=True
		NoveltyTermination s1=c4 s2=c3 win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c5 s2=c2 win=True
		NoveltyTermination s1=c5 s2=c3 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c3 limit=0 win=True
		SpriteCounter stype=c4 limit=0 win=True
	LevelMapping
		0 > c4
		1 > c5
		3 > avatar
		5 > c2
		7 > c3
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
