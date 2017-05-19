level="""
55555555555555
5      6 1   5
5  286       5
5    6       5
5    66      5
55555555555555
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > Chaser color=BLUE speed=0.4 fleeing=False
		c2 > Resource color=ORANGE
		c5 > ResourcePack color=RED
		c4 > ResourcePack color=BLACK
	InteractionSet
		c2 avatar > killSprite
		c2 c5 > killSprite
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
		avatar c3 > nothing
		c5 c5 > killSprite
		c2 EOS > stepBack
		avatar c4 > stepBack
		c3 EOS > stepBack
		c5 c3 > killSprite
		c4 c4 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		SpriteCounter stype=c5 limit=0 win=True
	LevelMapping
		1 > c3
		2 > avatar
		9 > avatar c3
		5 > c4
		6 > c2
		8 > c5
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
