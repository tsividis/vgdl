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
		avatar > MovingAvatar color=WHITE
		c2 > Missile color=DARKBLUE singleton=False cooldown=1 speed=1.0 orientation=UP
	InteractionSet
		avatar avatar > stepBack
		c3 c3 > killIfSlow limitspeed=1
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
		SpriteCounter stype=c2 limit=0 win=True
	LevelMapping
		2 > c3
		4 > c2
		8 > avatar
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
