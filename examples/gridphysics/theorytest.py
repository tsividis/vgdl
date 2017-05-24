level="""
333333333333333333
3 4 6   3    2   3
3   6   3    33333
36666      6     3
3     6 6       33
33   333         3
36666          6 3
3   66           3
3 1 6    6    6  3
333333333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > Resource color=WHITE
		c2 > ResourcePack color=ORANGE
		c6 > ResourcePack color=RED
		c5 > ResourcePack color=GOLD
		c4 > ResourcePack color=BLACK
		medicine > Resource color=RESOURCETOADD
	InteractionSet
		c2 avatar > killIfHasLess resource=medicine limit=0
		c2 avatar > killIfHasMore resource=medicine limit=1
		c2 c4 > killSprite
		c4 c2 > killSprite
		c5 EOS > stepBack
		avatar c6 > killIfHasLess resource=medicine limit=0
		c6 avatar > killIfHasLess resource=medicine limit=0
		c6 avatar > killIfHasMore resource=medicine limit=1
		avatar c6 > changeResource limit=0 resource=medicine
		c4 c5 > killSprite
		c5 c4 > killSprite
		c3 c5 > killSprite
		c5 c3 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
		c2 c5 > killSprite
		c5 c2 > killSprite
		c4 EOS > stepBack
		c3 avatar > killIfHasLess resource=medicine limit=0
		c3 avatar > killIfHasMore resource=medicine limit=1
		avatar c3 > changeResource limit=0 resource=medicine
		c2 c6 > killSprite
		c6 c2 > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c2 c2 > killSprite
		c5 c6 > killSprite
		c6 c5 > killSprite
		c3 c3 > killSprite
		c3 EOS > stepBack
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c6 EOS > stepBack
		c5 avatar > killIfHasLess resource=medicine limit=0
		c5 avatar > killIfHasMore resource=medicine limit=1
		c4 avatar > killIfHasMore resource=medicine limit=1
		avatar c4 > stepBack limit=0 resource=medicine
		c5 c5 > killSprite
		c2 EOS > stepBack
		c4 c4 > killSprite
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c6 limit=0 win=False
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
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
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c6 s2=avatar win=True
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
