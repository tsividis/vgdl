level="""
333333333333333333
3 4 6   3        3
3   6   3    33333
36666      6     3
3     6 6       33
33   333         3
36666          6 3
3   66           3
3 1 2    6    6  3
333333333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > Resource color=WHITE
		c2 > Resource color=ORANGE
		c6 > Resource color=RED
		c5 > ResourcePack color=GOLD
		c4 > ResourcePack color=BLACK
		medicine > Resource color=RESOURCETOADD
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c2 avatar > killSprite
		c2 avatar > bounceForward
		c5 EOS > stepBack
		avatar c6 > killIfHasLess resource=medicine limit=-1
		c6 avatar > killSprite
		avatar c6 > changeResource resource=medicine value=-1
		c4 c5 > killSprite
		c5 c4 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
		c2 c5 > killSprite
		c5 c2 > killSprite
		c4 EOS > stepBack
		c2 c4 > undoAll
		c3 avatar > killSprite
		avatar c3 > changeResource resource=medicine value=1
		c2 c6 > killSprite
		c6 c2 > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c2 c2 > killSprite
		c5 c6 > killSprite
		c6 c5 > killSprite
		avatar c4 > stepBack
		c3 EOS > stepBack
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c6 EOS > stepBack
		c5 avatar > killSprite
		c5 avatar > killIfHasMore resource=medicine limit=1
		c3 c3 > killSprite
		c5 c5 > killSprite
		c2 EOS > stepBack
		c4 c4 > killSprite
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c2 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c5 s2=avatar win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c6 limit=0 win=False
	LevelMapping
		1 > c5
		2 > avatar
		3 > c4
		4 > c2
		5 > c3
		6 > c6
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
