level="""
1111111111111
1        1  1
1   2       1
1   0 2 1 311
111 12  11111
1       1 3 1
1 2        11
1          11
1111111111111
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=GREEN
		c2 > ResourcePack color=DARKGRAY
		avatar > MovingAvatar color=DARKBLUE
		c4 > ResourcePack color=RED
	InteractionSet
		avatar c2 > stepBack
		c2 c4 > nothing
		c4 c2 > nothing
		c2 c2 > nothing
		avatar c4 > nothing
		avatar EOS > stepBack
		c3 c4 > killSprite
		c4 c4 > nothing
		c3 avatar > bounceForward
		c4 EOS > stepBack
		c3 c2 > stepBack
		c2 EOS > stepBack
		c3 c3 > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c3 limit=0 win=True
	LevelMapping
		0 > avatar
		1 > c2
		2 > c3
		3 > c4
		4 > avatar c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
