level="""
222222222222222222
2                2
2                2
2                2
2                2
2                2
2           1    2
2                2
2             3  2
222222222222222222
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=BLACK
		c2 > ResourcePack color=ORANGE
		avatar > MovingAvatar color=DARKBLUE
		c4 > ResourcePack color=GOLD
	InteractionSet
		c2 avatar > killSprite
		c2 c4 > nothing
		c4 c2 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c2 c2 > nothing
		c3 c3 > nothing
		avatar EOS > stepBack
		c3 avatar > killSprite
		c4 avatar > killSprite
		c4 c4 > nothing
		c3 c4 > nothing
		c4 c3 > nothing
		c4 EOS > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=True
	LevelMapping
		0 > c2
		1 > avatar
		2 > c3
		3 > c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
