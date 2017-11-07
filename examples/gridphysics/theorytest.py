level="""
22222222
2     32
2      2
2      2
21  2222
22     2
2      2
2  0   2
22222222
"""
game = """
BasicGame
	SpriteSet
		c3 > Resource color=BLACK
		c2 > Resource color=GREEN
		avatar > MovingAvatar color=WHITE
		c4 > ResourcePack color=GOLD
	InteractionSet
		c2 avatar > killSprite
		c4 EOS > stepBack
		c2 c4 > killSprite
		c4 c2 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c2 c2 > killSprite
		c3 c3 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
		c2 EOS > stepBack
		c4 avatar > killSprite
		c3 EOS > stepBack
		c4 c4 > killSprite
		c3 avatar > killSprite
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		2 > c3
		1 > avatar
		0 > c2
		3 > c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
