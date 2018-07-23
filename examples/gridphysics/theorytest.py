level="""
44444444444444444444444444444444
4                              4
4                              4
4                              4
4                              4
4                              4
4                             54
4      4                 3   664
444    4                 5   674
44444444444444444444444444444444
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=WHITE
		c2 > Chaser color=ORANGE fleeing=False cooldown=1 stype=c3
		c6 > ResourcePack color=PURPLE
		c5 > ResourcePack color=GREEN
		c4 > ResourcePack color=BLACK
	InteractionSet
		c5 c3 > nothing
		c3 c5 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		avatar c6 > nothing
		c5 c4 > nothing
		c4 c5 > nothing
		c3 avatar > bounceForward
		avatar EOS > stepBack
		c6 c4 > nothing
		c4 c6 > nothing
		c2 c2 > nothing
		c6 c5 > nothing
		c5 c6 > nothing
		c3 c3 > nothing
		c3 c6 > nothing
		c3 c2 > killSprite
		c5 avatar > killSprite
		avatar c4 > stepBack
		avatar c2 > nothing
		c4 c4 > nothing
		c5 EOS > stepBack
		c2 c5 > stepBack
		c4 EOS > stepBack
		c3 c4 > stepBack
		c2 c6 > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c2 EOS > stepBack
	TerminationSet
		MultiSpriteCounter stype0=c5 stype1=c6 limit=0 win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c5 s2=c3 win=True
		NoveltyTermination s1=c5 s2=c4 win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c6 s2=c4 win=True
		NoveltyTermination s1=c6 s2=c5 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c3 limit=0 win=True
	LevelMapping
		9 > avatar c2
		b > c3 c6
		1 > c6
		3 > avatar
		8 > avatar c6
		4 > c4
		5 > c2
		6 > c5
		7 > c3
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
