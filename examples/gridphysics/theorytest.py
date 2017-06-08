level="""
4444444444444444444444
4    5   6    4  4 4 4
4  5 4 6      45  5 44
4 0  4     6  5   55 4
4444444444444444444 44
4   42 6  4 4    4  44
4444 5    4 5 4  4   4
4    344 2    4  44 44
4  4  4 4 4   4     44
4444444444444444444444
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=LIGHTBLUE
		c2 > Resource color=PINK
		c7 > Resource color=ORANGE
		c6 > ResourcePack color=GREEN
		c5 > Resource color=DARKGRAY
		c4 > Resource color=GOLD
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c7 c6 > killSprite
		c2 c4 > killSprite
		c4 c2 > killSprite
		c5 EOS > stepBack
		c6 avatar > bounceForward
		c4 c5 > stepBack
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
		c4 c6 > bounceForward
		c3 c7 > killSprite
		c7 c3 > killSprite
		c2 c2 > killSprite
		c6 c5 > stepBack
		c7 EOS > stepBack
		c3 c3 > killSprite
		c3 EOS > stepBack
		c2 c7 > killSprite
		c7 c2 > killSprite
		c4 c7 > killSprite
		c7 c4 > killSprite
		c6 c3 > nothing
		c6 c6 > stepBack
		c2 c3 > killSprite
		c3 c2 > killSprite
		c7 c7 > killSprite
		c6 EOS > stepBack
		avatar c5 > stepBack
		avatar c4 > killSprite
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
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c2 limit=0 win=True
		SpriteCounter stype=c7 limit=0 win=True
	LevelMapping
		0 > c2
		1 > c3
		2 > c4
		3 > avatar
		4 > c5
		7 > c6 c3
		5 > c6
		6 > c7
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
