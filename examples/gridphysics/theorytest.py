level="""
111111111111111111111111
1111    13  11      3111
13 3  1 1       11    11
1         11    111    1
1 1111 11111    11   111
1        1            11
11   13   0211   111   1
11    11   1111    1   1
111              1    31
1111113     111111    11
111111111111111111111111
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=DARKGRAY
		c2 > Chaser color=BLUE speed=1 fleeing=True
		avatar > MovingAvatar color=WHITE
		c4 > Chaser color=ORANGE speed=1 fleeing=False
	InteractionSet
		c2 avatar > killSprite
		c4 EOS > stepBack
		c2 c4 > killSprite
		c4 c2 > killSprite
		c2 c3 > stepBack
		c2 c2 > killSprite
		c3 c3 > killSprite
		avatar c3 > stepBack
		c2 EOS > stepBack
		avatar c4 > killSprite
		c3 EOS > stepBack
		c4 c4 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c4
		1 > c3
		2 > avatar
		3 > c2
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
