level="""
0000000000000000
0              0
0              0
0           A  0
0              0
0      0       0
0              0
0              0
0              0
0000000000000000
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=BLACK
		c2 > Resource color=GREEN
		avatar > MovingAvatar color=WHITE
	InteractionSet
		c2 avatar > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c2 c2 > killSprite
		c3 c3 > killSprite
		c2 EOS > stepBack
		c3 EOS > stepBack
		avatar c3 > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c2 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		SpriteCounter stype=c2 limit=0 win=True
		SpriteCounter stype=c2 limit=0 win=True
	LevelMapping
		2 > c2
		0 > c3
		A > avatar
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
