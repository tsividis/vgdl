level="""
33333333333333
3    777   4 3
3        A6  3
3    7       3
3    777     3
33333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > Resource color=ORANGE
		c2 > Resource color=BLUE
		c5 > ResourcePack color=RED
		c4 > ResourcePack color=BLACK
	InteractionSet
		avatar c2 > nothing
		c5 c2 > killSprite
		c4 EOS > stepBack
		c2 c4 > killSprite
		c4 c2 > killSprite
		c5 c4 > stepBack
		c5 EOS > stepBack
		c2 c3 > killSprite
		c3 c2 > killSprite
		c2 c2 > killSprite
		c5 avatar > bounceForward
		c3 c3 > killSprite
		c3 avatar > killSprite
		c5 c5 > killSprite
		c2 EOS > stepBack
		avatar c4 > stepBack
		c3 EOS > stepBack
		c5 c3 > stepBack
		c4 c4 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		SpriteCounter stype=c5 limit=0 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		4 > c2
		A > avatar
		3 > c4
		7 > c3
		6 > c5
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
