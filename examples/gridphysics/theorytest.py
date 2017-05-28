level="""
44444444444444444444444444444444
4                              4
4                              4
4                              4
4  6                           4
4 0                            4
4                              4
4       5                     74
444                            4
44444444444444444444444444444444
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=DARKGRAY
		c2 > Resource color=BLUE
		c5 > Resource color=ORANGE
		c4 > ResourcePack color=RED
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c5 c2 > killSprite
		c4 EOS > stepBack
		c2 c4 > killSprite
		c4 c2 > killSprite
		c5 EOS > stepBack
		c2 c3 > killSprite
		c3 c2 > killSprite
		c2 c2 > killSprite
		c4 avatar > killSprite
		c5 avatar > bounceForward
		c3 c3 > killSprite
		avatar c3 > stepBack
		c5 c5 > killSprite
		c2 EOS > stepBack
		c5 c4 > stepBack
		c3 EOS > stepBack
		avatar c2 > nothing
		c4 c4 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c5 limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=True
	LevelMapping
		0 > c2
		4 > c3
		8 > avatar c2
		5 > avatar
		6 > c5
		7 > c4
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
