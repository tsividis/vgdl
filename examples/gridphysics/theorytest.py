level="""
2222222222222222222222222222
2           2   1    A 2 0 2
2                      20  2
2                      200 2
222222222222         00    2
21                  2     22
21                         2
21         22222   0  000  2
22222       0        20 0  2
2                    2   0 2
2222222222222222222222222222
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=DARKGRAY
		c2 > ResourcePack color=BLUE
		avatar > MovingAvatar color=WHITE
		c4 > Missile color=RED speed=0.9 orientation=UP
	InteractionSet
		c2 avatar > killSprite
		c4 EOS > stepBack
		c2 c4 > killSprite
		c4 c2 > cloneSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c2 c2 > killSprite
		c3 c3 > killSprite
		avatar c3 > stepBack
		c2 EOS > stepBack
		c4 avatar > killSprite
		c3 EOS > stepBack
		c4 c4 > killSprite
		c4 c3 > stepBack
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c2 limit=0 win=False
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		SpriteCounter stype=c4 limit=0 win=True
	LevelMapping
		1 > c2
		2 > c3
		A > avatar
		0 > c4
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
