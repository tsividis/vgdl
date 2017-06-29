level="""
3333333333333333333333333333
3         6      7   13 1  3
30 345             3333    3
3       7 737              3
3333333333333333333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > Resource color=LIGHTBLUE
		c2 > Resource color=PINK
		c7 > Resource color=ORANGE
		c6 > Resource color=GREEN
		c5 > Resource color=YELLOW
		c4 > Resource color=DARKGRAY
	InteractionSet
		c3 c5 > stepBack
		c5 c3 > stepBack
		c7 c6 > killSprite
		c2 c4 > killSprite
		c4 c2 > killSprite
		c5 EOS > stepBack
		c6 avatar > bounceForward
		c5 c4 > stepBack
		c3 c4 > killSprite
		c4 c3 > killSprite
		c2 c5 > killSprite
		c5 c2 > killSprite
		c4 EOS > stepBack
		avatar c7 > killSprite
		c5 c7 > killSprite
		c7 c5 > killSprite
		c3 avatar > killSprite
		c2 c6 > killSprite
		c6 c2 > killSprite
		c6 c4 > stepBack
		c3 c7 > killSprite
		c7 c3 > killSprite
		c2 c2 > killSprite
		c5 c6 > killSprite
		c6 c5 > killSprite
		c7 EOS > stepBack
		c3 c3 > killSprite
		c3 EOS > stepBack
		c2 c7 > killSprite
		c7 c2 > killSprite
		c4 c7 > killSprite
		c7 c4 > killSprite
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c7 c7 > killSprite
		c6 EOS > stepBack
		c5 avatar > bounceForward
		avatar c4 > stepBack
		c5 c5 > killSprite
		c2 EOS > stepBack
		c2 avatar > killSprite
		c4 c4 > killSprite
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c2 s2=c6 win=True
		NoveltyTermination s1=c2 s2=c7 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c3 limit=0 win=True
		SpriteCounter stype=c7 limit=0 win=True
		SpriteCounter stype=c2 limit=0 win=True
	LevelMapping
		0 > c2
		1 > c3
		3 > c4
		4 > c5
		5 > avatar
		6 > c6
		7 > c7
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
