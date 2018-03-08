level="""
22222222222222222222222222222222
2                              2
2                              2
2                              2
2              8               2
2                              2
2              4               2
2                              2
22222222222222222222222222222222
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=DARKGRAY
		c2 > ResourcePack color=DARKBLUE
		avatar > MovingAvatar color=WHITE
	InteractionSet
		c2 avatar > stepBack
		avatar c2 > stepBack
		avatar avatar > stepBack
		avatar EOS > stepBack
		c3 avatar > stepBack
		avatar c3 > stepBack
		c2 c3 > stepBack
		c3 c2 > stepBack
		c2 c2 > stepBack
		c3 c3 > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		2 > c3
		4 > c2
		8 > avatar
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
