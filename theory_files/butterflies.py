level="""
1111111111111111111111111111
1           1   2 2 2 212221
100        3           12221
1     0 2              12221
111111111111             221
12     0            1     11
12                         1
12         11111    0     21
11111                1     1
1        2 2 2 2 2   12   21
1111111111111111111111111111
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=DARKGRAY
		c2 > RandomNPC color=PINK speed=0.6 cooldown=1
		avatar > MovingAvatar color=DARKBLUE
		c4 > RandomNPC color=GREEN speed=0.8 cooldown=10
	InteractionSet
		c2 avatar > changeScore value=2
		c2 avatar > killSprite
		c2 c4 > nothing
		c2 c2 > nothing
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
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c2 limit=0 win=True
	LevelMapping
		0 > c2
		1 > c3
		2 > c4
		3 > avatar
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
