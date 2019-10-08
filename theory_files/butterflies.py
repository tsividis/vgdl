level="""
1111111111111111111111111111
1  0        1   2 2 2 212221
1 00      0 3          12221
1       2              12221
111111111111             221
12     0            1     11
12                         1
12         11111          21
11111              0 1     1
1        2 2 2 2 2   12   21
1111111111111111111111111111
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=DARKGRAY
		c2 > RandomNPC color=PINK speed=0.6 cooldown=1
		avatar > MovingAvatar color=DARKBLUE
		c4 > ResourcePack color=GREEN
	InteractionSet
		c2 avatar > killSprite
		c2 c4 > nothing
		c4 avatar > killSprite
		avatar EOS > stepBack
		avatar c3 > stepBack
		c3 c3 > nothing
		c4 c4 > nothing
		c3 c4 > nothing
		c4 EOS > stepBack
		c2 c3 > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c2
		1 > c3
		2 > c4
		3 > avatar
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
