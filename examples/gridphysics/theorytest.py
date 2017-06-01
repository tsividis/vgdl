level="""
44444444444444444444444444444444
4                6  56         4
4                66 66         4
4                              4
4                              4
4                 8            4
4                             74
4      4       6             664
444    4                     674
44444444444444444444444444444444
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=WHITE
		c2 > Chaser color=ORANGE fleeing=False stype=c3
		c6 > Resource color=PURPLE
		c5 > Resource color=GREEN
		c4 > Resource color=BLACK
	InteractionSet
		avatar c2 > nothing
		c2 c4 > killSprite
		c4 c2 > killSprite
		c5 EOS > stepBack
		avatar c6 > nothing
		c5 c4 > killSprite
		c4 c5 > killSprite
		c3 c5 > stepBack
		c3 c4 > stepBack
		c2 c5 > stepBack
		c4 EOS > stepBack
		c3 avatar > bounceForward
		c2 c6 > stepBack
		c6 c4 > killSprite
		c4 c6 > killSprite
		c2 c2 > killSprite
		c6 c5 > killSprite
		c5 c6 > killSprite
		c3 c3 > killSprite
		c3 EOS > stepBack
		c6 c3 > killSprite
		c3 c6 > killSprite
		c3 c2 > killSprite
		c6 EOS > stepBack
		c5 avatar > killSprite
		avatar c4 > stepBack
		c2 EOS > stepBack
		c4 c4 > killSprite
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c5 s2=c4 win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		NoveltyTermination s1=c6 s2=c4 win=True
		NoveltyTermination s1=c6 s2=c5 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c3 limit=0 win=True
	LevelMapping
		8 > avatar c2
		1 > c6
		3 > avatar
		9 > avatar c6
		4 > c4
		5 > c2
		6 > c5
		7 > c3
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
