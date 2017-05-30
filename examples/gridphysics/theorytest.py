level="""
22222222222222222222222222222222
2                              2
2                              2
2                              2
2                              2
2                              2
2                              2
2      4      3               02
222          5                 2
22222222222222222222222222222222
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > Resource color=DARKGRAY
		c2 > ResourcePack color=PINK
		c5 > Chaser color=LIGHTGREEN speed=1 fleeing=False
		c4 > ResourcePack color=YELLOW
	InteractionSet
		c2 avatar > killSprite
		c2 c5 > killSprite
		c5 c2 > killSprite
		c4 EOS > stepBack
		c2 c4 > killSprite
		c4 c2 > killSprite
		c4 c5 > killSprite
		c5 EOS > stepBack
		c2 c3 > killSprite
		c3 c2 > killSprite
		c2 c2 > killSprite
		avatar c5 > nothing
		c3 c3 > killSprite
		c4 c3 > stepBack
		c5 c5 > killSprite
		c2 EOS > stepBack
		c4 avatar > bounceForward
		c3 EOS > stepBack
		c3 c5 > killSprite
		c5 c3 > killSprite
		c4 c4 > killSprite
		avatar c3 > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=False
	LevelMapping
		0 > c2
		2 > c3
		3 > c4
		4 > c5
		5 > avatar
		8 > avatar c5
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
