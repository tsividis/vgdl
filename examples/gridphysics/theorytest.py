level="""
222222222222222222
2                2
2     4          2
2                2
2                2
2                2
2  0             2
2                2
2             3  2
222222222222222222
"""
game = """
BasicGame
	SpriteSet
		c3 > ogy.ResourcePack color=BLACK
		c2 > Resource color=ORANGE
		avatar > ogy.MovingAvatar color=DARKBLUE
		c4 > Resource color=GOLD
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
		0 > c2
		1 > avatar
		4 > avatar avatar
		2 > c3
		3 > c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
