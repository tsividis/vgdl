level="""
22222222222222222222222222222222
2                              2
2                              2
2                              2
2              8               2
2                              2
2               4              2
2                              2
22222222222222222222222222222222
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=DARKGRAY
		c2 > ResourcePack color=WHITE
		avatar > OrientedAvatar color=DARKBLUE
	InteractionSet
		avatar avatar > stepBack
		c3 c3 > undoAll
		avatar EOS > stepBack
		c2 c2 > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		2 > c3
		4 > avatar
		8 > c2
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
