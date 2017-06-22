level="""
11111111111
1  4 3  2 1
11111111111
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=DARKGRAY
		c2 > Resource color=PINK
		avatar > MovingAvatar color=DARKBLUE
		c4 > ResourcePack color=GREEN
		glucose > Resource color=RESOURCETOADD
	InteractionSet
		c2 avatar > killIfOtherHasMore resource=glucose limit=2
		c2 avatar > nothing
		c4 EOS > stepBack
		c2 c4 > killSprite
		c4 c2 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c2 c2 > killSprite
		c3 c3 > killSprite
		avatar c3 > stepBack
		c2 EOS > stepBack
		c4 avatar > killSprite
		c4 avatar > killIfOtherHasMore resource=glucose limit=2
		avatar c4 > changeResource limit=2 resource=glucose value=1
		c3 EOS > stepBack
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
		NoveltyTermination s1=c4 s2=avatar win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c2 limit=0 win=True
	LevelMapping
		3 > c2
		4 > avatar
		1 > c3
		5 > avatar c2
		2 > c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
