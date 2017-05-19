level="""
666666666666
6          6
6          6
6   0      6
6        9 6
6          6
6   0   8  6
6          6
6    9     6
666666666666
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=WHITE
		c3 > ResourcePack color=BLACK
		c2 > Resource color=BLUE
		c5 > ResourcePack color=YELLOW
		c4 > Resource color=RED
	InteractionSet
		c5 c3 > killSprite
		c3 c5 > killSprite
		c2 c5 > killSprite
		c5 c2 > undoAll
		c4 EOS > stepBack
		c2 c4 > killSprite
		c4 c2 > killSprite
		c5 EOS > stepBack
		c2 c3 > stepBack
		c2 c2 > stepBack
		c4 avatar > transformTo stype=c5
		avatar c5 > undoAll
		c3 c3 > killSprite
		avatar c3 > stepBack
		c2 EOS > stepBack
		c5 c4 > killSprite
		c4 c5 > killSprite
		c3 EOS > stepBack
		c2 avatar > bounceForward
		avatar c2 > stepBack
		c4 c4 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c5 s2=c3 win=True
		NoveltyTermination s1=c5 s2=c4 win=True
		SpriteCounter stype=c2 limit=0 win=True
	LevelMapping
		0 > c2
		b > avatar c5
		4 > c5
		6 > c3
		8 > avatar
		9 > c4
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
