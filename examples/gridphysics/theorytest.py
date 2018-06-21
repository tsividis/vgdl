level="""
44444444444444444444444444444444
4                              4
4                              4
4                              4
4      53                      4
4                             74
4                              4
4                              4
444                            4
44444444444444444444444444444444
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=WHITE
		c2 > ResourcePack color=ORANGE
		avatar > MovingAvatar color=DARKBLUE
		c4 > ResourcePack color=BLACK
	InteractionSet
		avatar c2 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c3 c2 > killSprite
		c2 c2 > nothing
		avatar c4 > stepBack
		avatar EOS > stepBack
		c3 c3 > bounceForward
		c4 c4 > nothing
		c3 avatar > bounceForward
		c4 EOS > stepBack
		c3 c4 > stepBack
		c2 EOS > stepBack
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
		8 > avatar c2
		3 > avatar
		4 > c4
		5 > c2
		7 > c3
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
